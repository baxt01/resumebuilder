from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from docx import Document
import PyPDF2
import spacy
import textstat

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model for authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    account_type = db.Column(db.String(50), default='free')  # 'free' or 'premium'
    analyses_left = db.Column(db.Integer, default=5)  # Limit for free users
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Resume analysis helper functions
def analyse_resume(resume_text, job_description):
    job_doc = nlp(job_description)
    must_have_keywords = [phrase.text.lower() for phrase in job_doc.ents]
    nice_to_have_keywords = ["HTML", "CSS", "critical thinking"]

    matched_must_have = [word for word in must_have_keywords if word.lower() in resume_text.lower()]
    matched_nice_to_have = [word for word in nice_to_have_keywords if word.lower() in resume_text.lower()]

    must_have_score = (len(matched_must_have) / len(must_have_keywords) * 70) if must_have_keywords else 0
    nice_to_have_score = (len(matched_nice_to_have) / len(nice_to_have_keywords) * 30) if nice_to_have_keywords else 0

    total_score = must_have_score + nice_to_have_score

    return {
        "matched_must_have": matched_must_have,
        "matched_nice_to_have": matched_nice_to_have,
        "total_score": round(total_score, 2),
    }

def check_action_verbs(resume_text):
    action_verbs = ["managed", "developed", "led", "implemented", "improved", "designed"]
    matched_verbs = [verb for verb in action_verbs if verb.lower() in resume_text.lower()]
    return matched_verbs

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

# User authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('register'))

        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('login'))

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', account_type=current_user.account_type, analyses_left=current_user.analyses_left)

# Resume analysis route
@app.route('/analyse', methods=['POST'])
@login_required
def analyse():
    if current_user.account_type == 'free' and current_user.analyses_left <= 0:
        return jsonify({"error": "You have reached your analysis limit. Upgrade to premium for unlimited access."})

    resume_file = request.files['resume']
    job_description = request.form['job_description']
    resume_text = process_file(resume_file)

    keyword_results = analyse_resume(resume_text, job_description)
    action_verbs = check_action_verbs(resume_text)

    if current_user.account_type == 'free':
        current_user.analyses_left -= 1
        db.session.commit()

    return jsonify({
        "keyword_results": keyword_results,
        "matched_verbs": action_verbs,
        "account_type": current_user.account_type,
        "analyses_left": current_user.analyses_left
    })

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
