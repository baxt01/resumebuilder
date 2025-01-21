from flask import Flask, request, jsonify, render_template
from docx import Document
import PyPDF2
import spacy
import textstat

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)

# Helper functions
def analyse_resume(resume_text, job_description):
    job_keywords = nlp(job_description)
    must_have_keywords = [token.text.lower() for token in job_keywords if token.is_alpha and not token.is_stop]
    nice_to_have_keywords = ["HTML", "CSS", "critical thinking"]

    matched_must_have = [word for word in must_have_keywords if word.lower() in resume_text.lower()]
    matched_nice_to_have = [word for word in nice_to_have_keywords if word.lower() in resume_text.lower()]

    must_have_score = (len(matched_must_have) / len(must_have_keywords)) * 70 if must_have_keywords else 0
    nice_to_have_score = (len(matched_nice_to_have) / len(nice_to_have_keywords)) * 30 if nice_to_have_keywords else 0

    total_score = must_have_score + nice_to_have_score

    return {
        "matched_must_have": matched_must_have,
        "missing_must_have": list(set(must_have_keywords) - set(matched_must_have)),
        "matched_nice_to_have": matched_nice_to_have,
        "total_score": round(total_score, 2)
    }

def suggest_rewritten_resume(resume_text, job_description):
    job_keywords = nlp(job_description)
    must_have_keywords = [token.text.lower() for token in job_keywords if token.is_alpha and not token.is_stop]
    missing_keywords = list(set(must_have_keywords) - set(word.lower() for word in resume_text.split()))
    
    # Rewriting suggestion
    suggestions = []
    for keyword in missing_keywords:
        suggestions.append(f"Consider adding a sentence using '{keyword}' to highlight your experience related to it.")

    rewritten_resume = resume_text
    if missing_keywords:
        rewritten_resume += "\n\nSuggested Additions:\n"
        for suggestion in suggestions:
            rewritten_resume += f"- {suggestion}\n"

    return rewritten_resume

def process_file(resume_file):
    if resume_file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(resume_file.stream)
        resume_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    elif resume_file.filename.endswith('.docx'):
        doc = Document(resume_file.stream)
        resume_text = " ".join([para.text for para in doc.paragraphs])
    else:
        resume_text = ""
    return resume_text

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse', methods=['POST'])
def analyse():
    resume_file = request.files['resume']
    job_description = request.form['job_description']

    resume_text = process_file(resume_file)

    keyword_results = analyse_resume(resume_text, job_description)
    rewritten_resume = suggest_rewritten_resume(resume_text, job_description)

    return jsonify({
        "keyword_results": keyword_results,
        "rewritten_resume": rewritten_resume
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
