from flask import Flask, request, jsonify, render_template
import spacy
import re
from werkzeug.utils import secure_filename
import os
from docx import Document
import PyPDF2
import nltk
from nltk.corpus import stopwords

# Flask App Setup
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load NLP Model (SpaCy)
nlp = spacy.load("en_core_web_sm")
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Utility Functions
def extract_text_from_file(file_path):
    """Extracts text from .docx or .pdf files."""
    if file_path.endswith('.docx'):
        doc = Document(file_path)
        return " ".join([paragraph.text for paragraph in doc.paragraphs])
    elif file_path.endswith('.pdf'):
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    else:
        raise ValueError("Unsupported file format. Please upload a .docx or .pdf file.")

def keyword_matching(job_description, resume_text):
    """Matches keywords from job description to resume."""
    job_doc = nlp(job_description.lower())
    resume_doc = nlp(resume_text.lower())

    job_keywords = set([token.text for token in job_doc if token.is_alpha and token.text not in stop_words])
    resume_keywords = set([token.text for token in resume_doc if token.is_alpha and token.text not in stop_words])

    matched_keywords = job_keywords.intersection(resume_keywords)
    missing_keywords = job_keywords.difference(resume_keywords)

    return {
        "matched": list(matched_keywords),
        "missing": list(missing_keywords),
        "score": int(len(matched_keywords) / len(job_keywords) * 100) if job_keywords else 0
    }

def formatting_analysis(resume_text):
    """Analyses resume formatting for ATS compatibility."""
    issues = []

    # Check for common ATS issues
    if len(re.findall(r'[\u2022\u25E6\u25AA]', resume_text)) == 0:  # Bullet points
        issues.append("No bullet points detected. Use standard bullets to highlight achievements.")

    if len(re.findall(r'\[img\]|<img>', resume_text)) > 0:  # Images
        issues.append("Images detected. Remove them as ATS systems cannot parse images.")

    if len(re.findall(r'(\w+\s+){15,}', resume_text)) > 0:  # Long sentences
        issues.append("Long sentences detected. Break them into shorter, concise points.")

    return issues

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse', methods=['POST'])
def analyse_resume():
    if 'resume' not in request.files or 'job_description' not in request.form:
        return jsonify({"error": "Resume file and job description are required."}), 400

    # File and job description handling
    resume_file = request.files['resume']
    job_description = request.form['job_description']

    if resume_file.filename == '':
        return jsonify({"error": "No resume file selected."}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(resume_file.filename))
    resume_file.save(file_path)

    try:
        resume_text = extract_text_from_file(file_path)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Perform analysis
    keyword_results = keyword_matching(job_description, resume_text)
    formatting_results = formatting_analysis(resume_text)

    # Return results
    return jsonify({
        "keyword_results": keyword_results,
        "formatting_issues": formatting_results
    })

if __name__ == '__main__':
    app.run(debug=True)
