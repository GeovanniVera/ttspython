# PDF To Speech Studio

Desktop application that converts PDF documents into MP3 audio files using Text-to-Speech technology. Built with Python, PySide6 (Qt), and a hexagonal architecture (Ports & Adapters), it provides a complete pipeline: PDF text extraction → text normalization → voice generation → audio mixing → final MP3 output.

## Features

- **PDF Text Extraction**: Direct text extraction via `pypdf`, with automatic OCR fallback using Tesseract for scanned/image-based PDFs (powered by Poppler for PDF-to-image conversion).
- **Text Normalization**: Intelligent preprocessing that joins hyphenated words, normalizes whitespace, and prepares text for natural-sounding narration.
- **TTS Voice Generation**: Uses Microsoft Edge TTS (`edge-tts`) with multiple voice options (Spanish and English), configurable speed and pitch, and exponential backoff retry logic for API resilience.
- **Audio Mixing**: FFmpeg-powered merging of voice segments, optional background music mixing with volume control, and MP3 encoding.
- **Concurrent Processing**: Multi-threaded chunk processing with configurable parallelism for faster generation on large documents.
- **Interactive GUI**: PySide6 (Qt) interface with live progress tracking, text editor for manual corrections, audio mixer, and theme toggle (Dark/Light).
- **Project History**: Persistent recent files list for quick re-processing.

## Architecture

The project follows **Hexagonal Architecture** (Ports & Adapters), keeping the domain logic decoupled from infrastructure concerns:

```
ttspython/
├── main_hexagonal.py          # Entry point — launches Qt MainWindow
├── run.sh                     # Desktop launcher wrapper
├── src/
│   ├── domain/
│   │   ├── models/            # Core data structures (AudioProject, VoiceSettings)
│   │   ├── ports/             # Abstract interfaces (ports)
│   │   │   ├── DocumentExtractorPort   # PDF text extraction contract
│   │   │   ├── SpeechGeneratorPort     # TTS generation contract
│   │   │   ├── AudioProcessorPort      # Audio merge/mix/convert contract
│   │   │   └── OcrPort                 # OCR recognition contract
│   │   ├── exceptions.py      # Domain exceptions
│   │   └── services/
│   │       └── TextService    # Domain logic: text normalization & chunking
│   ├── application/
│   │   └── use_cases/
│   │       └── ProcessPdfToSpeechUseCase  # Orchestrates the full pipeline
│   ├── infrastructure/
│   │   ├── adapters/          # Concrete implementations (adapters)
│   │   │   ├── PyPdfAdapter           # pypdf + pdf2image + Tesseract OCR
│   │   │   ├── EdgeTTSAdapter         # edge-tts with retry/backoff
│   │   │   ├── FFmpegAdapter          # Audio merge, mix, convert, silence
│   │   │   ├── TesseractAdapter       # Parallel OCR via pytesseract
│   │   │   ├── JournalAdapter         # Thread-safe logging to UI
│   │   │   ├── PlainTextAdapter       # Plain text extraction
│   │   │   ├── MarkdownAdapter        # Markdown extraction
│   │   │   └── DocumentExtractorResolver  # Routes to correct adapter
│   │   ├── repositories/      # Persistence (config, cache)
│   │   │   ├── ConfigRepository       # JSON-based settings persistence
│   │   │   └── CacheRepository        # SHA256-keyed audio cache
│   │   ├── container.py       # Dependency injection (manual IoC container)
│   │   └── env_manager.py     # Binary paths, PyInstaller compatibility
│   └── interfaces/
│       └── gui/
│           ├── main_window.py  # PySide6 (Qt) main window
│           ├── signals.py      # WorkerSignals, QtJournalBridge
│           ├── styles/         # QSS theme + palette
│           ├── widgets/        # Reusable Qt widgets
│           └── assets/         # SVG icons
├── tests/                     # Test suite (35+ tests)
├── bin/                       # Local Tesseract & Poppler binaries (Windows)
├── flujos/                    # Flow documentation (text cleaning, UI flow)
└── design/                    # Style guide & design docs
```

### Data Flow

```
PDF → [PyPdfAdapter] → Raw Text
       ↓ (if no text: [TesseractAdapter] via OCR)
     [TextService] → Normalized & Chunked Text
       ↓
     [EdgeTTSAdapter] → MP3 fragments (concurrent)
       ↓
     [FFmpegAdapter] → Merged audio → Mixed with BGM → Final MP3
```

### Key Design Decisions

- **Ports & Adapters**: Domain defines abstract ports; infrastructure provides concrete adapters. Swapping Edge TTS for another provider requires only a new adapter — zero domain changes.
- **Manual IoC Container**: Simple `Container` class wires all dependencies at startup. No framework overhead.
- **Binary Portability**: `EnvManager` detects PyInstaller bundles vs development mode, resolving Tesseract/Poppler paths accordingly.
- **Thread Safety**: `JournalAdapter` uses a lock-protected callback pattern to safely bridge background threads and the GUI main loop via a queue.

## Tech Stack

| Layer | Technology |
|---|---|
| GUI | PySide6 (Qt) |
| TTS Engine | edge-tts (Microsoft Edge neural voices) |
| PDF Extraction | pypdf + pdf2image (Poppler) |
| OCR | pytesseract + Tesseract (bundled) |
| Audio Processing | FFmpeg (via imageio-ffmpeg) |
| Text Processing | num2words, regex |
| Packaging | PyInstaller |

## Setup

### Development

```bash
pip install -r requirements.txt
python main_hexagonal.py
```

### Binary Dependencies

The application requires Tesseract and Poppler binaries in the `bin/` directory. These are bundled for Windows distribution. For development on other platforms, install them system-wide:

```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-spa poppler-utils

# macOS
brew install tesseract tesseract-lang poppler
```

### Build (Windows)

```bash
pyinstaller main_hexagonal.py --onefile
```

## Configuration

Settings are persisted in `settings.json` (auto-created on first run):

| Key | Default | Description |
|---|---|---|
| `voice` | `es-MX-JorgeNeural` | TTS voice ID |
| `rate_val` | `0` | Speech rate adjustment (-50% to +50%) |
| `pitch_val` | `0` | Pitch adjustment (-20Hz to +20Hz) |
| `output_path` | `~/Music` | Default output directory |
| `appearance_mode` | `Dark` | UI theme |
| `history` | `[]` | Recent PDF file paths |
