from flask import Flask, request, render_template, redirect, url_for, flash
import os
import io
import base64
from PIL import Image
import pdf2image
from dotenv import load_dotenv
import google.generativeai as genai

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


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/mentor')
def mentor():
    return render_template('mentorlogin.html')

@app.route('/student')
def student():
    return render_template('studentlogin.html')


@app.route('/pdf-analyze')
def pdfanalyze():
    return render_template('pdf-analyze.html')

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
