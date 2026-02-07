# Antigravity

Application for text-to-speech processing from PDF files.

## Delivery 1/7: UI Skeleton + PDF Selection + FFmpeg Validation

### Context
- Desktop App (Python/Tkinter)
- Personal use, 100% offline
- Platform: Windows 10/11
- Critical Dependency: FFmpeg

### Requirements
- **UX-01**: 100% visual interaction
- **UX-02**: Read single PDF
- **UX-03**: PDF upload section
- **UX-04**: Visual upload validation
- **RF-01**: PDF file selection
- **RF-02**: Support PDF only
- **RF-04**: PDF validation
- **RNF-05**: Platform Windows

### Traceability
- RNF-FFMPEG -> `services/utils.py` -> `check_ffmpeg`
- UX-03 -> `app.py` -> PDF Load Section
