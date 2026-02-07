# QA & DevRel Guide: Antigravity TTS

Este documento detalla el proceso de configuración, ejecución y validación de la aplicación **Antigravity**.

## A) Prerrequisitos (Windows)

Para ejecutar esta aplicación en un entorno Windows 10/11, asegúrese de cumplir con lo siguiente:

1.  **Windows 10 o 11** (64-bit recomendado).
2.  **Python 3.8+** instalado y agregado al PATH.
    -   Verificar con: `python --version`
3.  **FFmpeg** instalado y agregado al PATH. **(CRÍTICO)**
    -   La aplicación **no iniciará** si FFmpeg no es accesible.
    -   Verificar con: `ffmpeg -version`
4.  **Permisos de Escritura**: La aplicación creará carpetas (`output/`) en el directorio desde donde se ejecute.

## B) Instalación

1.  **Obtener el código**:
    Descargue o clone el repositorio en una carpeta local (ej: `C:\Desarrollo\text_to_speach`).

2.  **Instalar dependencias Python**:
    Abra una terminal en la carpeta raíz del proyecto y ejecute:
    ```bash
    pip install pypdf pyttsx3
    ```
    *Nota: `tkinter` y `unittest` vienen incluidos en la instalación estándar de Python en Windows.*

## C) Ejecución

1.  **Iniciar la aplicación**:
    Desde la terminal en la carpeta raíz:
    ```bash
    python app.py
    ```

2.  **Verificación de Inicio**:
    -   Debe aparecer una ventana titulada "Antigravity - Text to Speech".
    -   En la sección "Bitácora de Eventos" (abajo), debe ver el mensaje: `[INFO] FFmpeg detectado correctamente.`
    -   Si aparece un error de FFmpeg, revise la sección F) Troubleshooting.

## D) Pruebas Manuales (Validación Entrega 1/7)

Esta sección se enfoca en validar los cimientos de la aplicación (Carga y Validación de Archivos).

| Caso | Acción | Resultado Esperado (UI) | Resultado Esperado (Bitácora) |
| :--- | :--- | :--- | :--- |
| **01** | Iniciar App (Con FFmpeg) | Ventana abre sin errores. Estado: "Esperando PDF..." | `[INFO] FFmpeg detectado correctamente.` |
| **02** | Iniciar App (Sin FFmpeg) | Mensaje Error Crítico (Popup). Botón "Cargar PDF" deshabilitado. | `[ERROR] FFmpeg no detectado...` |
| **03** | Cargar archivo no PDF | El diálogo de archivo no debe mostrar/permitir seleccionar archivos que no sean `.pdf` (Filtro activo). | N/A (El usuario no debería poder seleccionar otro tipo). |
| **04** | Cargar PDF corrupto (header inválido) | Mensaje de Error "Validación fallida". Estado: "Error al cargar PDF". | `[ERROR] Validación fallida: El archivo no es un PDF válido...` |
| **05** | Cargar PDF Válido | Estado: "PDF Cargado...". Botón "Procesar" se habilita. | `[INFO] PDF validado y cargado exitosamente.` |
| **06** | Cancelar selección | No cambia el estado. | N/A o `[INFO] Intentando cargar...` sin seguimiento. |

*Para simular el caso 02 (Sin FFmpeg), puede renombrar temporalmente la carpeta de FFmpeg o quitarla del PATH y reiniciar la terminal.*

## E) Pruebas Automáticas

El proyecto incluye pruebas unitarias utilizando `unittest`.

1.  **Ejecutar todas las pruebas**:
    ```bash
    python -m unittest discover tests
    ```

2.  **Interpretación de Resultados**:
    -   `OK`: Todas las pruebas pasaron.
    -   `FAIL` / `ERROR`: Algo falló. Revise el traceback para ver qué función falló (ej: `test_basics.py`).

3.  **Archivos de prueba**:
    -   `tests/test_basics.py`: Valida `utils.py` (FFmpeg, validación PDF).
    -   `tests/test_extraction.py`: Valida `pdf_extractor` y `text_preprocessor`.
    -   `tests/test_tts.py`: Valida `chunker`, `output_manager` y `tts_engine`.
    -   `tests/test_merger.py`: Valida `wav_merger`.
    -   `tests/test_converter.py`: Valida `mp3_converter`.

## F) Troubleshooting

1.  **FFmpeg no se reconoce / Error Crítico al inicio**:
    -   **Causa**: Windows no encuentra `ffmpeg.exe`.
    -   **Solución**: Reinstale FFmpeg o asegúrese de que la ruta a su carpeta `bin` está en las Variables de Entorno (PATH). Reinicie la terminal después de cambiar el PATH.

2.  **`This application failed to start because no Qt platform plugin could be initialized`**:
    -   **Causa**: Conflicto raro con bibliotecas gráficas o PySide/PyQt si están instaladas (aunque usamos Tkinter).
    -   **Solución**: Generalmente no aplica a Tkinter, pero si ocurre, revise conflictos de `pip`.

3.  **Error `ModuleNotFoundError: No module named 'pypdf'`**:
    -   **Solución**: Ejecute `pip install pypdf`.

4.  **La UI no abre / se cierra inmediatamente**:
    -   Ejecute `python app.py` desde una terminal (CMD/PowerShell) en lugar de doble clic, para ver el error (traceback) en pantalla.

5.  **Permisos de Escritura**:
    -   Si falla al generar audio, verifique que no está ejecutando desde una carpeta protegida (como `C:\Program Files`). Mueva el proyecto a `Documentos` o `C:\Desarrollo`.

## G) Checklist de Validación Rápida (Entrega 1 - Base)

- [ ] Python 3.8+ instalado.
- [ ] FFmpeg accesible desde terminal (`ffmpeg -version`).
- [ ] `pip install pypdf pyttsx3` ejecutado.
- [ ] `python app.py` abre la ventana principal.
- [ ] La bitácora muestra "FFmpeg detectado".
- [ ] El botón "Cargar PDF" abre el explorador de archivos.
- [ ] El filtro de archivos solo muestra `*.pdf`.
- [ ] Cargar un PDF válido actualiza el estado a "Listo para procesar".
- [ ] Intentar cargar un archivo falso (crear un .txt y renombrar a .pdf) da error de validación.
