from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Resume Analyzer is running!"

if __name__ == "__main__":
    app.run(debug=True)

import spacy, pdfplumber, re

nlp = spacy.load("en_core_web_sm")

# Function to extract text from uploaded PDF
def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        all_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
        return all_text


def extract_info(text):
    doc = nlp(text)

    # Email & Phone
    email = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    phone = re.findall(r"\+?\d[\d -]{8,}\d", text)

    # Name from PERSON entities
    name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "N/A")

    # Skill matching from a known list
    skills_list = ['Python', 'JavaScript', 'Angular', 'Node', 'React', 'C++', 'SQL']
    skills = [skill for skill in skills_list if skill.lower() in text.lower()]

    return {
        "name": name,
        "email": email[0] if email else "N/A",
        "phone": phone[0] if phone else "N/A",
        "skills": skills
    }

@app.route("/analyze", methods=["POST"])
def analyze_resume():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    text = extract_text_from_pdf(file)
    info = extract_info(text)
    return jsonify(info)
