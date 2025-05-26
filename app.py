import streamlit as st
from fpdf import FPDF
from io import BytesIO
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# --- TEMPLATE ---
template = """
Dear {hiring_manager},

I am writing to express my interest in the {job_title} position at {company_name}, as advertised on {platform}. With over three years of experience at Willis Towers Watson as a Senior Actuarial Analyst, I bring a solid foundation in pension valuation, regulatory reporting, and actuarial modeling across diverse markets including the US and China.

In my current role, I’ve managed valuations for over 15 Defined Benefit pension plans, ensured 100% compliance in government reporting (Form 5500, Schedule SB), and mentored junior analysts on both data and regulatory processes. Having cleared four IFOA exams (CM1, CS1, CB1, CB2) and developed strong technical skills in Excel and R, I am now looking to broaden my exposure to life and general insurance through dynamic consultancy work.

I am particularly drawn to {company_name}'s reputation for {company_value}, which aligns with my own drive to grow within a forward-thinking actuarial environment.

I have attached my resume for your review and would welcome the opportunity to discuss how I can contribute to your team.

Best regards,  
Vratika Jodhani  
📍 Mumbai | 📧 vratikajodhani@gmail.com | 📞 +91 98878 38722  
🔗 https://www.linkedin.com/in/vratika-jodhani-4678661ab
"""

# --- NLP Job Parsing ---
def extract_job_info(description):
    doc = nlp(description)

    job_title = ""
    company_name = ""
    keywords = []

    for ent in doc.ents:
        if ent.label_ == "ORG" and not company_name:
            company_name = ent.text

    # Heuristic: look for likely title from lines
    for line in description.splitlines():
        if "job title" in line.lower() or "role" in line.lower():
            job_title = line.split(":")[-1].strip()
        elif not job_title and line.istitle() and len(line.split()) <= 6:
            job_title = line.strip()

    keywords = [chunk.text for chunk in doc.noun_chunks][:5]
    return job_title, company_name, ", ".join(keywords)

# --- PDF Generation ---
def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.strip().split('\n'):
        pdf.multi_cell(0, 10, line)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- STREAMLIT UI ---
st.set_page_config(page_title="Cover Letter Generator", layout="centered")
st.title("📄 Cover Letter Generator (Vratika Jodhani)")

# Step 1: Job Description Parsing
st.subheader("🔍 Paste Job Description (Optional)")
job_desc = st.text_area("Paste the full job description from LinkedIn (or other sources):")

if st.button("Auto-Fill from Description") and job_desc.strip():
    job_title, company_name, company_value = extract_job_info(job_desc)
    st.session_state["job_title"] = job_title
    st.session_state["company_name"] = company_name
    st.session_state["company_value"] = company_value
    st.success("Fields below have been pre-filled based on the job description.")

# Step 2: Manual or Auto-Filled Inputs
st.subheader("✏️ Fill in Cover Letter Details")

hiring_manager = st.text_input("Hiring Manager's Name or 'Recruitment Team'", "Recruitment Team")
job_title = st.text_input("Job Title", st.session_state.get("job_title", ""))
company_name = st.text_input("Company Name", st.session_state.get("company_name", ""))
platform = st.text_input("Platform/Source (e.g., LinkedIn)", "LinkedIn")
company_value = st.text_area("Company Initiative/Value", st.session_state.get("company_value", ""))

# Step 3: Generate Cover Letter
if st.button("Generate Cover Letter"):
    letter = template.format(
        hiring_manager=hiring_manager,
        job_title=job_title,
        company_name=company_name,
        platform=platform,
        company_value=company_value
    )

    st.subheader("📃 Preview")
    st.text_area("Your Cover Letter:", letter, height=400)

    pdf_file = create_pdf(letter)
    st.download_button(
        label="📥 Download as PDF",
        data=pdf_file,
        file_name="Vratika_Cover_Letter.pdf",
        mime="application/pdf"
    )
