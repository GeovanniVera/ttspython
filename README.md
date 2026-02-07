# 🎙️ TTS Narrador Pro (Open Source PDF To Speech - Studio)

**Versión:** 1.1

¡Convierte tus documentos PDF en audiolibros profesionales con voces neuronales de alta calidad!
Esta aplicación de escritorio, construida con Python y CustomTkinter, ofrece una solución robusta y gratuita para la síntesis de voz, aprovechando la potencia de **Microsoft Edge TTS** y **FFmpeg**.

![TTS Narrador Pro](https://img.shields.io/badge/Status-Active-success) ![Python](https://img.shields.io/badge/Python-3.x-blue) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Características Principales

*   **📄 Extracción Inteligente de PDF**: Extrae y limpia el texto de tus documentos automáticamente.
*   **🗣️ Voces Neuronales**: Acceso a voces de alta calidad como *Jorge (México)*, *Lorenzo (Chile)*, *Dalia (México)* y *Alvaro (España)*.
*   **🎛️ Control Total de Audio**:
    *   Ajuste de **Velocidad** (-50% a +50%).
    *   Ajuste de **Tono** (-20Hz a +20Hz).
*   **🎵 Mezcla de Audio (Nuevo)**:
    *   Añade **Música de Fondo** (BGM) a tu narración.
    *   **Loop Automático**: La música se repite automáticamente para cubrir toda la duración de la voz.
    *   **Control de Volúmenes**: Ajusta independientemente el volumen de la voz y de la música.
*   **🚀 Procesamiento en Lotes**: Generación de audio por fragmentos para evitar errores en textos largos y permitir la reanudación.
*   **📦 Portátil**: Todo el proceso de conversión y mezcla se realiza localmente (usando binarios integrados de FFmpeg).
*   **🌑 Modo Oscuro**: Interfaz moderna y amigable para la vista.

---

## 🛠️ Requisitos e Instalación

### Prerrequisitos
*   **Python 3.8+**
*   **FFmpeg**: El sistema utiliza `imageio-ffmpeg` automáticamente, pero se recomienda tener FFmpeg instalado en el sistema o en la carpeta del proyecto para asegurar compatibilidad total.

### Instalación de Dependencias

Ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install -r requirements.txt
```

*Contenido de requirements.txt:*
*   `customtkinter`: Interfaz gráfica moderna.
*   `edge-tts`: Motor de síntesis de voz.
*   `pypdf`: Lectura de archivos PDF.
*   `imageio-ffmpeg`: Binarios de FFmpeg.
*   `pyinstaller`: Para crear el ejecutable.

---

## 🚀 Uso de la Aplicación

1.  **Iniciar la App**: Ejecuta `python app.py`.
2.  **Cargar PDF**: Haz clic en el botón "Cargar PDF" y selecciona tu archivo.
3.  **Configurar Voz**:
    *   Selecciona la voz deseada en el menú desplegable.
    *   Ajusta los sliders de Velocidad y Tono según tu preferencia.
4.  **Añadir Música (Opcional)**:
    *   En la barra lateral, haz clic en "Cargar Música".
    *   Selecciona un archivo MP3 o WAV.
    *   Ajusta los volúmenes de Voz y Música.
5.  **Generar**: Haz clic en "Procesar y Generar Audio".
    *   La aplicación extraerá el texto, generará los fragmentos de audio y unirá todo en un archivo final.
    *   **Nota**: Durante la generación, verás el progreso en la barra inferior.
6.  **Resultado**: Al finalizar, puedes reproducir el audio directamente o abrir la carpeta de salida.

---

## 🏗️ Construcción del Ejecutable (Build)

Para generar un archivo `.exe` independiente (portable) que incluya todas las dependencias y binarios:

1.  Asegúrate de tener instalado `pyinstaller`:
    ```bash
    pip install pyinstaller
    ```
2.  Ejecuta el script de construcción:
    ```bash
    python build.py
    ```
3.  El ejecutable se generará en la carpeta `dist/TTS_Narrador_Pro/`.

*Nota: El proceso de build utiliza `main.spec` para incluir automáticamente los binarios de FFmpeg y los recursos de CustomTkinter.*

---

## 📂 Estructura del Proyecto

```text
text_to_speach/
├── app.py                  # Punto de entrada y GUI (CustomTkinter)
├── requirements.txt        # Dependencias
├── build.py                # Script de automatización de PyInstaller
├── main.spec               # Configuración avanzada de PyInstaller
├── services/               # Módulos de lógica de negocio
│   ├── audio_mixer.py      # [Nuevo] Mezcla de voz y música con FFmpeg
│   ├── chunker.py          # División de texto inteligente
│   ├── config_manager.py   # Gestión de configuración (settings.json)
│   ├── journal.py          # Sistema de logging
│   ├── mp3_converter.py    # Conversión WAV -> MP3
│   ├── output_manager.py   # Gestión de carpetas de salida
│   ├── pdf_extractor.py    # Extracción de texto de PDF
│   ├── text_preprocessor.py# Limpieza de texto
│   ├── tts_engine.py       # Cliente de Edge TTS
│   ├── utils.py            # Utilidades generales
│   └── wav_merger.py       # Unión de fragmentos WAV
└── tests/                  # Pruebas unitarias
```

---

## 🤝 Contribuciones

Este es un proyecto de código abierto. ¡Las contribuciones son bienvenidas!
Visita el repositorio oficial: [GitHub - GeovanniVera/ttspython](https://github.com/GeovanniVera/ttspython)

---

**Desarrollado con ❤️ y Python.**
