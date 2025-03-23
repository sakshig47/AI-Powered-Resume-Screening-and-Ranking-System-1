import os
import pdfplumber
import spacy
import docx
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# Load NLP model
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_skills_experience(text):
    doc = nlp(text)
    skills, experience = [], []

    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT"]:
            skills.append(ent.text)
        if ent.label_ in ["DATE", "TIME"]:
            experience.append(ent.text)

    return list(set(skills)), list(set(experience))

def rank_resumes(resumes, job_description):
    job_doc = nlp(job_description)
    ranked = []

    for resume in resumes:
        resume_doc = nlp(resume["text"])
        similarity = job_doc.similarity(resume_doc)
        ranked.append((resume, similarity))

    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    job_description = request.form["job_description"]
    uploaded_files = request.files.getlist("resumes")

    resumes = []

    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            text = extract_text_from_pdf(file_path) if filename.endswith(".pdf") else extract_text_from_docx(file_path)
            skills, experience = extract_skills_experience(text)

            resumes.append({"name": filename, "text": text, "skills": skills, "experience": experience})

    ranked_resumes = rank_resumes(resumes, job_description)

    return jsonify([
        {
            "name": resume[0]["name"],
            "skills": resume[0]["skills"],
            "experience": resume[0]["experience"],
            "score": round(resume[1] * 100, 2),
        }
        for resume in ranked_resumes
    ])

if __name__ == "__main__":
    app.run(debug=True)
