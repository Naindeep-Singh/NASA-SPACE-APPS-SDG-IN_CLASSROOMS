from flask import Flask, request, render_template, redirect, url_for, flash
import os
import io
import base64
from PIL import Image
import fitz  # PyMuPDF for handling PDFs
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
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input_prompt, pdf_content, input_text])
    return response.text


# Function to process the PDF and extract the first page as an image or text
def input_pdf_setup(uploaded_file):
    pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")

    # Extract text from the first page of the PDF
    first_page = pdf_document[0]
    pdf_text = first_page.get_text("text")

    # Convert the first page to an image (optional if needed for Gemini analysis)
    pix = first_page.get_pixmap()
    img_byte_arr = io.BytesIO(pix.tobytes("jpeg"))
    img_byte_arr = img_byte_arr.getvalue()

    pdf_parts = {
        "text_content": pdf_text,
        "image_content": base64.b64encode(img_byte_arr).decode(),
    }

    return pdf_parts


# Routes


## Home Route
@app.route("/")
def index():
    return render_template("home2.html")


## Login Route
@app.route("/login", methods=["POST"])
def login():
    # Here we assume successful login without actual validation
    return redirect(url_for("pdf_analyze"))


@app.route("/student")
def student():
    return render_template("studentlogin.html")


@app.route("/quiz")
def quiz():
    return render_template("quiz.html")


@app.route("/quiz-score")
def quizscore():
    score = request.args.get("score", 0)
    total = request.args.get("total", 0)
    return render_template("quiz-score.html", score=score, total=total)


@app.route("/mentor")
def mentor():
    return render_template("mentorlogin.html")


# PDF Analysis Route (Modified to accept POST requests)
@app.route("/pdf-analyze", methods=["GET", "POST"])
def pdf_analyze():
    # Render the PDF analysis form
    return render_template("pdf-analyze.html")


## Analyze PDF (PDF Processing and Analysis)
@app.route("/analyze", methods=["POST"])
def analyze():
    if "pdf_file" not in request.files:
        flash("No file part")
        return redirect(request.url)

    uploaded_file = request.files["pdf_file"]
    if uploaded_file.filename == "":
        flash("No selected file")
        return redirect(request.url)

    # Check if PDF is uploaded
    if uploaded_file and uploaded_file.filename.endswith(".pdf"):
        try:
            input_prompt = """
            Professional Prompt:

Role: You are a professional strategist and analyst specializing in Sustainable Development Goals (SDGs). Your task is to analyze text documents by comparing them against pre-defined SDG guidelines.

Instructions:

1. Document Text (Final): You will receive the final document text as [document_text]. This is the full extracted text that you are required to analyze.


2. SDG Guidelines (Pre-defined): Use the following structured SDG guidelines as the evaluation criteria:

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



Expected Output (Strictly in JSON Format - jsut giv the data  , do not start with ''json  and do nto end with '''):

SDG_score: A score from 0 to 10, representing how well the document aligns with SDG goals.

Guideline_mapping: An array of zeros (0) and ones (1), indicating whether each SDG guideline is met. For example, if SDG1 and SDG5 are met, the array would look like: [1, 0, 0, 0, 1, 0, ...].

Summary: Provide a concise evaluation of how well the SDG guidelines are represented in the document, including strengths and weaknesses.

Suggestive Improvements: Provide actionable suggestions for improving the alignment of the document with the SDG guidelines, formatted as bullet points.


Example Output strictly no use of  '''json at start and no use of ''' in end:

{
    "SDG_score": 8,
    "Guideline_mapping": [1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0],
    "Summary": "The document strongly aligns with SDG1, SDG2, SDG5, SDG7, and SDG10, demonstrating effective policies aimed at poverty reduction, gender equality, and access to clean energy. However, it lacks significant content on SDG4 (Quality education) and SDG6 (Clean water and sanitation).",
    "Suggestive Improvements": [
        "Incorporate educational initiatives or programs to enhance alignment with SDG4 (Quality education).",
        "Add strategies or practices that ensure access to clean water and sanitation to align with SDG6.",
        "Consider including more specific data or case studies to illustrate the impact of policies related to SDG3 (Good health and well-being).",
        "Strengthen partnerships with local communities or organizations to enhance outreach for SDG17 (Partnerships for the goals)."
    ]
}

Additional Requirements:

Positive Patterns:

Always highlight where the document aligns with the SDG guidelines. Mention specific strengths and policies where applicable.

Ensure that the positive pattern is consistent and not broken at any cost. The output must clearly and consistently highlight areas of alignment with SDG goals.


Negative Patterns:

Identify and explicitly point out gaps and areas not aligned with the SDG guidelines.

Provide constructive suggestions on how these areas could improve.

Ensure that the negative pattern is followed consistently and not broken at any cost. Any areas lacking alignment must be addressed thoroughly and consistently.


Strict Adherence to Format: The output must strictly follow the JSON format without deviations.

            """
            input_text = request.form.get("input_text", "")

            # Process the PDF and convert to content for analysis
            pdf_content = input_pdf_setup(uploaded_file)

            # Get response from Gemini LLM
            response = get_gemini_response(
                input_prompt, pdf_content["text_content"], input_text
            )

            print(response)
            cleaned_response = (
                response.replace("```json", "").replace("```", "").strip()
            )
            # Render the response on a new page
            return render_template("result.html", response=cleaned_response)

        except Exception as e:
            flash(f"Error during analysis: {e}")
            return redirect(url_for("index"))

    flash("Please upload a valid PDF file.")
    return redirect(url_for("index"))


# Main Function to Run the App
if __name__ == "__main__":
    app.run(debug=True)
