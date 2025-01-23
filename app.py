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
def extract_phrases(doc):
    """Extract noun chunks and important phrases from a text."""
    return [chunk.text.lower() for chunk in doc.noun_chunks]

def analyse_resume(resume_text, job_description):
    # Process job description and resume with spaCy
    job_doc = nlp(job_description)
    resume_doc = nlp(resume_text)

    # Extract keywords and phrases
    job_keywords = set(token.text.lower() for token in job_doc if token.is_alpha and not token.is_stop)
    resume_keywords = set(token.text.lower() for token in resume_doc if token.is_alpha and not token.is_stop)

    job_phrases = set(extract_phrases(job_doc))
    resume_phrases = set(extract_phrases(resume_doc))

    # Skills and qualifications (example categories)
    skills = {"python", "teamwork", "project management", "html", "css", "critical thinking"}
    qualifications = {"bachelor's degree", "master's degree", "certification", "5+ years experience"}

    # Matched and missing elements
    matched_keywords = job_keywords & resume_keywords
    missing_keywords = job_keywords - resume_keywords

    matched_phrases = job_phrases & resume_phrases
    missing_phrases = job_phrases - resume_phrases

    matched_skills = skills & resume_keywords
    missing_skills = skills - resume_keywords

    matched_qualifications = qualifications & resume_keywords
    missing_qualifications = qualifications - resume_keywords

    # Scoring
    total_elements = len(job_keywords | job_phrases | skills | qualifications)
    matched_elements = len(matched_keywords | matched_phrases | matched_skills | matched_qualifications)
    total_score = (matched_elements / total_elements) * 100 if total_elements else 0

    # Suggested edits
    suggestions = []
    if missing_keywords:
        suggestions.append(f"Consider adding these keywords: {', '.join(missing_keywords)}.")
    if missing_phrases:
        suggestions.append(f"Incorporate these key phrases: {', '.join(missing_phrases)}.")
    if missing_skills:
        suggestions.append(f"Highlight these skills: {', '.join(missing_skills)}.")
    if missing_qualifications:
        suggestions.append(f"Mention these qualifications: {', '.join(missing_qualifications)}.")

    return {
        "matched_keywords": list(matched_keywords),
        "matched_phrases": list(matched_phrases),
        "matched_skills": list(matched_skills),
        "matched_qualifications": list(matched_qualifications),
        "missing_keywords": list(missing_keywords),
        "missing_phrases": list(missing_phrases),
        "missing_skills": list(missing_skills),
        "missing_qualifications": list(missing_qualifications),
        "total_score": round(total_score, 2),
        "suggestions": suggestions
    }

def process_file(resume_file):
    # Logic for extracting text from file (PDF or DOCX)
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
    # Retrieve resume and job description
    resume_file = request.files['resume']
    job_description = request.form['job_description']

    # Process resume file
    resume_text = process_file(resume_file)

    # Perform analysis
    analysis_results = analyse_resume(resume_text, job_description)

    # Return JSON response
    return jsonify(analysis_results)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
