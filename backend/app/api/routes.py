# app/api/routes.py
from flask import Blueprint, jsonify, request, Response, stream_with_context
import json
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from dataproc.report_processor import ReportProcessor
from dataproc.generic_processor import GenericProcessor, analyze_columns, validate_column_selection
from dataproc.db_handler import DatabaseHandler
from dataproc.file_analyzer import FileAnalyzer
from dotenv import load_dotenv
import queue
import threading

load_dotenv()

bp = Blueprint('api', __name__)

# Configure application settings
DATA_DIR = os.getenv('DATA_DIR', "../data")
UPLOAD_DIR = os.getenv('UPLOAD_DIR', "../data/raw")
DB_PATH = os.getenv('DATABASE_URL', "../data/security.db")
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

db = DatabaseHandler(DB_PATH)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/health')
def health_check():
    return {'status': 'healthy'}, 200


@bp.route('/analyze', methods=['POST'])
def analyze_file():
    """
    Analyze uploaded file structure and provide preview.
    Returns preview rows, suggested header row, and file type detection.
    """
    try:
        data = request.json
        file_path = data.get('filePath')
        num_rows = data.get('numRows', 10)
        
        if not file_path:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_FILE_PATH",
                    "user_message": "No file path provided for analysis.",
                    "suggestions": ["Please upload a file first"]
                }
            }), 400
        
        # Construct full path
        full_path = os.path.join(UPLOAD_DIR, file_path)
        
        if not os.path.exists(full_path):
            return jsonify({
                "success": False,
                "error": {
                    "code": "FILE_NOT_FOUND",
                    "user_message": "The uploaded file could not be found.",
                    "suggestions": [
                        "Try uploading the file again",
                        "Check that the file was uploaded successfully"
                    ]
                }
            }), 404
        
        # Analyze file
        analyzer = FileAnalyzer(full_path)
        result = analyzer.analyze(num_rows=num_rows)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        return jsonify({
            "success": False,
            "error": {
                "code": "ANALYSIS_ERROR",
                "user_message": "An unexpected error occurred while analyzing your file.",
                "suggestions": [
                    "Try uploading the file again",
                    "Check that the file is a valid CSV or Excel file",
                    "Contact support if the problem persists"
                ],
                "technical_details": str(e)
            }
        }), 500


@bp.route('/data', methods=['GET'])
def get_data():
    try:
        session_id = request.args.get('session_id', 'default')
        data_file = os.path.join(DATA_DIR, f'{session_id}_sunburst_data.json')

        # Fallback to old format if session file doesn't exist
        if not os.path.exists(data_file):
            data_file = os.path.join(DATA_DIR, 'sunburst_data.json')

        with open(data_file, 'r') as f:
            data = json.load(f)
            return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404


