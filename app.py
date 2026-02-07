import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import sys
import threading

# Add the current directory to sys.path to ensure modules can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from services import utils
from services.journal import Journal
from services import pdf_extractor
from services import text_preprocessor
from services import chunker
from services import output_manager
from services import output_manager
from services import tts_engine
from services import wav_merger
from services import mp3_converter

class AntigravityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Antigravity - Text to Speech")
        self.root.geometry("700x650") # Increased height for new sections
        
        self.journal = Journal()
        self.current_pdf_path = None
        self.extracted_text = None
        self.output_chunks_dir = None
        
        self.create_widgets()
        self.check_environment()

    def create_widgets(self):
        # --- Stage 1: Input ---
        frame_input = tk.LabelFrame(self.root, text="1. Entrada", padx=10, pady=5)
        frame_input.pack(fill=tk.X, padx=10, pady=5)

        self.btn_load = tk.Button(frame_input, text="Cargar PDF", command=self.load_pdf, height=1)
        self.btn_load.pack(fill=tk.X)
        
        self.lbl_file = tk.Label(frame_input, text="Ningún archivo seleccionado", fg="grey")
        self.lbl_file.pack(fill=tk.X)

        # --- Stage 2: Preparation ---
        frame_prep = tk.LabelFrame(self.root, text="2. Preparación", padx=10, pady=5)
        frame_prep.pack(fill=tk.X, padx=10, pady=5)

        self.btn_process = tk.Button(frame_prep, text="Procesar Texto", command=self.start_processing_thread, height=1, state=tk.DISABLED)
        self.btn_process.pack(fill=tk.X)
        
        self.lbl_stats = tk.Label(frame_prep, text="Páginas: - | Palabras: -", fg="grey")
        self.lbl_stats.pack(fill=tk.X)

        # --- Stage 3: Synthesis ---
        frame_synth = tk.LabelFrame(self.root, text="3. Síntesis (TTS)", padx=10, pady=5)
        frame_synth.pack(fill=tk.X, padx=10, pady=5)

        self.btn_tts = tk.Button(frame_synth, text="Generar Audio (SAPI)", command=self.start_tts_thread, height=1, state=tk.DISABLED, bg="#e1f5fe")
        self.btn_tts.pack(fill=tk.X)
        
        self.lbl_progress = tk.Label(frame_synth, text="Progreso: -", fg="grey")
        self.lbl_progress.pack(fill=tk.X)

        # --- Stage 4: Output & Finalize ---
        frame_output = tk.LabelFrame(self.root, text="4. Salida", padx=10, pady=5)
        frame_output.pack(fill=tk.X, padx=10, pady=5)

        self.btn_open_folder = tk.Button(frame_output, text="Abrir Carpeta de Fragmentos", command=self.open_output_folder, state=tk.DISABLED)
        self.btn_open_folder.pack(fill=tk.X, pady=(0, 5))
        
        # Placeholders for future deliveries
        self.btn_merge = tk.Button(frame_output, text="Unir Audio (WAV Final)", command=self.start_merge_thread, state=tk.DISABLED)
        self.btn_merge.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_mp3 = tk.Button(frame_output, text="Convertir a MP3 (Final)", command=self.start_mp3_thread, state=tk.DISABLED)
        self.btn_mp3.pack(fill=tk.X)

        # --- Status & Logs ---
        self.lbl_status = tk.Label(self.root, text="Estado: Esperando PDF...", fg="grey", pady=5)
        self.lbl_status.pack(fill=tk.X)

        log_frame = tk.Frame(self.root, padx=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        lbl_log = tk.Label(log_frame, text="Bitácora de Eventos", anchor="w")
        lbl_log.pack(fill=tk.X)

        self.txt_log = scrolledtext.ScrolledText(log_frame, state=tk.DISABLED, height=8)
        self.txt_log.pack(fill=tk.BOTH, expand=True)

        self.journal.set_widget(self.txt_log)
        self.journal.info("Aplicación iniciada. UI optimizada cargada.")

    def check_environment(self):
        self.journal.info("Verificando entorno...")
        if not utils.check_ffmpeg():
            error_msg = "FFmpeg no detectado. Instale FFmpeg y agréguelo al PATH."
            self.journal.error(error_msg)
            messagebox.showerror("Error Crítico", error_msg)
            self.btn_load.config(state=tk.DISABLED)
            self.lbl_status.config(text="Error: FFmpeg no encontrado", fg="red")
        else:
            self.journal.info("FFmpeg detectado correctamente.")

    def load_pdf(self):
        filepath = filedialog.askopenfilename(
            title="Seleccionar archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )

        if not filepath:
            return

        self.journal.info(f"Intentando cargar: {filepath}")
        is_valid, message = utils.validate_pdf(filepath)

        if is_valid:
            self.current_pdf_path = filepath
            self.extracted_text = None 
            self.output_chunks_dir = None
            
            self.lbl_file.config(text=f"Archivo: {os.path.basename(filepath)}", fg="black")
            self.lbl_status.config(text="PDF Cargado. Listo para procesar.", fg="green")
            self.journal.info("PDF validado y cargado exitosamente.")
            
            # Reset workflow
            self.btn_process.config(state=tk.NORMAL)
            self.btn_tts.config(state=tk.DISABLED)
            self.btn_open_folder.config(state=tk.DISABLED)
            self.lbl_stats.config(text="Páginas: - | Palabras: -")
            self.lbl_progress.config(text="Progreso: -")
            
        else:
            self.lbl_status.config(text="Error al cargar PDF", fg="red")
            self.journal.error(f"Validación fallida: {message}")
            messagebox.showerror("Error de Validación", message)
            self.btn_process.config(state=tk.DISABLED)
            self.current_pdf_path = None

    def start_processing_thread(self):
        if not self.current_pdf_path:
            return
        self.toggle_inputs(False)
        self.lbl_status.config(text="Procesando PDF...", fg="blue")
        threading.Thread(target=self.process_pdf, daemon=True).start()

    def process_pdf(self):
        try:
            self.journal.info("Iniciando extracción de texto...")
            raw_text, metadata = pdf_extractor.extract_text(self.current_pdf_path)
            
            if not metadata['success']:
                raise Exception(metadata.get('error', 'Error desconocido'))
            if not raw_text or not raw_text.strip():
                raise Exception("PDF vacío o escaneado.")
                
            self.journal.info(f"[EXTRACT] Extracción ok. {metadata['num_pages']} págs.")
            
            clean_text = text_preprocessor.preprocess(raw_text)
            self.extracted_text = clean_text
            word_count = len(clean_text.split())
            
            self.journal.info(f"[PREPROCESS] Normalizado: {word_count} palabras.")
            
            self.root.after(0, lambda: self.finish_processing(True, metadata['num_pages'], word_count))
            
        except Exception as e:
            self.journal.error(f"Error Proc: {str(e)}")
            self.root.after(0, lambda: self.finish_processing(False))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def finish_processing(self, success, pages=0, words=0):
        self.toggle_inputs(True)
        if success:
            self.lbl_stats.config(text=f"Páginas: {pages} | Palabras: {words}")
            self.btn_tts.config(state=tk.NORMAL)
            self.lbl_status.config(text="Texto listo. Puede generar audio.", fg="green")
        else:
            self.lbl_status.config(text="Error en procesamiento.", fg="red")

    def start_tts_thread(self):
        if not self.extracted_text:
            return
        self.toggle_inputs(False)
        self.lbl_status.config(text="Generando Audios...", fg="blue")
        threading.Thread(target=self.generate_audio, daemon=True).start()

    def generate_audio(self):
        try:
            chunks = chunker.chunk_text(self.extracted_text)
            total_chunks = len(chunks)
            
            if total_chunks == 0:
                raise Exception("No hay bloques de texto.")

            self.output_chunks_dir = output_manager.prepare_output_structure(self.current_pdf_path)
            engine = tts_engine.TTSEngine()
            
            for i, chunk in enumerate(chunks):
                index = i + 1
                filename = output_manager.get_chunk_filename(self.output_chunks_dir, os.path.basename(self.current_pdf_path).split('.')[0], index, total_chunks)
                
                # Update progress
                msg = f"Generando bloque {index}/{total_chunks}..."
                self.journal.info(msg)
                self.root.after(0, lambda m=msg: self.lbl_progress.config(text=m))
                
                engine.save_to_file(chunk, filename)
                
            self.journal.info(f"[TTS] Completado. {total_chunks} archivos.")
            self.root.after(0, lambda: self.finish_tts(True))

        except Exception as e:
            self.journal.error(f"Error TTS: {str(e)}")
            self.root.after(0, lambda: self.finish_tts(False))
            self.root.after(0, lambda: messagebox.showerror("Error TTS", str(e)))

    def finish_tts(self, success):
        self.toggle_inputs(True)
        if success:
            self.lbl_progress.config(text="Generación Completada.")
            self.lbl_status.config(text="Audio generado exitosamente.", fg="green")
            self.btn_open_folder.config(state=tk.NORMAL)
            self.btn_merge.config(state=tk.NORMAL)
        else:
            self.lbl_status.config(text="Error en generación de audio.", fg="red")

    def start_merge_thread(self):
        if not self.output_chunks_dir:
            return
        self.toggle_inputs(False)
        self.lbl_status.config(text="Uniendo audios...", fg="blue")
        threading.Thread(target=self.merge_audio, daemon=True).start()

    def merge_audio(self):
        try:
            self.journal.info("Iniciando unión de audios...")
            base_name = output_manager.get_base_name(self.current_pdf_path)
            
            # Dynamically count actual .wav files in the directory to determine total_chunks
            wav_files = [f for f in os.listdir(self.output_chunks_dir) if f.endswith('.wav')]
            real_total_chunks = len(wav_files)
            
            if real_total_chunks == 0:
                 raise Exception("No se encontraron archivos WAV en la carpeta de fragmentos.")

            final_path = wav_merger.merge_wavs(self.output_chunks_dir, base_name, real_total_chunks)
            
            self.journal.info(f"[MERGE] Archivo final creado: {final_path}")
            self.root.after(0, lambda: self.finish_merge(True, final_path))

        except Exception as e:
            self.journal.error(f"Error Merge: {str(e)}")
            self.root.after(0, lambda: self.finish_merge(False))
            self.root.after(0, lambda: messagebox.showerror("Error Unión", str(e)))

    def finish_merge(self, success, path=None):
        self.toggle_inputs(True)
        if success:
            self.lbl_status.config(text="Unión completada.", fg="green")
            self.btn_mp3.config(state=tk.NORMAL)
            if path:
                 messagebox.showinfo("Éxito", f"Audio unido correctamente:\n{path}")
        else:
            self.lbl_status.config(text="Error en unión.", fg="red")

    def start_mp3_thread(self):
        # We need the final wav path. 
        # For simplicity, infer it or store it.
        # Let's infer from current_pdf_path
        if not self.current_pdf_path: return
        
        base_name = output_manager.get_base_name(self.current_pdf_path)
        final_dir = output_manager.get_final_output_dir(self.current_pdf_path)
        wav_path = os.path.join(final_dir, f"{base_name}_final.wav")
        
        if not os.path.exists(wav_path):
            messagebox.showerror("Error", "No se encuentra el archivo WAV final.")
            return

        self.toggle_inputs(False)
        self.lbl_status.config(text="Convirtiendo a MP3...", fg="blue")
        threading.Thread(target=self.convert_mp3, args=(wav_path,), daemon=True).start()

    def convert_mp3(self, wav_path):
        try:
            self.journal.info("Iniciando conversión a MP3...")
            mp3_path = mp3_converter.convert_wav_to_mp3(wav_path)
            self.journal.info(f"[MP3] Archivo creado: {mp3_path}")
            self.root.after(0, lambda: self.finish_mp3(True, mp3_path))
        except Exception as e:
            self.journal.error(f"Error MP3: {str(e)}")
            self.root.after(0, lambda: self.finish_mp3(False))
            self.root.after(0, lambda: messagebox.showerror("Error MP3", str(e)))

    def finish_mp3(self, success, path=None):
        self.toggle_inputs(True)
        if success:
            self.lbl_status.config(text="Conversión MP3 completada.", fg="green")
            if path:
                messagebox.showinfo("Conversión Exitosa", f"MP3 guardado en:\n{path}")
        else:
             self.lbl_status.config(text="Error en conversión MP3.", fg="red")

    def open_output_folder(self):
        if self.output_chunks_dir and os.path.exists(self.output_chunks_dir):
            try:
                os.startfile(self.output_chunks_dir)
            except Exception as e:
                self.journal.error(f"No se pudo abrir carpeta: {e}")

    def toggle_inputs(self, enable):
        state = tk.NORMAL if enable else tk.DISABLED
        self.btn_load.config(state=state)
        if enable:
            self.btn_process.config(state=tk.NORMAL if self.current_pdf_path else tk.DISABLED)
            self.btn_tts.config(state=tk.NORMAL if self.extracted_text else tk.DISABLED)
            self.btn_open_folder.config(state=tk.NORMAL if self.output_chunks_dir else tk.DISABLED)
            # Enable merge if chunks exist
            self.btn_merge.config(state=tk.NORMAL if self.output_chunks_dir else tk.DISABLED)
            # Enable mp3 if final wav exists (simplified check, maybe relax or check file)
             # For now, keep disabled until merge explicit success or check file existence
            self.btn_mp3.config(state=tk.NORMAL if self.output_chunks_dir else tk.DISABLED) # Simplified
        else:
            self.btn_process.config(state=tk.DISABLED)
            self.btn_tts.config(state=tk.DISABLED)
            self.btn_open_folder.config(state=tk.DISABLED)
            self.btn_merge.config(state=tk.DISABLED)
            self.btn_mp3.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = AntigravityApp(root)
    root.mainloop()
