from flask import Flask, render_template, request
import re
import pdfplumber

app = Flask(__name__)

def clean_text(text):
    text = re.sub(r'[^a-zA-Z0-9 ]', ' ', text)
    return text.lower().split()

def extract_text(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                content = page.extract_text()
                if content:
                    text += content
    except:
        return ""
    return text

def analyze_resume(resume_text, job_desc):
    resume_words = set(clean_text(resume_text))
    job_words = set(clean_text(job_desc))

    important_keywords = {
        "python","java","c++","sql","flask","machine","learning",
        "data","analysis","project","team","communication"
    }

    matched = resume_words.intersection(job_words)
    keyword_match = resume_words.intersection(important_keywords)

    score = int((len(matched) / len(job_words)) * 100)

    if len(keyword_match) > 3:
        score += 10

    score = min(score, 100)

    missing = list(job_words - resume_words)

    suggestions = []

    if score >= 80:
        suggestions.append("Strong profile for this role")
    elif score >= 60:
        suggestions.append("Good match, minor improvements needed")
    else:
        suggestions.append("Improve resume by adding relevant skills")

    if len(missing) > 5:
        suggestions.append("Include more keywords from job description")

    if "project" not in resume_text.lower():
        suggestions.append("Add projects section")

    if "experience" not in resume_text.lower():
        suggestions.append("Mention internships or experience")

    if "skills" not in resume_text.lower():
        suggestions.append("Add technical skills clearly")

    return score, missing[:10], suggestions

@app.route('/', methods=['GET', 'POST'])
def index():
    score = None
    missing = []
    suggestions = []

    if request.method == 'POST':
        file = request.files['resume']
        job_desc = request.form['job_desc']

        if not file:
            return render_template('index.html',
                                   score=0,
                                   missing=[],
                                   suggestions=["Please upload a resume"])

        if not job_desc.strip():
            return render_template('index.html',
                                   score=0,
                                   missing=[],
                                   suggestions=["Please enter job description"])

        text = extract_text(file)

        if text.strip() == "":
            return render_template('index.html',
                                   score=0,
                                   missing=[],
                                   suggestions=["PDF not readable. Upload proper resume"])

        score, missing, suggestions = analyze_resume(text, job_desc)

    return render_template('index.html',
                           score=score,
                           missing=missing,
                           suggestions=suggestions)

if __name__ == '__main__':
    app.run(debug=True)