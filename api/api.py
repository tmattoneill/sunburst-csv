from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app) # Enable CORS for all routes and origins


@app.route('/data', methods=['GET'])
def get_data():
    try:
        with open('../data/sunburst_data.json', 'r') as f:
            data = json.load(f)
            return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404


if __name__ == '__main__':
    app.run(debug=True, port=5001)