import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import threading
import subprocess
import queue
from tkinterdnd2 import DND_FILES, TkinterDnD

# Use Absolute imports
from src.domain.models.voice_settings import VoiceSettings
from src.infrastructure.container import container # Dependency Injection

# --- Configuration ---
# Inherit from ctk.CTk for professional visuals and manually load DND
class AntigravityApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Manually initialize TkinterDnD on this CTK window
        try:
            self.TkdndVersion = TkinterDnD._require(self)
        except Exception as e:
            print(f"Warn: No se pudo cargar soporte para Arrastrar y Soltar: {e}")

        # --- Architecture Setup ---
        self.use_case = container.process_pdf_use_case
        self.config_repo = container.config_repo
        self.journal = container.journal_adapter
        
        # UI Refresh Queue (To prevent blocking main thread)
        self.log_queue = queue.Queue()
        self.update_interval = 100 # ms

        # Window Setup
        self.title("PDF To Speech Studio v4.1")
        self.geometry("1100x850")
        
        # Theme Setup
        self.appearance_mode = self.config_repo.get("appearance_mode", "Dark")
        ctk.set_appearance_mode(self.appearance_mode)
        
        # State
        self.current_pdf_path = None
        self.extracted_text = ""
        self.bgm_path = None
        self.final_mp3_path = None
        self.cancel_event = threading.Event()
        self.history = self.config_repo.get("history", [])

        # Icon Setup (After loading CTK to avoid conflicts)
        from src.infrastructure.env_manager import env_manager
        icon_path = env_manager.get_icon_path()
        if icon_path:
            try:
                self.after(200, lambda: self.iconbitmap(icon_path))
            except: pass

        self._build_ui()
        self.journal.set_callback(self.thread_safe_log)
        
        # Start periodic UI log checker
        self.after(self.update_interval, self._process_log_queue)
        self.journal.info("Studio Premium listo. Sistema responsivo activado.")

    def _process_log_queue(self):
        """Periodically flushes logs from the background threads to the UI."""
        try:
            while True: # Process all pending logs
                message = self.log_queue.get_nowait()
                self._append_to_log(message)
        except queue.Empty:
            pass
        finally:
            self.after(self.update_interval, self._process_log_queue)

    def thread_safe_log(self, message):
        """Enqueues a message for UI update instead of writing directly."""
        self.log_queue.put(message)

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar_frame, text="STUDIO PDF", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 10))
        
        # Theme Toggle
        self.theme_switch = ctk.CTkSwitch(self.sidebar_frame, text="MODO OSCURO", 
                                          command=self.toggle_theme,
                                          variable=tk.BooleanVar(value=self.appearance_mode == "Dark"))
        self.theme_switch.pack(pady=10)

        # History Section
        ctk.CTkLabel(self.sidebar_frame, text="◷ RECIENTES", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(20, 5))
        self.history_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.history_frame.pack(fill="x", padx=10)
        self._update_history_ui()

        # Mixer Card
        self.mixer_card = ctk.CTkFrame(self.sidebar_frame, fg_color="#2B2B2B" if self.appearance_mode == "Dark" else "#DBDBDB")
        self.mixer_card.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(self.mixer_card, text="⛭ MEZCLA DE AUDIO", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        
        self.lbl_v_vol = ctk.CTkLabel(self.mixer_card, text="VOZ: 100%", font=ctk.CTkFont(size=11))
        self.lbl_v_vol.pack(anchor="w", padx=15)
        self.slider_v_vol = ctk.CTkSlider(self.mixer_card, from_=0.0, to=2.0, command=self.update_v_vol_label)
        self.slider_v_vol.set(1.0)
        self.slider_v_vol.pack(fill="x", padx=15, pady=(0, 10))

        self.lbl_b_vol = ctk.CTkLabel(self.mixer_card, text="MÚSICA: 20%", font=ctk.CTkFont(size=11))
        self.lbl_b_vol.pack(anchor="w", padx=15)
        self.slider_b_vol = ctk.CTkSlider(self.mixer_card, from_=0.0, to=1.0, command=self.update_b_vol_label)
        self.slider_b_vol.set(0.2)
        self.slider_b_vol.pack(fill="x", padx=15, pady=(0, 20))

        self.btn_bgm = ctk.CTkButton(self.sidebar_frame, text="♫ CARGAR MÚSICA", command=self.load_bgm, fg_color="#37474F")
        self.btn_bgm.pack(fill="x", padx=20, pady=10)

        # Main Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # Toolbar
        self.toolbar = ctk.CTkFrame(self.main_frame, height=50)
        self.toolbar.pack(fill="x", pady=(0, 15))
        
        self.btn_load = ctk.CTkButton(self.toolbar, text="📄 CARGAR PDF", command=self.load_pdf, width=120)
        self.btn_load.pack(side="left", padx=10, pady=10)

        self.btn_dest = ctk.CTkButton(self.toolbar, text="⚲ DESTINO", command=self.select_destination, width=100, fg_color="#455A64")
        self.btn_dest.pack(side="left", padx=5, pady=10)
        
        self.lbl_file = ctk.CTkLabel(self.toolbar, text="Arrastre un archivo aquí...", text_color="gray")
        self.lbl_file.pack(side="left", padx=10)

        # Drag & Drop Area Setup (Using the CTK wrapper now correctly)
        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self.handle_drop)
        except: pass

        # EDITOR TOGGLE
        self.edit_mode_var = tk.BooleanVar(value=False)
        self.switch_edit = ctk.CTkSwitch(self.toolbar, text="EDICIÓN", variable=self.edit_mode_var, command=self.toggle_editor, state="disabled")
        self.switch_edit.pack(side="right", padx=20)

        self.editor_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.text_editor = ctk.CTkTextbox(self.editor_frame, font=ctk.CTkFont(size=14), height=300)
        self.text_editor.pack(fill="both", expand=True, pady=(0, 10))

        # Action Panel
        self.action_panel = ctk.CTkFrame(self.main_frame)
        self.action_panel.pack(fill="x", pady=(0, 10))
        
        vrow = ctk.CTkFrame(self.action_panel, fg_color="transparent")
        vrow.pack(fill="x", padx=20, pady=10)
        
        self.voice_var = ctk.StringVar(value=self.config_repo.get("voice", "es-MX-JorgeNeural"))
        self.opt_voice = ctk.CTkOptionMenu(vrow, values=["es-MX-JorgeNeural", "es-CL-LorenzoNeural", "es-MX-DaliaNeural", "es-ES-AlvaroNeural", "en-US-GuyNeural", "en-US-AvaNeural"], variable=self.voice_var)
        self.opt_voice.pack(side="left", padx=(0, 10))

        self.lbl_rate = ctk.CTkLabel(vrow, text=f"VELO: {int(self.config_repo.get('rate_val', 0))}%")
        self.lbl_rate.pack(side="left", padx=(10, 0))
        self.slider_rate = ctk.CTkSlider(vrow, from_=-50, to=50, width=100, command=self.update_rate_label)
        self.slider_rate.set(self.config_repo.get("rate_val", 0))
        self.slider_rate.pack(side="left", padx=5)

        self.lbl_pitch = ctk.CTkLabel(vrow, text=f"TONO: {int(self.config_repo.get('pitch_val', 0))}Hz")
        self.lbl_pitch.pack(side="left", padx=(10, 0))
        self.slider_pitch = ctk.CTkSlider(vrow, from_=-20, to=20, width=100, command=self.update_pitch_label)
        self.slider_pitch.set(self.config_repo.get("pitch_val", 0))
        self.slider_pitch.pack(side="left", padx=5)

        self.btn_preview = ctk.CTkButton(vrow, text="🔊 ESCUCHAR", command=self.preview_voice, fg_color="#F57F17", width=100)
        self.btn_preview.pack(side="right", padx=10)

        arow = ctk.CTkFrame(self.action_panel, fg_color="transparent")
        arow.pack(fill="x", padx=20, pady=(0, 15))
        
        self.btn_process = ctk.CTkButton(arow, text="▶ INICIAR PROCESO", command=self.start_pipeline, height=50, fg_color="#2E7D32", font=ctk.CTkFont(weight="bold"))
        self.btn_process.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_cancel = ctk.CTkButton(arow, text="⏹", command=self.stop_process, width=50, height=50, fg_color="#C62828", state="disabled")
        self.btn_cancel.pack(side="left")

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, height=12)
        self.progress_bar.pack(fill="x", pady=(5, 5))
        self.progress_bar.set(0)
        self.lbl_status = ctk.CTkLabel(self.main_frame, text="Listo", font=ctk.CTkFont(size=13))
        self.lbl_status.pack()

        # Log Console
        self.log_container = ctk.CTkFrame(self.main_frame, height=200)
        self.log_header = ctk.CTkFrame(self.log_container, height=30, fg_color="#333333")
        self.log_header.pack(fill="x")
        ctk.CTkLabel(self.log_header, text="☰ BITÁCORA", font=ctk.CTkFont(size=11, weight="bold")).pack(side="left", padx=10)
        ctk.CTkButton(self.log_header, text="✕", width=30, height=25, fg_color="transparent", hover_color="#C62828", command=self.hide_logs).pack(side="right", padx=5)

        self.textbox_log = ctk.CTkTextbox(self.log_container, height=170, font=ctk.CTkFont(family="Consolas", size=11))
        self.textbox_log.pack(fill="both", expand=True)
        self.textbox_log.configure(state="disabled")
        self.textbox_log.tag_config("INFO", foreground="#64B5F6")
        self.textbox_log.tag_config("ERROR", foreground="#E57373")
        self.textbox_log.tag_config("WARN", foreground="#FFF176")

        self.btn_show_logs = ctk.CTkButton(self, text="☰ VER BITÁCORA", width=120, height=30, fg_color="#455A64", command=self.show_logs)
        self.btn_show_logs.place(relx=0.5, rely=0.96, anchor="center")

    def _update_history_ui(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        for item in self.history[-5:]: # Show last 5
            name = os.path.basename(item)
            if len(name) > 25: name = name[:22] + "..."
            btn = ctk.CTkButton(self.history_frame, text=f"📄 {name}", 
                                anchor="w", fg_color="transparent", 
                                text_color="gray", height=25,
                                command=lambda p=item: self.load_pdf_from_path(p))
            btn.pack(fill="x")

    def toggle_theme(self):
        self.appearance_mode = "Light" if self.appearance_mode == "Dark" else "Dark"
        ctk.set_appearance_mode(self.appearance_mode)
        self.config_repo.set("appearance_mode", self.appearance_mode)
        self.mixer_card.configure(fg_color="#2B2B2B" if self.appearance_mode == "Dark" else "#DBDBDB")

    def handle_drop(self, event):
        path = event.data.strip('{}')
        if path.lower().endswith('.pdf'):
            self.load_pdf_from_path(path)
        else:
            messagebox.showwarning("Archivo no válido", "Por favor, arrastre solo archivos PDF.")

    def _set_busy(self, busy=True):
        """Disables or enables all interactive components to prevent race conditions."""
        state = "disabled" if busy else "normal"
        self.btn_load.configure(state=state)
        self.btn_dest.configure(state=state)
        self.btn_bgm.configure(state=state)
        self.btn_preview.configure(state=state)
        self.btn_process.configure(state=state)
        self.switch_edit.configure(state="disabled" if busy else ("normal" if self.current_pdf_path else "disabled"))
        self.theme_switch.configure(state=state)

    def load_pdf_from_path(self, path):
        if os.path.exists(path):
            self._set_busy(True)
            self.current_pdf_path = path
            self.lbl_file.configure(text=f"📂 {os.path.basename(path)}", text_color="#1E88E5")
            # Update history
            if path in self.history: self.history.remove(path)
            self.history.append(path)
            self.config_repo.set("history", self.history[-10:])
            self._update_history_ui()
            threading.Thread(target=self.run_extraction, daemon=True).start()

    def select_destination(self):
        path = filedialog.askdirectory(initialdir=self.config_repo.get("output_path"))
        if path:
            self.config_repo.set("output_path", path)
            self.journal.info(f"Carpeta de destino: {path}")

    def load_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path: self.load_pdf_from_path(path)

    def run_extraction(self):
        try:
            self.after(0, lambda: self.lbl_status.configure(text="Extrayendo texto..."))
            text = self.use_case.extract_only(self.current_pdf_path)
            self.extracted_text = text
            self.after(0, self._on_extraction_complete)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error de Extracción", str(e)))
            self.after(0, lambda: self._set_busy(False))

    def _on_extraction_complete(self):
        self.lbl_status.configure(text="Texto cargado correctamente.")
        self._set_busy(False)
        if self.edit_mode_var.get(): self._update_editor_content()

    def show_logs(self):
        self.log_container.pack(fill="both", expand=False, pady=(10, 0))
        self.btn_show_logs.place_forget()

    def hide_logs(self):
        self.log_container.pack_forget()
        self.btn_show_logs.place(relx=0.5, rely=0.96, anchor="center")

    def toggle_editor(self):
        if self.edit_mode_var.get():
            self.editor_frame.pack(fill="x", after=self.toolbar, pady=(0, 15))
            self._update_editor_content()
        else:
            self.editor_frame.pack_forget()

    def update_v_vol_label(self, val): self.lbl_v_vol.configure(text=f"Voz: {int(val*100)}%")
    def update_b_vol_label(self, val): self.lbl_b_vol.configure(text=f"Música: {int(val*100)}%")
    def update_rate_label(self, val):
        self.lbl_rate.configure(text=f"Velo: {int(val)}%")
        self.config_repo.set("rate_val", int(val))

    def update_pitch_label(self, val):
        self.lbl_pitch.configure(text=f"Tono: {int(val)}Hz")
        self.config_repo.set("pitch_val", int(val))

    def _update_editor_content(self):
        self.text_editor.delete("1.0", "end")
        self.text_editor.insert("1.0", self.extracted_text)

    def preview_voice(self):
        text = self.text_editor.get("1.0", "end").strip() if self.edit_mode_var.get() else self.extracted_text
        if not text: return
        self._set_busy(True)
        self.btn_preview.configure(text="⌛")
        threading.Thread(target=self.run_preview, args=(text,), daemon=True).start()

    def run_preview(self, text):
        try:
            settings = VoiceSettings(
                voice_id=self.voice_var.get(),
                rate=f"{'+' if self.slider_rate.get() >= 0 else ''}{int(self.slider_rate.get())}%",
                pitch=f"{'+' if self.slider_pitch.get() >= 0 else ''}{int(self.slider_pitch.get())}Hz"
            )
            path = self.use_case.preview_voice(text, settings)
            os.startfile(path)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error Preview", str(e)))
        finally:
            self.after(0, lambda: self._set_busy(False))
            self.after(0, lambda: self.btn_preview.configure(text="🔊 Probar"))

    def stop_process(self):
        self.cancel_event.set()
        self.btn_cancel.configure(state="disabled")

    def load_bgm(self):
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.mp3;*.wav")])
        if path: self.bgm_path = path

    def start_pipeline(self):
        text_to_use = self.text_editor.get("1.0", "end").strip() if self.edit_mode_var.get() else self.extracted_text
        if not text_to_use: return
        self.cancel_event.clear()
        self._set_busy(True)
        self.btn_process.configure(text="⌛ CONVIRTIENDO...")
        self.btn_cancel.configure(state="normal")
        threading.Thread(target=self.run_generation, args=(text_to_use,), daemon=True).start()

    def run_generation(self, text):
        try:
            settings = VoiceSettings(
                voice_id=self.voice_var.get(),
                rate=f"{'+' if self.slider_rate.get() >= 0 else ''}{int(self.slider_rate.get())}%",
                pitch=f"{'+' if self.slider_pitch.get() >= 0 else ''}{int(self.slider_pitch.get())}Hz",
                volume=self.slider_v_vol.get()
            )
            def on_progress(msg, val): self.after(0, lambda: self._update_ui(msg, val))
            final = self.use_case.execute(
                text=text, pdf_path=self.current_pdf_path,
                output_base_dir=self.config_repo.get("output_path"),
                voice_settings=settings, bgm_path=self.bgm_path,
                bgm_volume=self.slider_b_vol.get(),
                progress_callback=on_progress, cancel_event=self.cancel_event
            )
            if final: self.after(0, lambda p=final: self._finish_success(p))
            else: self.after(0, self._finish_cancelled)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, self._reset_ui)
            self.after(0, lambda: self._set_busy(False))

    def _update_ui(self, msg, val):
        self.lbl_status.configure(text=msg)
        self.progress_bar.set(val)
        self.journal.info(msg)

    def _finish_success(self, path):
        if messagebox.askyesno("Éxito", "¿Deseas escuchar el audio final?"):
            os.startfile(path)

    def _finish_cancelled(self):
        self.lbl_status.configure(text="Cancelado.", text_color="orange")

    def _reset_ui(self):
        self.btn_process.configure(state="normal", text="🚀 INICIAR CONVERSIÓN")
        self.btn_cancel.configure(state="disabled")

    def _append_to_log(self, message):
        try:
            self.textbox_log.configure(state="normal")
            tag = "INFO"
            if "[ERROR]" in message: tag = "ERROR"
            elif "[WARN]" in message: tag = "WARN"
            self.textbox_log.insert("end", message, tag)
            self.textbox_log.see("end")
            self.textbox_log.configure(state="disabled")
        except: pass

if __name__ == "__main__":
    app = AntigravityApp()
    app.mainloop()
