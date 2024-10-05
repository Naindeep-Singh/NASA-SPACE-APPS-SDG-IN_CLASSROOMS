import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials 

app = Flask(__name__)
TEMP_FOLDER = '/tmp'
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)
# Load Google Drive credentials
SERVICE_ACCOUNT_FILE = r'NASA-SPACE-APPS-SDG-IN_CLASSROOMS\creds\sdg-nasa-firebase-adminsdk-67pxz-cd966ca1fa.json'
SCOPES = ['https://www.googleapis.com/auth/drive.file']

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Secure the filename
    filename = secure_filename(file.filename)
    file_path = os.path.join(TEMP_FOLDER, filename)
    
    # Save the file temporarily
    file.save(file_path)

    try:
        # Upload the file to Google Drive in the specific folder
        file_metadata = {
            'name': filename,
            'parents': ['14Il3i8ql7k5gyqRBgjgU4TTqZC5VBx5X']  # Add the folder ID here
        }
        media = MediaFileUpload(file_path, mimetype='application/pdf')
        file_uploaded = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        # Return success response with file ID
        return jsonify({"message": "File uploaded successfully", "file_id": file_uploaded.get('id')}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_file/<file_id>', methods=['GET'])
def get_file(file_id):
    try:
        # Use the Drive API to get the file
        file = drive_service.files().get(fileId=file_id, fields='webContentLink').execute()
        return jsonify({"file_link": file.get('webContentLink')}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
