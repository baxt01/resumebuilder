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
        # Extract keywords (split by priority levels)
        must_have_keywords = ["teamwork", "Python", "project management"]  # Example
        nice_to_have_keywords = ["HTML", "CSS", "critical thinking"]  # Example

        # Check keyword matches
        matched_must_have = [word for word in must_have_keywords if word.lower() in resume_text.lower()]
        matched_nice_to_have = [word for word in nice_to_have_keywords if word.lower() in resume_text.lower()]

        # Scoring
        must_have_score = (len(matched_must_have) / len(must_have_keywords)) * 70  # 70% weight
        nice_to_have_score = (len(matched_nice_to_have) / len(nice_to_have_keywords)) * 30  # 30% weight

        total_score = must_have_score + nice_to_have_score

        # Format response
        return {
            "matched_must_have": matched_must_have,
            "matched_nice_to_have": matched_nice_to_have,
            "total_score": round(total_score, 2)
        }

def check_action_verbs(resume_text):
        action_verbs = ["managed", "developed", "led", "implemented", "improved", "designed"]
        matched_verbs = [verb for verb in action_verbs if verb.lower() in resume_text.lower()]
        return matched_verbs

def check_formatting_issues(resume_text):
        issues = []
        if "table" in resume_text.lower():
            issues.append("Contains tables that may not parse well.")
        if "image" in resume_text.lower():
            issues.append("Contains images which ATS systems cannot read.")
        if len(resume_text.split("\n")) < 5:
            issues.append("Too short; consider elaborating on experience.")
        return issues

def calculate_readability(resume_text):
        readability_score = textstat.flesch_reading_ease(resume_text)
        return readability_score

def generate_custom_tips(missing_keywords, formatting_issues):
        tips = []
        if missing_keywords:
            tips.append(f"Add these keywords: {', '.join(missing_keywords)}")
        if formatting_issues:
            tips.extend(formatting_issues)
        if not tips:
            tips.append("Your resume is well-optimised!")
        return tips

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
        keyword_results = analyse_resume(resume_text, job_description)
        action_verbs = check_action_verbs(resume_text)
        formatting_issues = check_formatting_issues(resume_text)
        readability_score = calculate_readability(resume_text)
        custom_tips = generate_custom_tips(keyword_results['matched_must_have'], formatting_issues)

        # Return JSON response
        return jsonify({
    "keyword_results": keyword_results,
    "matched_verbs": action_verbs,
    "formatting_issues": formatting_issues or [],
    "readability_score": readability_score,
    "tips": custom_tips
})

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


    # Run the app
if __name__ == '__main__':
    nlp = spacy.load("en_core_web_sm")
    app.run(debug=True)