@bp.route('/table-data', methods=['GET', 'POST'])
def get_table_data():
    """
    Get table data - supports both generic mode (CSV) and legacy mode (security.db)
    """
    try:
        # Get session ID
        session_id = request.args.get('session_id', 'default') if request.method == 'GET' else request.get_json().get('session_id', 'default')

        # Check if we're in generic mode by reading session-specific metadata
        session_metadata_path = Path(DATA_DIR) / f'{session_id}_sunburst_data.json'
        fallback_metadata_path = Path(DATA_DIR) / 'sunburst_data.json'

        metadata_path = session_metadata_path if session_metadata_path.exists() else fallback_metadata_path

        is_generic_mode = False
        source_file = None
        tree_order = []

        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
                is_generic_mode = 'chart_name' in metadata
                source_file = metadata.get('source_file')
                tree_order = metadata.get('tree_order', [])

        if is_generic_mode and source_file:
            # Generic mode - read from CSV
            csv_path = Path(UPLOAD_DIR) / source_file

            if not csv_path.exists():
                return jsonify({"error": f"Source file not found: {source_file}"}), 404

            # Read CSV (low_memory=False to avoid DtypeWarning on large files)
            df = pd.read_csv(csv_path, low_memory=False)

            # Get filters and pagination params
            page = int(request.args.get('page', 1)) if request.method == 'GET' else 1
            items_per_page = int(request.args.get('items_per_page', 20)) if request.method == 'GET' else len(df)
            filters = {}

            if request.method == 'GET':
                filters_param = request.args.get('filters')
                if filters_param:
                    filters = json.loads(filters_param)
            elif request.method == 'POST' and request.is_json:
                filters = request.get_json() or {}

            # Apply filters
            filtered_df = df.copy()
            for column, value in filters.items():
                if column in filtered_df.columns and value:
                    filtered_df = filtered_df[filtered_df[column] == value]

            # Paginate
            total = len(filtered_df)
            total_pages = (total + items_per_page - 1) // items_per_page
            start_idx = (page - 1) * items_per_page
            end_idx = start_idx + items_per_page
            paginated_df = filtered_df.iloc[start_idx:end_idx]

            # Convert to records, replacing NaN with empty strings
            data = paginated_df.fillna('').to_dict('records')

            return jsonify({
                'data': data,
                'page': page,
                'total': total,
                'total_pages': total_pages
            }), 200

        else:
            # No data available - return empty result instead of falling back to legacy DB
            if not metadata_path.exists():
                return jsonify({
                    'data': [],
                    'page': 1,
                    'total': 0,
                    'total_pages': 0
                }), 200

            # Legacy mode - use database (only if metadata exists but is legacy format)
            if request.method == 'GET':
                page = int(request.args.get('page', 1))
                items_per_page = int(request.args.get('items_per_page', 20))
                filters = request.args.get('filters')
                if filters:
                    filters = json.loads(filters)
                result = db.get_filtered_data(page, items_per_page, filters, paginate=True)
                return jsonify(result), 200

            elif request.method == 'POST' and request.is_json:
                filters = request.get_json()
                result = db.get_filtered_data(filters=filters, paginate=False)
                return jsonify(result), 200

    except Exception as e:
        print(f"Error in get_table_data: {str(e)}")
        import traceback
        traceback.print_exc()
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
        file_ext = original_name.rsplit('.', 1)[1].lower()
        base_name = os.path.splitext(original_name)[0]
        
        # If Excel file, convert to CSV
        if file_ext in ['xls', 'xlsx']:
            temp_path = os.path.join(UPLOAD_DIR, f"temp_{timestamp}.{file_ext}")
            file.save(temp_path)
            
            try:
                # Read Excel file
                df = pd.read_excel(temp_path)
                
                # Save as CSV
                filename = f"{base_name}-{timestamp}.csv"
                file_path = os.path.join(UPLOAD_DIR, filename)
                df.to_csv(file_path, index=False)
                
                # Remove temp Excel file
                os.remove(temp_path)
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return jsonify({"error": f"Failed to convert Excel file: {str(e)}"}), 400
        else:
            # Save CSV directly
            filename = f"{base_name}-{timestamp}.csv"
            file_path = os.path.join(UPLOAD_DIR, filename)
            file.save(file_path)

        return jsonify({
            "message": "File uploaded successfully",
            "filePath": filename  # Send just the filename, not the full path
        }), 200

    return jsonify({"error": "File type not allowed. Please upload CSV, XLS, or XLSX files."}), 400


@bp.route('/file-info', methods=['GET'])
def get_file_info():
    """
    Get column metadata for an uploaded file.
    Returns column names, types, sample values, and statistics.
    Supports headerRow and skipRows parameters for flexible file parsing.
    """
    try:
        file_path_param = request.args.get('filePath')
        header_row = int(request.args.get('headerRow', 0))
        skip_rows = int(request.args.get('skipRows', 0))
        
        if not file_path_param:
            return jsonify({"error": "Missing filePath parameter"}), 400

        # Construct full path
        full_path = Path(UPLOAD_DIR) / file_path_param

        if not full_path.exists():
            return jsonify({"error": f"File not found: {file_path_param}"}), 404

        # Read file with specified header row and skip rows
        file_ext = full_path.suffix.lower()
        skiprows = list(range(skip_rows)) if skip_rows > 0 else None
        
        if file_ext == '.csv':
            df = pd.read_csv(full_path, header=header_row, skiprows=skiprows)
        else:
            df = pd.read_excel(full_path, header=header_row, skiprows=skiprows)

        # Analyze columns
        columns_info = analyze_columns(full_path, header_row=header_row, skip_rows=skip_rows)

        row_count = len(df)

        # Get preview (first 5 rows) - replace NaN with None for valid JSON
        preview = df.head(5).fillna('').to_dict('records')

        return jsonify({
            "columns": columns_info,
            "rowCount": row_count,
            "preview": preview,
            "fileName": file_path_param,
            "headerRow": header_row,
            "skipRows": skip_rows
        }), 200

    except Exception as e:
        print(f"Error analyzing file: {str(e)}")
        return jsonify({"error": f"Failed to analyze file: {str(e)}"}), 500


