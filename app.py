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
