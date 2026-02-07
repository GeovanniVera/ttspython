# Guía de Migración de TTS (SAPI → Coqui/Neural)

Actualmente, Antigravity usa **SAPI5 (pyttsx3)**, el motor nativo de Windows. Es rápido y funciona sin internet, pero la voz suena robótica. Si desea una voz natural (neural), aquí le explico las opciones y qué información necesito para realizar el cambio.

## Opción 1: Coqui TTS (Recomendado para Offline / Privacidad)
Utiliza modelos de Deep Learning (VITS/Tacotron2) para generar voces muy realistas localmente.

*   **Pros:** Funciona sin internet. Alta calidad. Gratis.
*   **Contras:** Lento en CPU (necesita GPU NVIDIA para ser rápido). La instalación es pesada (>2GB en librerías). Puede ser complicado instalar en Windows (requiere C++ Build Tools).

## Opción 2: Edge TTS (Recomendado para Calidad/Facilidad)
Usa el motor de Microsoft Edge (Azure) de forma gratuita.

*   **Pros:** Calidad extrema (casi humana). Muy rápido. Instalación sencilla (`pip install edge-tts`).
*   **Contras:** Requiere internet constante.

## Opción 3: OpenAI / ElevenLabs (Premium)
API de pago.

*   **Pros:** La mejor calidad del mercado. Clonación de voz.
*   **Contras:** Cuesta dinero por carácter. Requiere API Key y tarjeta de crédito.

---

## Qué pedirme para integrar Coqui TTS

Si decide usar **Coqui TTS** (la opción más compleja pero local), necesito que copie y complete el siguiente "Prompt Maestro" para que yo pueda configurar el entorno correctamente.

### 📋 Copie y pegue esto en el chat:

> "Quiero migrar el motor TTS de Antigravity a **Coqui TTS**.
>
> **Mis especificaciones son:**
> 1.  **Sistema Operativo:** Windows 10/11
> 2.  **Tarjeta Gráfica (GPU):** [Tengo NVIDIA RTX 3060 / No tengo GPU dedicada, usaré CPU]
> 3.  **Python actual:** [3.9 / 3.10 / 3.11] *(Nota: Coqui suele fallar en Python 3.12+, ideal < 3.11)*
> 4.  **Idioma preferido:** Español [Latino / España]
> 5.  **Acepto instalar:** Visual Studio C++ Build Tools si es necesario (para compilar eSpeak/MeCab).
>
> **Tarea:**
> - Crear un nuevo entorno virtual (opcional pero recomendado) o actualizar `requirements.txt`.
> - Reemplazar la lógica en `services/tts_engine.py` para usar `TTS.api`.
> - Descargar el modelo `tts_models/es/css10/vits` (u otro recomendado).
>
> Por favor, dame las instrucciones paso a paso para prepar mi entorno antes de que toques el código."

---

## Qué pedirme para integrar Edge TTS (Más fácil)

Si prefiere la **Opción 2 (Edge TTS)**, el cambio es mucho más rápido y menos propenso a errores de instalación.

### 📋 Copie y pegue esto:

> "Quiero cambiar el motor TTS por **Edge TTS** (online gratuito).
> - Instala `edge-tts` y `nest_asyncio`.
> - Modifica `services/tts_engine.py` para usar `edge_tts` con la voz `es-MX-DaliaNeural` (o similar).
> - Asegura que funcione con `asyncio` dentro del hilo de Tkinter."