@bp.route('/validate-columns', methods=['POST'])
def validate_columns_endpoint():
    """
    Validate user's column selection before processing.
    """
    try:
        data = request.json
        file_path_param = data.get('filePath')
        tree_order = data.get('treeOrder', [])
        value_column = data.get('valueColumn')
        header_row = data.get('headerRow', 0)
        skip_rows = data.get('skipRows', 0)

        if not all([file_path_param, tree_order, value_column]):
            return jsonify({
                "valid": False,
                "errors": ["Missing required parameters: filePath, treeOrder, or valueColumn"]
            }), 400

        # Construct full path
        full_path = Path(UPLOAD_DIR) / file_path_param

        if not full_path.exists():
            return jsonify({
                "valid": False,
                "errors": [f"File not found: {file_path_param}"]
            }), 404

        # Validate selection
        is_valid, errors = validate_column_selection(full_path, tree_order, value_column, header_row, skip_rows)

        return jsonify({
            "valid": is_valid,
            "errors": errors,
            "warnings": []  # Could add warnings for non-critical issues
        }), 200

    except Exception as e:
        print(f"Error validating columns: {str(e)}")
        return jsonify({
            "valid": False,
            "errors": [f"Validation failed: {str(e)}"]
        }), 500


@bp.route('/process', methods=['POST'])
def process_file():
    """
    Process file for sunburst visualization with Server-Sent Events for progress.
    Supports both legacy (security report) and generic modes.
    """
    try:
        data = request.json
        input_file = data.get("filePath")

        if not input_file:
            return jsonify({"error": "Missing required parameter: filePath"}), 400

        # Check if this is a generic request (has treeOrder and valueColumn)
        tree_order = data.get("treeOrder")
        value_column = data.get("valueColumn")
        chart_name = data.get("chartName")
        session_id = data.get("sessionId", "default")
        header_row = data.get("headerRow", 0)
        skip_rows = data.get("skipRows", 0)

        if tree_order and value_column and chart_name:
            # Generic mode with progress tracking
            print(f"Processing (GENERIC): {chart_name}")
            print(f"  Session: {session_id}")
            print(f"  Hierarchy: {' → '.join(tree_order)}")
            print(f"  Value: {value_column}")
            print(f"  Header row: {header_row}, Skip rows: {skip_rows}")

            progress_queue = queue.Queue()

            def progress_callback(current, total, message):
                """Callback to send progress updates."""
                progress_queue.put({
                    'current': current,
                    'total': total,
                    'message': message
                })

            def generate():
                """Generator function for SSE."""
                try:
                    # Start processing in background thread
                    def process_in_thread():
                        try:
                            processor = GenericProcessor(
                                input_file=input_file,
                                chart_name=chart_name,
                                tree_order=tree_order,
                                value_column=value_column,
                                data_path=DATA_DIR,
                                session_id=session_id,
                                header_row=header_row,
                                skip_rows=skip_rows,
                                progress_callback=progress_callback
                            )
                            processor.process_all()
                            progress_queue.put({'done': True})
                        except Exception as e:
                            progress_queue.put({'error': str(e)})

                    thread = threading.Thread(target=process_in_thread)
                    thread.start()

                    # Stream progress updates
                    while True:
                        update = progress_queue.get()

                        if 'error' in update:
                            yield f"data: {json.dumps({'error': update['error']})}\n\n"
                            break
                        elif 'done' in update:
                            yield f"data: {json.dumps({'done': True})}\n\n"
                            break
                        else:
                            yield f"data: {json.dumps(update)}\n\n"

                    thread.join()

                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return Response(stream_with_context(generate()), mimetype='text/event-stream')

        else:
            # Legacy mode - security reports (no progress tracking)
            client_name = data.get("clientName")

            if not client_name:
                return jsonify({"error": "Missing required parameters. For generic mode: chartName, treeOrder, valueColumn. For legacy mode: clientName"}), 400

            print(f"Processing (LEGACY): {client_name}")

            try:
                processor = ReportProcessor(client_name=client_name, input_file=input_file)
                processor.process_all()

            except Exception as proc_error:
                print(f"Legacy processing error: {str(proc_error)}")
                return jsonify({"error": f"Processing failed: {str(proc_error)}"}), 500

            return jsonify({"message": "Report processed successfully"}), 200

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, port=int(os.getenv('FLASK_PORT', 6500)))
