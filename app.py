from flask import Flask, request, render_template, redirect, url_for, flash
import os
import io
import base64
from PIL import Image
import pdf2image
from dotenv import load_dotenv
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_secret_key_here")

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

# Routes

## Home Route
@app.route('/')
def index():
    return render_template('home.html')

## Login Route
@app.route('/login', methods=['POST'])
def login():
    # Here we assume successful login without actual validation
    return redirect(url_for('pdf_analyze'))

@app.route('/student')
def student():
    return render_template('studentlogin.html')

@app.route('/mentor')
def mentor():
    return render_template('mentorlogin.html')


# PDF Analysis Route (Modified to accept POST requests)
@app.route('/pdf-analyze', methods=['GET', 'POST'])
def pdf_analyze():
    #ender the PDF analysis form
    return render_template('pdf-analyze.html')


## Analyze PDF (PDF Processing and Analysis)
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
            You are a professional strategist and analyst with expertise in Sustainable Development Goals (SDGs). Your task is to analyze text documents by comparing them to a set of pre-defined SDG guidelines. ...
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

# Main Function to Run the App
if __name__ == '__main__':
    app.run(debug=True)
