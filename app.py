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
    print(f"Job description: {job_description}")  # Debugging
    print(f"Resume text: {resume_text[:200]}")  # Debug first 200 characters

    # Extract single and multi-word keywords dynamically from the job description
    job_doc = nlp(job_description)
    single_word_keywords = [token.text.lower() for token in job_doc if token.is_alpha and not token.is_stop]
    multi_word_keywords = [" ".join(chunk.text.lower().split()) for chunk in job_doc.noun_chunks]

    # Combine all keywords
    all_keywords = set(single_word_keywords + multi_word_keywords)

    # Debug extracted keywords
    print(f"Single-Word Keywords: {single_word_keywords}")
    print(f"Multi-Word Keywords: {multi_word_keywords}")
    print(f"All Keywords: {all_keywords}")

    # Check keyword matches
    matched_keywords = [keyword for keyword in all_keywords if keyword in resume_text.lower()]
    missing_keywords = [keyword for keyword in all_keywords if keyword not in resume_text.lower()]

    # Scoring
    match_score = (len(matched_keywords) / len(all_keywords)) * 100 if all_keywords else 0

    return {
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "total_score": round(match_score, 2)
    }

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
    if not resume_text:
        return "Not available"
    return textstat.flesch_reading_ease(resume_text)

def generate_custom_tips(missing_keywords, formatting_issues):
    tips = []
    if missing_keywords:
        tips.append(f"Consider adding these keywords: {', '.join(missing_keywords)}")
    if formatting_issues:
        tips.extend(formatting_issues)
    if not tips:
        tips.append("Your resume is well-optimised!")
    return tips

def process_file(resume_file):
    if resume_file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(resume_file.stream)
        resume_text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    elif resume_file.filename.endswith('.docx'):
        doc = Document(resume_file.stream)
        resume_text = " ".join([para.text for para in doc.paragraphs])
    else:
        resume_text = ""
    print(f"Extracted Resume Text: {resume_text[:200]}")  # Debugging first 200 characters
    return resume_text

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse', methods=['POST'])
def analyse():
    resume_file = request.files['resume']
    job_description = request.form['job_description']

    # Process resume file
    resume_text = process_file(resume_file)

    # Perform analysis
    keyword_results = analyse_resume(resume_text, job_description)
    formatting_issues = check_formatting_issues(resume_text)
    readability_score = calculate_readability(resume_text)
    custom_tips = generate_custom_tips(keyword_results["missing_keywords"], formatting_issues)

    # Debugging response data
    print(f"Keyword Results: {keyword_results}")
    print(f"Formatting Issues: {formatting_issues}")
    print(f"Readability Score: {readability_score}")
    print(f"Custom Tips: {custom_tips}")

    # Return JSON response
    return jsonify({
        "keyword_results": keyword_results,
        "formatting_issues": formatting_issues,
        "readability_score": readability_score,
        "suggested_edits": custom_tips
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
