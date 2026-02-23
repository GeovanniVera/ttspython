import os
import concurrent.futures
import threading
import time
import shutil
from typing import Callable, Optional, List, Tuple
from src.domain.models.audio_project import AudioProject
from src.domain.models.voice_settings import VoiceSettings
from src.domain.ports.document_extractor import DocumentExtractorPort
from src.domain.ports.speech_generator import SpeechGeneratorPort
from src.domain.ports.audio_processor import AudioProcessorPort
from src.domain.services.text_service import TextService
from src.infrastructure.adapters.journal_adapter import JournalAdapter

class ProcessPdfToSpeechUseCase:
    def __init__(
        self,
        extractor: DocumentExtractorPort,
        generator: SpeechGeneratorPort,
        processor: AudioProcessorPort,
        text_service: TextService,
        journal: Optional[JournalAdapter] = None,
        max_workers: int = 4
    ):
        self.extractor = extractor
        self.generator = generator
        self.processor = processor
        self.text_service = text_service
        self.journal = journal
        self.max_workers = max_workers

    def _log(self, message, level="INFO"):
        if self.journal:
            self.journal.log(message, level)

    def extract_only(self, pdf_path: str) -> str:
        self._log(f"Extrayendo texto de: {os.path.basename(pdf_path)}")
        raw_text, _ = self.extractor.extract_text(pdf_path)
        if not raw_text:
            raise Exception("No se pudo extraer texto del PDF.")
        return self.text_service.preprocess(raw_text)

    def preview_voice(self, text: str, voice_settings: VoiceSettings) -> str:
        self._log("Generando previsualización de voz...")
        temp_preview = os.path.join(os.environ.get('TEMP', os.getcwd()), "preview_voice.mp3")
        preview_text = " ".join(text.split()[:30]) 
        self.generator.generate_speech(preview_text, temp_preview, voice_settings)
        return temp_preview

    def execute(
        self,
        text: str,
        pdf_path: str,
        output_base_dir: str,
        voice_settings: VoiceSettings,
        bgm_path: Optional[str] = None,
        bgm_volume: float = 0.2,
        progress_callback: Optional[Callable[[str, float], None]] = None,
        cancel_event: Optional[threading.Event] = None
    ) -> Optional[str]:
        base_name = os.path.basename(pdf_path).split('.')[0]
        project_dir = os.path.join(output_base_dir, base_name)
        os.makedirs(project_dir, exist_ok=True)
        
        self._log(f"Iniciando pipeline para: {base_name}")

        # Cleanup existing part files
        for f in os.listdir(project_dir):
            if f.startswith(base_name) and f.endswith(".mp3"):
                try: os.remove(os.path.join(project_dir, f))
                except: pass

        project = AudioProject(
            pdf_path=pdf_path, output_dir=project_dir,
            voice_settings=voice_settings, base_name=base_name,
            bgm_path=bgm_path, bgm_volume=bgm_volume
        )

        temp_merged_path = None

        def check_cancel():
            if cancel_event and cancel_event.is_set():
                self._log("Cancelación detectada.", "WARN")
                raise InterruptedError("Proceso cancelado.")

        try:
            check_cancel()
            
            project.extracted_text = text
            project.chunks = self.text_service.chunk_text(text)
            total_chunks = len(project.chunks)
            if total_chunks == 0: raise Exception("No hay texto.")

            self._log(f"Plan de audio: {total_chunks} fragmentos.")

            chunk_tasks = []
            for i, chunk in enumerate(project.chunks):
                idx = i + 1
                chunk_path = os.path.join(project_dir, f"{base_name}_part_{idx:03d}.mp3")
                chunk_tasks.append((idx, chunk, chunk_path))
                project.generated_files.append(chunk_path)

            completed_count = 0
            start_time = time.time()
            
            def process_chunk(chunk_data):
                idx, chunk_text, path = chunk_data
                check_cancel()
                self.generator.generate_speech(chunk_text, path, voice_settings)
                return idx

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(process_chunk, t): t[0] for t in chunk_tasks}
                for future in concurrent.futures.as_completed(futures):
                    check_cancel()
                    future.result()
                    completed_count += 1
                    
                    elapsed = time.time() - start_time
                    avg = elapsed / completed_count
                    eta = int(avg * (total_chunks - completed_count))
                    
                    if progress_callback:
                        progress = 0.15 + (0.6 * (completed_count / total_chunks))
                        msg = f"Generando: {completed_count}/{total_chunks} - ETA: {eta}s"
                        progress_callback(msg, progress)

            check_cancel()
            project.generated_files.sort()

            self._log("Uniendo fragmentos de audio...")
            if progress_callback: progress_callback("Finalizando mezcla...", 0.9)
            temp_merged_path = os.path.join(project_dir, f"{base_name}_temp_merged.mp3")
            self.processor.merge_wavs(project.generated_files, temp_merged_path)

            final_mp3_path = os.path.join(project_dir, f"{base_name}_mixed.mp3")
            self._log("Aplicando mezcla final...")
            self.processor.mix_with_bgm(
                temp_merged_path, 
                bgm_path if bgm_path and os.path.exists(bgm_path) else "", 
                final_mp3_path, 
                voice_settings.volume, 
                bgm_volume
            )

            self._log(f"¡Proceso completado! Archivo final: {final_mp3_path}")
            return final_mp3_path

        except InterruptedError: return None
        except Exception as e:
            self._log(f"Error en el pipeline: {str(e)}", "ERROR")
            raise e
        finally:
            self._log("Limpiando archivos temporales...")
            for f in project.generated_files:
                if os.path.exists(f): os.remove(f)
            if temp_merged_path and os.path.exists(temp_merged_path): os.remove(temp_merged_path)
