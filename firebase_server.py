from flask import Flask, request, render_template, redirect, url_for, flash
import os
import io
import base64
from PIL import Image
import pdf2image
from dotenv import load_dotenv
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from flask import Flask, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r'C:\Users\Naindeep\Desktop\SDG\NASA-SPACE-APPS-SDG-IN_CLASSROOMS\creds\sdg-nasa-firebase-adminsdk-67pxz-cd966ca1fa.json')  # Update this path
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

app = Flask(__name__)
app.secret_key = "AIzaSyCRiShoZR6ctrRklHRgix1W6k_9p8GEtoU"

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Gemini API
def get_gemini_response(input_prompt, pdf_content, input_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_prompt, pdf_content[0], input_text])
    return response.text

# Function to process the PDF and convert it to an image
def input_pdf_setup(uploaded_file):
    images = pdf2image.convert_from_bytes(uploaded_file.read())
    first_page = images[0]
    img_byte_arr = io.BytesIO()
    first_page.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()
    
    pdf_parts = [
        {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }
    ]
    return pdf_parts

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.json
    # Set created_at and updated_at fields
    data['created_at'] = firestore.SERVER_TIMESTAMP
    data['updated_at'] = firestore.SERVER_TIMESTAMP
    
    user_ref = db.collection('users').add(data)  # Adds data to Firestore
    doc_id = user_ref[1].id  # Extract the document ID
    
    return jsonify({"status": "success", "doc_id": doc_id}), 201

# Route to get all users
@app.route('/get_users', methods=['GET'])
def get_users():
    users_ref = db.collection('users')
    docs = users_ref.stream()

    users = [doc.to_dict() for doc in docs]  # Convert Firestore documents to dictionary
    return jsonify(users), 200

# Route to update user credentials
@app.route('/update_user/<doc_id>', methods=['PUT'])
def update_user(doc_id):
    data = request.json
    db.collection('users').document(doc_id).set(data, merge=True)  # Merge updates
    return jsonify({"status": "success"}), 200

# Route to delete a user
@app.route('/delete_user/<doc_id>', methods=['DELETE'])
def delete_user(doc_id):
    db.collection('users').document(doc_id).delete()  # Delete Firestore document
    return jsonify({"status": "success"}), 200

# Route to add a document summary to a user's 'documents' subcollection
@app.route('/add_document_summary/<user_id>', methods=['POST'])
def add_document_summary(user_id):
    data = request.json
    # Set created_at and updated_at fields
    data['created_at'] = firestore.SERVER_TIMESTAMP
    data['updated_at'] = firestore.SERVER_TIMESTAMP
    
    # Add document summary to the user's 'documents' subcollection
    doc_ref = db.collection('users').document(user_id).collection('documents').add(data)
    doc_id = doc_ref[1].id  # Extract the document ID
    
    return jsonify({"status": "success", "doc_id": doc_id}), 201

# Route to get all documents for a given user ID
@app.route('/get_documents/<user_id>', methods=['GET'])
def get_documents(user_id):
    try:
        # Fetch all documents from the 'documents' subcollection for the user
        documents_ref = db.collection('users').document(user_id).collection('documents')
        docs = documents_ref.stream()

        # Convert the Firestore documents to a list of dictionaries
        documents = [doc.to_dict() for doc in docs]
        
        return jsonify(documents), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'pdf_file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    uploaded_file = request.files['pdf_file']
    if uploaded_file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    # Check if PDF is uploaded
    if uploaded_file and uploaded_file.filename.endswith('.pdf'):
        try:
            input_prompt = """
            You are a professional strategist and analyst with expertise in Sustainable Development Goals (SDGs). Your task is to analyze text documents by comparing them to a set of pre-defined SDG guidelines. These guidelines will be provided to you in a structured key format, and your job is to produce a comprehensive output in strict JSON format as follows:

1.⁠ ⁠Input Fields (Final Document):
Document Text (Final):
You will receive the final document text in the following format for analysis. This is the actual extracted text from the document, and it will be provided as:

text
Copy code
[document_text]
You should treat [document_text] as the final text to be analyzed and proceed with the evaluation accordingly.

SDG Guidelines (Pre-defined):
A structured list of SDG guidelines (in a mapped format) that will serve as the evaluation criteria:

json
Copy code
{
    "SDG1": "No poverty",
    "SDG2": "Zero hunger",
    "SDG3": "Good health and well-being",
    "SDG4": "Quality education",
    "SDG5": "Gender equality",
    "SDG6": "Clean water and sanitation",
    "SDG7": "Affordable and clean energy",
    "SDG8": "Decent work and economic growth",
    "SDG9": "Industry, innovation, and infrastructure",
    "SDG10": "Reduced inequalities",
    "SDG11": "Sustainable cities and communities",
    "SDG12": "Responsible consumption and production",
    "SDG13": "Climate action",
    "SDG14": "Life below water",
    "SDG15": "Life on land",
    "SDG16": "Peace, justice, and strong institutions",
    "SDG17": "Partnerships for the goals"
}
2.⁠ ⁠Expected Output in JSON Format:
SDG_score: A number from 0 to 10, representing how well the document aligns with SDG goals.
Guideline_mapping: An array of zeros (0) and ones (1) representing whether each guideline (from SDG1 to SDG17) is met. For instance, if the document aligns with SDG1 and SDG5, the array could look like: [1, 0, 0, 0, 1, 0, ...].
Summary: A concise summary evaluating how well the SDG guidelines are represented in the final document, identifying strengths and weaknesses.Summarize the whole pdf content in short.
    2. Also highlight  important points and keywords from the pdf.

            """
            input_text = request.form.get('input_text', '')

            # Process the PDF and convert to content for analysis
            pdf_content = input_pdf_setup(uploaded_file)

            # Get response from Gemini LLM
            response = get_gemini_response(input_prompt, pdf_content, input_text)

            # Render the response on a new page
            return render_template('result.html', response=response)

        except Exception as e:
            flash(f"Error during analysis: {e}")
            return redirect(url_for('index'))
    
    flash('Please upload a valid PDF file.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
