# app/api/routes.py
from flask import Blueprint, jsonify, request
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from dataproc.report_processor import ReportProcessor
from dataproc.db_handler import DatabaseHandler

bp = Blueprint('api', __name__)

# Configure application settings
UPLOAD_DIR = os.getenv('UPLOAD_DIR', "/data/raw")
DB_PATH = os.getenv('DATABASE_URL', "/data/security.db")
ALLOWED_EXTENSIONS = {'csv'}

db = DatabaseHandler(DB_PATH)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

@bp.route('/data', methods=['GET'])
def get_data():
    try:
        with open('../data/sunburst_data.json', 'r') as f:
            data = json.load(f)
            return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404


# In api.py, update the get_table_data route:
@bp.route('/table-data', methods=['GET', 'POST'])
def get_table_data():
    try:
        if request.method == 'GET':
            # Normal table view with pagination
            page = int(request.args.get('page', 1))
            items_per_page = int(request.args.get('items_per_page', 20))
            filters = request.args.get('filters')
            if filters:
                filters = json.loads(filters)
            result = db.get_filtered_data(page, items_per_page, filters, paginate=True)
            return jsonify(result), 200

        elif request.method == 'POST' and request.is_json:
            # CSV download without pagination
            filters = request.get_json()
            result = db.get_filtered_data(filters=filters, paginate=False)
            headers = {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=export-{datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'
            }
            return jsonify(result), 200, headers

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/upload', methods=['POST'])
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
            "filePath": filename  # Send just the filename, not the full path
        }), 200

    return jsonify({"error": "File type not allowed"}), 400


@bp.route('/process', methods=['POST'])
def process_file():
    try:
        data = request.json
        client_name = data.get("clientName")
        input_file = data.get("filePath")

        print(f"Processing request with client_name: {client_name}, file: {input_file}")  # Debug log

        if not client_name or not input_file:
            return jsonify({"error": "Missing required parameters"}), 400

        # Initialize the report processor
        processor = ReportProcessor(client_name=client_name, input_file=input_file)

        try:
            # Process data for sunburst visualization
            processor.process_all()
        except Exception as proc_error:
            print(f"Detailed processing error: {str(proc_error)}")  # Debug log
            return jsonify({"error": f"Processing failed: {str(proc_error)}"}), 500

        return jsonify({"message": "Report processed successfully"}), 200

    except Exception as e:
        print(f"Error processing file: {str(e)}")  # Debug log
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, port=int(os.getenv('FLASK_PORT', 5001)))
