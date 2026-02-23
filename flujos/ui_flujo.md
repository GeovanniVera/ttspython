# Flujo de Experiencia de Usuario (UI/UX) - PDF To Speech Studio

Este documento detalla el recorrido del usuario (User Journey) y la arquitectura de información de la interfaz gráfica construida con `customtkinter`.

## 1. Arquitectura de la Interfaz (Layout)
La aplicación utiliza una disposición de **Panel Lateral (Sidebar)** y **Cuerpo Principal**, diseñada para un flujo de trabajo de izquierda a derecha.

- **Sidebar (Configuración Global):** Controla el mezclador de audio (volúmenes de voz y música) y la carga de música de fondo.
- **Toolbar (Acciones Rápidas):** Gestión de archivos PDF y toggle de modo edición.
- **Área Central (Visualización/Edición):** Muestra el estado del archivo o el editor de texto.
- **Panel de Control Inferior:** Configuración de voz (TTS) y disparadores de proceso.
- **Consola de Estado:** Feedback técnico en tiempo real.

## 2. Flujo de Trabajo Detallado

### Paso 1: Inicialización y Carga
1. **Entrada:** El usuario abre la aplicación. El `JournalAdapter` registra el inicio y lo muestra en la consola.
2. **Acción 1:** Click en "📁 Cargar PDF" para seleccionar el archivo de origen.
3. **Acción 2:** Click en "📂 Carpeta Destino" para definir dónde se guardarán los resultados.
4. **Proceso:** 
   - Se abre el explorador de archivos de Windows.
   - Al seleccionar un PDF, se dispara `run_extraction` en un hilo secundario.
   - **Feedback:** La barra de estado muestra "Extrayendo texto...".

### Paso 2: Preparación del Contenido (Opcional)
1. **Validación:** El switch "📝 Habilitar Edición" permanece bloqueado hasta que se haya cargado un PDF exitosamente.
2. **Acción:** Activar el switch "📝 Habilitar Edición".
3. **UI/UX:** Se despliega un `CTkTextbox` con el texto extraído.
4. **Propósito:** Permite al usuario corregir errores del OCR o eliminar secciones no deseadas (bibliografías, encabezados) antes de generar el audio.

### Paso 3: Configuración de Audio y Mezcla
1. **Ajuste de Voz:** El usuario selecciona el narrador, velocidad y tono.
2. **Prueba rápida:** Click en "🔊 Probar" genera una previsualización de las primeras 30 palabras para validar la configuración sin procesar todo el documento.
3. **Mezcla (Mixer):** 
   - El usuario carga una pista de música ("🎵 Cargar Música").
   - Ajusta los sliders de volumen. La UI responde dinámicamente mostrando el porcentaje (ej: "Música: 20%").

### Paso 4: Ejecución y Monitoreo (Pipeline)
1. **Acción:** Click en "🚀 INICIAR CONVERSIÓN".
2. **UX de Seguridad:** Los botones de inicio y carga se bloquean; se habilita el botón de cancelación (🛑).
3. **Feedback Visual:**
   - **Barra de Progreso:** Se actualiza según los fragmentos completados.
   - **Status Label:** Muestra información en tiempo real: `Generando: 5/20 - ETA: 45s`.
   - **Consola:** Muestra logs técnicos sobre la fusión de FFmpeg y la limpieza de archivos.

### Paso 5: Finalización
1. **Cierre:** Al llegar al 100%, se muestra un diálogo de confirmación ("Éxito").
2. **Acción Final:** Si el usuario acepta, el sistema abre el archivo MP3 final automáticamente con el reproductor predeterminado del sistema.
3. **Reset:** La UI vuelve a su estado "Listo", habilitando de nuevo todos los controles.

## 3. Manejo de Estados y Errores
- **Cancelación:** Si el usuario presiona "🛑", el `cancel_event` detiene los hilos de trabajo y el sistema limpia los archivos temporales de inmediato.
- **Errores de OCR:** Si el PDF es una imagen y falla Tesseract, se muestra un `messagebox` con el error técnico capturado.
- **BGM Opcional:** Si no hay música cargada, el flujo se adapta automáticamente para procesar solo la voz, manteniendo la consistencia de la UI.
