from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

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

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    return jsonify({'message': 'Upload complete!'})

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