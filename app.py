
import customtkinter as ctk
import tkinter as tk # For some specific mixed usage if needed, mostly pure CTk
from tkinter import filedialog, messagebox
import os
import sys
import threading

# Add services
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from services import utils
from services.journal import Journal
from services import pdf_extractor
from services import text_preprocessor
from services import chunker
from services import output_manager
from services import tts_engine
from services import wav_merger
from services import mp3_converter
from services import audio_mixer
from services.config_manager import ConfigManager

# --- Configuration & Theme ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class AntigravityApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Open Source PDF To Speech - Studio")
        self.geometry("900x750")
        self.minsize(800, 600)
        
        # State
        self.config = ConfigManager()
        self.journal = Journal()
        self.current_pdf_path = None
        self.extracted_text = None
        self.output_chunks_dir = None
        self.final_mp3_path = None
        
        # Audio Mixer State
        self.bgm_path = None
        self.voice_vol = 1.0
        self.bgm_vol = 0.2
        
        self.is_running = False # Flag for cancellation
        
        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar (Left) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Open Source\nPDF To Speech", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.label_version = ctk.CTkLabel(self.sidebar_frame, text="v1.1", font=ctk.CTkFont(size=12))
        self.label_version.grid(row=1, column=0, padx=20, pady=10)
        
       
        # --- GitHub Link ---
        def open_github():
            import webbrowser
            webbrowser.open("https://github.com/GeovanniVera/ttspython")

        self.github_link = ctk.CTkLabel(
            self.sidebar_frame, 
            text="GitHub Repository", 
            font=ctk.CTkFont(size=12, underline=True),
            text_color="#1f538d", # Color azul profesional
            cursor="hand2"        # Cambia el cursor al pasar el mouse
        )
        self.github_link.grid(row=6, column=0, padx=20, pady=10)
        
        # --- Audio Mixer Controls ---
        self.lbl_mixer = ctk.CTkLabel(self.sidebar_frame, text="Mezcla de Audio", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_mixer.grid(row=2, column=0, padx=20, pady=(10, 5))
        
        self.btn_bgm = ctk.CTkButton(self.sidebar_frame, text="Cargar Música (Opcional)", command=self.load_bgm, height=30, fg_color="#5D4037", hover_color="#4E342E")
        self.btn_bgm.grid(row=3, column=0, padx=20, pady=5)

        self.lbl_bgm_info = ctk.CTkLabel(self.sidebar_frame, text="Sin música", text_color="gray", font=ctk.CTkFont(size=10))
        self.lbl_bgm_info.grid(row=4, column=0, padx=20, pady=(0, 10))

        # Sliders
        self.lbl_v_vol = ctk.CTkLabel(self.sidebar_frame, text=f"Vol. Voz: {int(self.voice_vol*100)}%", font=ctk.CTkFont(size=11))
        self.lbl_v_vol.grid(row=5, column=0, padx=20, sticky="w")
        
        self.slider_v_vol = ctk.CTkSlider(self.sidebar_frame, from_=0.0, to=2.0, number_of_steps=20, command=self.update_vol_labels)
        self.slider_v_vol.set(self.voice_vol)
        self.slider_v_vol.grid(row=6, column=0, padx=20, pady=(0, 5))
        
        self.lbl_b_vol = ctk.CTkLabel(self.sidebar_frame, text=f"Vol. Música: {int(self.bgm_vol*100)}%", font=ctk.CTkFont(size=11))
        self.lbl_b_vol.grid(row=7, column=0, padx=20, sticky="w")
        
        self.slider_b_vol = ctk.CTkSlider(self.sidebar_frame, from_=0.0, to=1.0, number_of_steps=10, command=self.update_vol_labels)
        self.slider_b_vol.set(self.bgm_vol)
        self.slider_b_vol.grid(row=8, column=0, padx=20, pady=(0, 15))

        # Adjust grid rows
        # Logo: 0, Version: 1, Mixer: 2, Btn: 3, Info: 4, VLab: 5, VSlid: 6, BLab: 7, BSlid: 8
        # GitHub: 9
        self.github_link.grid(row=9, column=0, padx=20, pady=20)
        
        # Vincular el clic al navegador
        self.github_link.bind("<Button-1>", lambda e: open_github())

        # --- Main Area (Right) ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 1. File Input Section
        self.frame_file = ctk.CTkFrame(self.main_frame)
        self.frame_file.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.frame_file.grid_columnconfigure(1, weight=1)

        self.btn_load = ctk.CTkButton(self.frame_file, text="Cargar PDF", command=self.load_pdf, height=40, font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_load.grid(row=0, column=0, padx=15, pady=15)

        self.lbl_file_info = ctk.CTkLabel(self.frame_file, text="Ningún archivo seleccionado", text_color="gray")
        self.lbl_file_info.grid(row=0, column=1, padx=15, pady=15, sticky="w")
        
        self.lbl_stats = ctk.CTkLabel(self.frame_file, text="Páginas: - | Palabras: -", text_color="gray")
        self.lbl_stats.grid(row=0, column=2, padx=15, pady=15, sticky="e")

        # 2. Voice & Tone Settings
        self.frame_settings = ctk.CTkFrame(self.main_frame)
        self.frame_settings.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.frame_settings.grid_columnconfigure((0, 1, 2), weight=1)

        # Load Saved Settings
        saved_voice = self.config.get("voice", "Jorge (México)")
        saved_rate = self.config.get("rate", 0.0)
        saved_pitch = self.config.get("pitch", 0.0)

        # Voice Selector
        self.lbl_voice = ctk.CTkLabel(self.frame_settings, text="Voz Neural", font=ctk.CTkFont(weight="bold"))
        self.lbl_voice.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.voice_var = ctk.StringVar(value=saved_voice)
        self.opt_voice = ctk.CTkOptionMenu(self.frame_settings, values=["Jorge (México)", "Lorenzo (Chile)", "Dalia (México)", "Alvaro (España)"], variable=self.voice_var, command=self.save_settings)
        self.opt_voice.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")

        # Rate Slider
        self.lbl_rate = ctk.CTkLabel(self.frame_settings, text=f"Velocidad: {int(saved_rate)}%", font=ctk.CTkFont(weight="bold"))
        self.lbl_rate.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")
        
        self.slider_rate = ctk.CTkSlider(self.frame_settings, from_=-50, to=50, number_of_steps=20, command=self.update_rate_label)
        self.slider_rate.set(saved_rate)
        self.slider_rate.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="ew")

        # Pitch Slider
        self.lbl_pitch = ctk.CTkLabel(self.frame_settings, text=f"Tono: {int(saved_pitch)}Hz", font=ctk.CTkFont(weight="bold"))
        self.lbl_pitch.grid(row=0, column=2, padx=15, pady=(15, 5), sticky="w")
        
        self.slider_pitch = ctk.CTkSlider(self.frame_settings, from_=-20, to=20, number_of_steps=40, command=self.update_pitch_label)
        self.slider_pitch.set(saved_pitch)
        self.slider_pitch.grid(row=1, column=2, padx=15, pady=(0, 15), sticky="ew")

        # 3. Action Area
        self.frame_actions = ctk.CTkFrame(self.main_frame)
        self.frame_actions.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.frame_actions.grid_columnconfigure(0, weight=1)

        self.btn_process = ctk.CTkButton(self.frame_actions, text="Procesar y Generar Audio", command=self.start_pipeline, height=50, font=ctk.CTkFont(size=16, weight="bold"), fg_color="#1E88E5", hover_color="#1565C0")
        self.btn_process.grid(row=0, column=0, padx=15, pady=15, sticky="ew")

        self.btn_cancel = ctk.CTkButton(self.frame_actions, text="Cancelar", command=self.stop_process, height=50, fg_color="#D32F2F", hover_color="#C62828", state="disabled")
        self.btn_cancel.grid(row=0, column=1, padx=(0,15), pady=15, sticky="ew")
        self.frame_actions.grid_columnconfigure(1, weight=0) # Cancel button smaller if desired, or equal
        
        self.progress_bar = ctk.CTkProgressBar(self.frame_actions)
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="ew")
        self.progress_bar.set(0)
        
        self.lbl_progress = ctk.CTkLabel(self.frame_actions, text="Listo", text_color="gray")
        self.lbl_progress.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 15))

        # 4. Final Actions (Merge/Open)
        self.frame_final = ctk.CTkFrame(self.main_frame)
        self.frame_final.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        self.frame_final.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_open_folder = ctk.CTkButton(self.frame_final, text="Abrir Carpeta", command=self.open_output_folder, state="disabled", fg_color="transparent", border_width=1)
        self.btn_open_folder.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        self.btn_merge = ctk.CTkButton(self.frame_final, text="Unir Todo (MP3 Final)", command=self.start_merge_thread, state="disabled", fg_color="#43A047", hover_color="#2E7D32")
        self.btn_merge.grid(row=0, column=1, padx=15, pady=15, sticky="ew")

        self.btn_play = ctk.CTkButton(self.frame_final, text="Reproducir 🎵", command=self.play_audio, state="disabled", fg_color="#F57F17", hover_color="#F9A825")
        self.btn_play.grid(row=0, column=2, padx=15, pady=15, sticky="ew")

        # 5. Console/Log
        self.textbox_log = ctk.CTkTextbox(self.main_frame, height=150)
        self.textbox_log.grid(row=4, column=0, sticky="nsew")
        self.textbox_log.configure(state="disabled") # Initial state
        
        # Link Journal with Thread-Safe Callback
        self.journal.set_callback(self.thread_safe_log)
        self.journal.info("Aplicación iniciada. Motor: Edge TTS.")

    def thread_safe_log(self, message):
        """Appends log message safely from any thread."""
        self.after(0, lambda: self._append_to_log(message))

    def _append_to_log(self, message):
        try:
            self.textbox_log.configure(state="normal")
            self.textbox_log.insert("end", message)
            self.textbox_log.see("end")
            self.textbox_log.configure(state="disabled")
        except:
            pass

    # --- UX & Settings ---
    def save_settings(self, _=None):
        self.config.set("voice", self.voice_var.get())
        self.config.set("rate", self.slider_rate.get())
        self.config.set("pitch", self.slider_pitch.get())

    def update_rate_label(self, value):
        self.lbl_rate.configure(text=f"Velocidad: {int(value)}%")
        self.save_settings() # Auto-save on slide end
    
    def update_pitch_label(self, value):
        self.lbl_pitch.configure(text=f"Tono: {int(value)}Hz")
        self.save_settings()

    def get_voice_id(self):
        map = {
            "Jorge (México)": "es-MX-JorgeNeural",
            "Lorenzo (Chile)": "es-CL-LorenzoNeural",
            "Dalia (México)": "es-MX-DaliaNeural",
            "Alvaro (España)": "es-ES-AlvaroNeural"
        }
        return map.get(self.voice_var.get(), "es-MX-JorgeNeural")

    def get_rate_str(self):
        val = int(self.slider_rate.get())
        prefix = "+" if val >= 0 else ""
        return f"{prefix}{val}%"
        
    def get_pitch_str(self):
        val = int(self.slider_pitch.get())
        prefix = "+" if val >= 0 else ""
        return f"{prefix}{val}Hz"

    # --- Loop Control ---
    def stop_process(self):
        if self.is_running:
             self.is_running = False
             self.journal.warning("Cancelando proceso...")
             self.btn_cancel.configure(state="disabled")

    def load_bgm(self):
        filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav")])
        if filepath:
            self.bgm_path = filepath
            self.lbl_bgm_info.configure(text=os.path.basename(filepath)[:20]+"...")
            self.journal.info(f"Música de fondo cargada: {filepath}")
        else:
            self.bgm_path = None
            self.lbl_bgm_info.configure(text="Sin música")

    def update_vol_labels(self, _=None):
        self.voice_vol = self.slider_v_vol.get()
        self.bgm_vol = self.slider_b_vol.get()
        self.lbl_v_vol.configure(text=f"Vol. Voz: {int(self.voice_vol*100)}%")
        self.lbl_b_vol.configure(text=f"Vol. Música: {int(self.bgm_vol*100)}%")


    # --- Logic ---
    def load_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf")])
        if not filepath: return

        self.current_pdf_path = filepath
        self.extracted_text = None
        self.output_chunks_dir = None
        self.final_mp3_path = None
        
        self.lbl_file_info.configure(text=os.path.basename(filepath), text_color="#E0E0E0")
        self.journal.info(f"PDF Cargado: {filepath}")
        
        # Reset
        self.btn_process.configure(state="normal")
        self.btn_merge.configure(state="disabled")
        self.btn_open_folder.configure(state="disabled")
        self.btn_play.configure(state="disabled")

    def start_pipeline(self):
        if not self.current_pdf_path: return
        self.is_running = True
        self.btn_process.configure(state="disabled")
        self.btn_cancel.configure(state="normal") # Enable Cancel
        self.progress_bar.set(0)
        self.lbl_progress.configure(text="Procesando texto...")
        
        threading.Thread(target=self.run_process, daemon=True).start()

    def run_process(self):
        try:
            # 1. Extract
            if not self.is_running: return # Check cancel
            self.journal.info("Extrayendo texto...")
            raw_text, metadata = pdf_extractor.extract_text(self.current_pdf_path)
            
            clean_text = text_preprocessor.preprocess(raw_text)
            self.extracted_text = clean_text
            
            # Update info (UI needs after)
            word_count = len(clean_text.split())
            self.after(0, lambda: self.lbl_stats.configure(text=f"Páginas: {metadata['num_pages']} | Palabras: {word_count}"))
            
            # 2. TTS
            if not self.is_running: return 
            self.after(0, lambda: self.lbl_progress.configure(text="Generando audio..."))
            chunks = chunker.chunk_text(self.extracted_text)
            total = len(chunks)
            if total == 0: raise Exception("No text chunks found")

            self.output_chunks_dir = output_manager.prepare_output_structure(self.current_pdf_path)
            # Pass the thread-safe logger to the engine so traces appear in GUI
            engine = tts_engine.TTSEngine(log_callback=self.thread_safe_log)
            
            voice = self.get_voice_id()
            rate = self.get_rate_str()
            pitch = self.get_pitch_str()
            
            for i, chunk in enumerate(chunks):
                if not self.is_running: 
                    self.journal.warning("Proceso detenido por usuario.")
                    break

                idx = i+1
                filename = output_manager.get_chunk_filename(self.output_chunks_dir, os.path.basename(self.current_pdf_path).split('.')[0], idx, total)
                
                msg = f"Generando {idx}/{total}"
                self.journal.info(msg)
                
                engine.save_to_file(chunk, filename, voice=voice, rate=rate, pitch=pitch)
                
                # Update progress bar
                progress = idx / total
                self.after(0, lambda p=progress, m=msg: self.update_progress(p, m))
            
            success = self.is_running # If we broke loop because of cancel, success is False-ish in logic
            self.after(0, lambda: self.finish_tts(success))
            
        except Exception as e:
            self.journal.error(f"Error: {e}")
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self.finish_tts(False))
        finally:
            self.is_running = False
            self.after(0, lambda: self.btn_cancel.configure(state="disabled"))

    def update_progress(self, val, msg):
        self.progress_bar.set(val)
        self.lbl_progress.configure(text=msg)

    def finish_tts(self, success):
        self.btn_process.configure(state="normal")
        if success:
            self.lbl_progress.configure(text="Generación Completada", text_color="#66BB6A")
            self.btn_open_folder.configure(state="normal")
            self.btn_merge.configure(state="normal")
            # Auto-enable merge logic could go here if requested
        else:
             self.lbl_progress.configure(text="Proceso Interrumpido o Error", text_color="#EF5350")

    def open_output_folder(self):
        if self.output_chunks_dir and os.path.exists(self.output_chunks_dir):
            os.startfile(self.output_chunks_dir)

    def start_merge_thread(self):
        self.is_running = True
        self.btn_merge.configure(state="disabled")
        threading.Thread(target=self.run_merge, daemon=True).start()

    def run_merge(self):
        try:
            self.after(0, lambda: self.lbl_progress.configure(text="Uniendo archivos..."))
            base_name = output_manager.get_base_name(self.current_pdf_path)
            wav_files = [f for f in os.listdir(self.output_chunks_dir) if f.endswith('.wav')]
            count = len(wav_files)
            
            final_path = wav_merger.merge_wavs(self.output_chunks_dir, base_name, count)
            
            # --- Audio Mixing (Optional) ---
            if self.bgm_path and os.path.exists(self.bgm_path):
                self.journal.info("Mezclando con música de fondo...")
                mixed_path = final_path.replace("_final.wav", "_mixed.wav")
                try:
                    audio_mixer.mix_audio(
                        voice_path=final_path,
                        bgm_path=self.bgm_path,
                        output_path=mixed_path,
                        voice_vol=self.voice_vol,
                        bgm_vol=self.bgm_vol
                    )
                    final_path = mixed_path # Update flow to use mixed file
                    self.journal.info("Mezcla completada.")
                except Exception as e:
                    self.journal.error(f"Error en mezcla: {e}")
                    # Continue without mixing if fails? Or stop? 
                    # Let's fail safe: continue with original
                    self.journal.warning("Se usará el audio sin música.")
            
            # Convert to MP3
            self.journal.info("Convirtiendo a MP3...")
            self.final_mp3_path = mp3_converter.convert_wav_to_mp3(final_path)
            
            self.journal.info(f"Finalizado: {self.final_mp3_path}")
            
            self.after(0, lambda: self.finish_merge(True))
            
        except Exception as e:
             self.journal.error(f"Merge Error: {e}")
             self.after(0, lambda: self.finish_merge(False))
        finally:
             self.is_running = False

    def finish_merge(self, success):
         self.btn_merge.configure(state="normal")
         if success:
             messagebox.showinfo("Éxito", f"Audio creado:\n{self.final_mp3_path}")
             self.lbl_progress.configure(text="Proceso Finalizado")
             self.btn_play.configure(state="normal")

    def play_audio(self):
        if self.final_mp3_path and os.path.exists(self.final_mp3_path):
            self.journal.info("Reproduciendo audio...")
            os.startfile(self.final_mp3_path)

if __name__ == "__main__":
    app = AntigravityApp()
    app.mainloop()
