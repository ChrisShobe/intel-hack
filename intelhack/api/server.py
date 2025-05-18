from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import shutil

from pdf_text import extract_text_and_note_images # converting the pdf to text
from textChunk import process_text_and_chunk #converting the text to chunks
from quizGeneration import generate_quiz_from_chunk_file # generating the 

app = Flask(__name__, static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../dist')), static_url_path='')
CORS(app) # Enable CORS so React can access this server

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# filepath: intel-hack/intelhack/api/server.py
@app.route('/api', methods=['GET'])
def home():
    return jsonify({'message': 'Server is running!'})

@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['pdf']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    pdf_filename = file.filename
    base_name = os.path.splitext(pdf_filename)[0]
    pdf_path = os.path.join(UPLOAD_FOLDER, pdf_filename)

    try:
        # Step 1: Save PDF
        file.save(pdf_path)

        # Step 2: Extract text
        text_path = os.path.join(UPLOAD_FOLDER, f"{base_name}.txt")
        extract_text_and_note_images(pdf_path, text_path)

        # Step 3: Chunk text
        chunk_output_path = os.path.join(UPLOAD_FOLDER, f"{base_name}_chunks.txt")
        process_text_and_chunk(text_path, chunk_output_path)

        # Step 4: Generate quiz questions
        json_output_path = os.path.join(UPLOAD_FOLDER, f"{base_name}_quiz.json")
        csv_output_path = os.path.join(UPLOAD_FOLDER, f"{base_name}_quiz.csv")
        quiz_data = generate_quiz_from_chunk_file(chunk_output_path, json_output_path, csv_output_path)

        # Path to the React public directory (adjust this if needed)
        frontend_public_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/public'))
        public_json_path = os.path.join(frontend_public_path, 'quizData.json')

        # Copy quiz JSON to public so React frontend can access it
        shutil.copy(json_output_path, public_json_path)
    
    except Exception as e:
        return jsonify({'message': f'Upload succeeded, but processing failed: {str(e)}'}), 500

    return jsonify({
        'message': 'Upload and quiz generation complete!',
        'quiz_url': f'/uploads/{base_name}_quiz.json',
        'quiz_csv': f'/uploads/{base_name}_quiz.csv',
        'num_chunks': len(quiz_data),
        'total_questions': sum(len(chunk["questions"]) for chunk in quiz_data)
    })  

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
  app.run(debug=True, port=3000, host='0.0.0.0')