 plan de optimización avanzado dividido en 4 ejes:

  ---


  1. Optimización de Salida (Calidad Narrativa)
  El sistema actual convierte el texto de forma plana. Para una experiencia profesional (tipo audiolibro):
   * Normalización de Texto Inteligente: Implementar un motor que traduzca símbolos ($, %, &) y números (fechas,
     monedas) a palabras narradas. No es lo mismo leer "10/12/2024" que "diez de diciembre de dos mil veinticuatro".
   * Gestión de Pausas Dinámicas: Permitir que el TextService detecte cambios de párrafo o etiquetas personalizadas (ej:
     [silencio:2s]) e inserte pausas reales de audio mediante FFmpeg entre fragmentos.


  2. Optimización de Distribución (Reducción de Peso)
  Actualmente, los binarios de Tesseract y Poppler son pesados (~100-200MB):
   * Poda de Binarios (Pruning): Eliminar archivos de idioma de Tesseract no utilizados (mantener solo spa y eng) y DLLs
     de Poppler innecesarias para reducir el tamaño del instalador final en un 40%.
   * Compresión UPX: Configurar la compresión de ejecutables en el main.spec para que el archivo final sea mucho más
     pequeño sin perder rendimiento.


  3. Optimización de Rendimiento (Concurrencia Adaptativa)
   * Control de Rate Limiting: El sistema actual lanza 4 hilos fijos. Si el PDF es muy largo, Edge TTS podría bloquear
     la IP. Optimizar el adaptador para que detecte errores 429 (Too Many Requests) y reduzca la velocidad de forma
     automática (Exponential Backoff).
   * Pipeline en Memoria (RAM Disk): En lugar de escribir fragmentos en disco y luego borrarlos, podemos usar objetos
     BytesIO para procesar todo en memoria RAM, reduciendo el desgaste del SSD y ganando milisegundos extra.


  4. Experiencia de Usuario (UX Premium)
   * Drag & Drop: Permitir al usuario arrastrar el PDF directamente a la ventana de la aplicación.
   * Modo Nocturno/Claro Seleccionable: Añadir un botón para que el usuario elija su tema preferido (actualmente está
     fijo en Dark).
   * Historial de Proyectos: Guardar una lista de los últimos PDFs procesados para cargarlos rápidamente con su
     configuración anterior.

  ---

  Resumen de Impacto



  ┌────────────────────────┬──────────┬────────────────────────────┐
  │ Tarea                  │ Esfuerzo │ Beneficio                  │
  ├────────────────────────┼──────────┼────────────────────────────┤
  │ Normalización de Texto │ Medio    │ Crítico (Calidad de audio) │
  │ Pausas entre Párrafos  │ Bajo     │ Alto (Naturalidad)         │
  │ Poda de Binarios       │ Bajo     │ Alto (Portabilidad)        │
  │ Drag & Drop            │ Medio    │ Alto (Comodidad)           │
  └────────────────────────┴──────────┴────────────────────────────┘
