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
<<<<<<< HEAD
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

=======
def extract_keywords(job_description):
    # Process job description with spaCy
    doc = nlp(job_description)
    
    # Extract single-word keywords
    single_word_keywords = [token.text.lower() for token in doc if token.is_alpha and not token.is_stop]

    # Extract multi-word keywords (noun chunks)
    multi_word_keywords = [chunk.text.lower() for chunk in doc.noun_chunks]

    return single_word_keywords, multi_word_keywords

def analyse_resume(resume_text, job_description):
    single_word_keywords, multi_word_keywords = extract_keywords(job_description)
    
    # Check matches for single and multi-word keywords
    matched_single_words = [word for word in single_word_keywords if word in resume_text.lower()]
    matched_multi_words = [phrase for phrase in multi_word_keywords if phrase in resume_text.lower()]
    
    missing_single_words = list(set(single_word_keywords) - set(matched_single_words))
    missing_multi_words = list(set(multi_word_keywords) - set(matched_multi_words))

    # Calculate scores
    single_word_score = (len(matched_single_words) / len(single_word_keywords)) * 50 if single_word_keywords else 0
    multi_word_score = (len(matched_multi_words) / len(multi_word_keywords)) * 50 if multi_word_keywords else 0

    total_score = single_word_score + multi_word_score

    return {
        "matched_single_words": matched_single_words,
        "missing_single_words": missing_single_words,
        "matched_multi_words": matched_multi_words,
        "missing_multi_words": missing_multi_words,
        "total_score": round(total_score, 2)
    }

def suggest_rewritten_resume(resume_text, job_description):
    _, multi_word_keywords = extract_keywords(job_description)
    missing_multi_words = [phrase for phrase in multi_word_keywords if phrase not in resume_text.lower()]
    
    # Generate suggestions
    suggestions = []
    for phrase in missing_multi_words:
        suggestions.append(f"Consider adding a sentence to showcase your expertise in '{phrase}'.")

    rewritten_resume = resume_text
    if missing_multi_words:
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

>>>>>>> 5a29c812ec0755aafa36fd5ff75464ef95f9fd3b
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
<<<<<<< HEAD
    formatting_issues = check_formatting_issues(resume_text)
    readability_score = calculate_readability(resume_text)
    custom_tips = generate_custom_tips(keyword_results["missing_keywords"], formatting_issues)

    # Debugging response data
    print(f"Keyword Results: {keyword_results}")
    print(f"Formatting Issues: {formatting_issues}")
    print(f"Readability Score: {readability_score}")
    print(f"Custom Tips: {custom_tips}")
=======
    rewritten_resume = suggest_rewritten_resume(resume_text, job_description)
>>>>>>> 5a29c812ec0755aafa36fd5ff75464ef95f9fd3b

    return jsonify({
        "keyword_results": keyword_results,
<<<<<<< HEAD
        "formatting_issues": formatting_issues,
        "readability_score": readability_score,
        "suggested_edits": custom_tips
=======
        "rewritten_resume": rewritten_resume
>>>>>>> 5a29c812ec0755aafa36fd5ff75464ef95f9fd3b
    })

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
