from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from pdf_text import extract_text_and_note_images  # Import your PDF processor

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔄 Route to handle PDF upload and processing
@app.route('/api/upload', methods=['POST'])
def upload_pdf():
    if 'pdf' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    pdf = request.files['pdf']
    filename = pdf.filename
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    pdf.save(save_path)

    # Process the uploaded PDF
    output_path = os.path.join("data", "pdfoutput.txt")
    extract_text_and_note_images(save_path, output_path)

    return jsonify({
        "message": f"Processed '{filename}' successfully.",
        "output_file": output_path
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)