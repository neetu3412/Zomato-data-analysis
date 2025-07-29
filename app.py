# app.py (Flask Backend)

from flask import Flask, request, jsonify  # Flask components for API
from flask_cors import CORS  # CORS support for frontend-backend communication
import pandas as pd  # For CSV handling
import os  # For checking file existence

# Initialize Flask app
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (important for requests from Streamlit app)
CORS(app)

# File path to store uploaded CSV temporarily
DATA_PATH = "uploaded_data.csv"

# -----------------------------
# 📥 File Upload API (POST /upload)
# Accepts a CSV file uploaded by the Streamlit frontend,
# performs basic cleaning (removes unnamed columns),
# and saves it locally as uploaded_data.csv
# -----------------------------
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Read and clean the uploaded file
    df = pd.read_csv(file)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # Drop unnamed columns
    df.to_csv(DATA_PATH, index=False)

    return jsonify({"message": "File uploaded and processed successfully"}), 200

# -----------------------------
# 📤 Data Retrieval API (GET /data)
# Returns the processed dataset as JSON to the frontend
# Used by Streamlit after upload to fetch and display the data
# -----------------------------
@app.route('/data', methods=['GET'])
def get_data():
    if not os.path.exists(DATA_PATH):
        return jsonify({"error": "No data found. Upload first."}), 404

    df = pd.read_csv(DATA_PATH)
    return df.to_json(orient='records')  # Return entire data as JSON

# -----------------------------
# Run the Flask app on localhost:5000
# -----------------------------
if __name__ == '__main__':
    app.run(port=5000, debug=True)
