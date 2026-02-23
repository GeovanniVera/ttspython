# Flujo de Limpieza y Normalización de Texto

Este documento describe cómo se procesa el texto desde la extracción del PDF hasta la generación del audio, detallando el tratamiento de símbolos y pausas.

## 1. Preprocesamiento (`preprocess`)
- **Unión de guiones:** Se eliminan los guiones al final de línea (`- 
`) para reconstruir palabras rotas.
- **Normalización de saltos de línea:** Se convierten todos los finales de línea a `
`.
- **Detección de párrafos:** Se identifican saltos de línea dobles y se inserta una etiqueta temporal `[PAUSE:1.0]`.
- **Limpieza de espacios:** Se eliminan espacios múltiples y se convierte el texto en una sola línea continua (manteniendo las etiquetas de pausa).
- **Sustitución de símbolos:** 
  - `&` se convierte en " y ".
  - `%` se convierte en " por ciento ".
  - `@` se convierte en " arroba ".

## 2. Normalización Inteligente (`normalize_text`)
Este paso utiliza la librería `num2words` para convertir elementos técnicos en lenguaje natural narrable:
- **Monedas:** Detecta el símbolo `$` y convierte cifras a palabras (ej: $100 -> "cien dólares").
- **Fechas:** Detecta formatos `DD/MM/AAAA` y los convierte a formato narrado (ej: "diez de diciembre...").
- **Números:** Convierte cualquier cifra numérica aislada a su equivalente en palabras según el idioma configurado (español o inglés).

## 3. Segmentación (`chunk_text`)
- El texto normalizado se divide utilizando la etiqueta `[PAUSE:X]` como delimitador.
- El resultado es una lista de tuplas: `("text", "contenido narrable")` o `("pause", "duración")`.
- Los segmentos de texto se subdividen adicionalmente si exceden el límite de palabras configurado para evitar saturar la API.

## 4. Generación de Audio
- Si el segmento es `"text"`, se envía al motor `EdgeTTS`.
- Si el segmento es `"pause"`, el `FFmpegAdapter` genera un archivo de silencio puro con la duración especificada.
