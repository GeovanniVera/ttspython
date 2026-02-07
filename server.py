
import os
import sys
import threading
import uuid
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Add services to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from services import pdf_extractor, text_preprocessor, chunker, output_manager, tts_engine, wav_merger, mp3_converter

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global state (simplified for single-user local app)
class AppState:
    def __init__(self):
        self.current_pdf_path = None
        self.extracted_text = None
        self.chunks = []
        self.output_dir = None
        self.processing = False
        self.tts_progress = {"current": 0, "total": 0, "status": "Idle"}
        self.tts_engine = tts_engine.TTSEngine()

state = AppState()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({
        "pdf_loaded": bool(state.current_pdf_path),
        "text_ready": bool(state.extracted_text),
        "tts_progress": state.tts_progress,
        "pdf_name": os.path.basename(state.current_pdf_path) if state.current_pdf_path else None
    })

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        # Use a unique ID to avoid overwrites/conflicts in uploads
        unique_id = str(uuid.uuid4())[:8]
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{filename}")
        file.save(save_path)
        
        state.current_pdf_path = save_path
        
        # Auto-process text extraction
        try:
            raw_text, metadata = pdf_extractor.extract_text(save_path)
            if not metadata['success']:
                return jsonify({"error": metadata.get('error', 'Unknown extraction error')}), 500
            
            clean_text = text_preprocessor.preprocess(raw_text)
            state.extracted_text = clean_text
            state.chunks = chunker.chunk_text(clean_text)
            
            return jsonify({
                "message": "PDF uploaded and processed",
                "pages": metadata['num_pages'],
                "word_count": len(clean_text.split()),
                "chunk_count": len(state.chunks)
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/api/tts/start', methods=['POST'])
def start_tts():
    if not state.extracted_text:
        return jsonify({"error": "No text extracted"}), 400
    
    if state.processing:
        return jsonify({"message": "Already processing"}), 200

    # Reset progress
    state.tts_progress = {"current": 0, "total": len(state.chunks), "status": "Starting..."}
    
    # Run in thread
    thread = threading.Thread(target=run_tts_process)
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "TTS started"})

def run_tts_process():
    state.processing = True
    try:
        # Prepare output
        state.output_dir = output_manager.prepare_output_structure(state.current_pdf_path)
        total = len(state.chunks)
        state.tts_progress["total"] = total
        state.tts_progress["status"] = "Generating..."
        
        for i, chunk in enumerate(state.chunks):
            state.tts_progress["current"] = i + 1
            index = i + 1
            filename = output_manager.get_chunk_filename(state.output_dir, os.path.basename(state.current_pdf_path).split('.')[0], index, total)
            
            # Call Engine
            state.tts_engine.save_to_file(chunk, filename)
            
    except Exception as e:
        print(f"TTS Error: {e}")
        state.tts_progress["status"] = f"Error: {e}"
    finally:
        state.processing = False
        if state.tts_progress["status"] == "Generating...":
             state.tts_progress["status"] = "Completed"

@app.route('/api/merge', methods=['POST'])
def merge_audio():
    if not state.output_dir:
        return jsonify({"error": "No audio chunks found"}), 400
        
    try:
        base_name = output_manager.get_base_name(state.current_pdf_path)
        wav_files = [f for f in os.listdir(state.output_dir) if f.endswith('.wav')]
        count = len(wav_files)
        
        final_path = wav_merger.merge_wavs(state.output_dir, base_name, count)
        
        # Auto convert to MP3 for web playback compatibility (optional, but good)
        mp3_path = mp3_converter.convert_wav_to_mp3(final_path)
        
        return jsonify({
            "message": "Merge complete",
            "wav_path": final_path,
            "mp3_path": mp3_path,
            "filename": os.path.basename(mp3_path)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/download/<path:filename>')
def download_file(filename):
    # This is a bit insecure for production but fine for local tool
    # We assume filename is inside the output structure
    # A safer way would be to track exact generated file paths
    # For now, let's try to serve from the final output dir
    
    if not state.current_pdf_path:
        return "No file generated", 404
        
    final_dir = output_manager.get_final_output_dir(state.current_pdf_path)
    file_path = os.path.join(final_dir, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    if state.output_dir and os.path.exists(state.output_dir):
        os.startfile(state.output_dir)
        return jsonify({"message": "Opened"})
    return jsonify({"error": "Folder not found"}), 404

if __name__ == '__main__':
    # Auto-open browser
    threading.Timer(1.5, lambda: os.system('start http://127.0.0.1:5000')).start()
    app.run(debug=True, use_reloader=False)
