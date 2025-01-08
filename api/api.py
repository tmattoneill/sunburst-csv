from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins

# Configure upload settings
UPLOAD_DIR = "../data/raw"
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/data', methods=['GET'])
def get_data():
    try:
        with open('../data/sunburst_data.json', 'r') as f:
            data = json.load(f)
            return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        # Create directory if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        original_name = secure_filename(file.filename)
        filename = f"{os.path.splitext(original_name)[0]}-{timestamp}.csv"

        # Save file
        file_path = os.path.join(UPLOAD_DIR, filename)
        file.save(file_path)

        return jsonify({
            "message": "File uploaded successfully",
            "filePath": file_path
        }), 200

    return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)