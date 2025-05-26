import streamlit as st
from fpdf import FPDF
from io import BytesIO
import re

# ----------  T E M P L A T E  ----------
TEMPLATE = """
Dear {hiring_manager},

I am writing to express my interest in the {job_title} position at {company_name}, as advertised on {platform}. With over three years of experience at Willis Towers Watson as a Senior Actuarial Analyst, I bring a solid foundation in pension valuation, regulatory reporting, and actuarial modeling across diverse markets including the US and China.

In my current role, I’ve managed valuations for over 15 Defined Benefit pension plans, ensured 100 % compliance in government reporting (Form 5500, Schedule SB), and mentored junior analysts on both data and regulatory processes. Having cleared four IFOA exams (CM1, CS1, CB1, CB2) and developed strong technical skills in Excel and R, I am now looking to broaden my exposure to life and general insurance through dynamic consultancy work.

I am particularly drawn to {company_name}'s reputation for {company_value}, which aligns with my own drive to grow within a forward‑thinking actuarial environment.

I have attached my résumé for your review and would welcome the opportunity to discuss how I can contribute to your team.

Best regards,  
Vratika Jodhani  
📍 Mumbai | 📧 vratikajodhani@gmail.com | 📞 +91 98878 38722  
🔗 https://www.linkedin.com/in/vratika-jodhani-4678661ab
"""

# ----------  H E L P E R S  ----------
UNICODE_MAP = {
    "’": "'", "‘": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "•": "*", "\u00a0": " ",
}

def clean_text(txt: str) -> str:
    """Replace characters unsupported by FPDF’s Latin‑1."""
    for bad, good in UNICODE_MAP.items():
        txt = txt.replace(bad, good)
    return txt

def extract_info(desc: str):
    """Very lightweight heuristics to pull title, company, keywords."""
    job_title = company_name = ""
    keywords = []

    for line in desc.splitlines():
        # Job title
        if not job_title and re.search(r"(?i)(job title|role)", line):
            job_title = line.split(":")[-1].strip()
        elif not job_title and line.istitle() and 1 < len(line.split()) <= 6:
            job_title = line.strip()

        # Company name after the word “at …”
        if not company_name:
            m = re.search(r"at\s+([A-Z][A-Za-z0-9 &\-]+)", line)
            if m:
                company_name = m.group(1).strip()

        # Grab a few longer lines as “values”
        if len(line.split()) > 5 and len(keywords) < 3:
            keywords.append(line.strip())

    if not job_title:
        job_title = "Actuarial Analyst"
    if not company_name:
        company_name = "Your Company"
    if not keywords:
        keywords = ["innovative actuarial services"]

    return job_title, company_name, ", ".join(keywords)


def create_pdf(letter: str) -> bytes:
    """Return a binary PDF (safe for st.download_button)."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in clean_text(letter).split("\n"):
        pdf.multi_cell(0, 10, line)

    buffer = BytesIO()
    pdf.output(buffer, "F")          # write into buffer in memory
    buffer.seek(0)
    return buffer.read()             # return raw bytes


# ----------  S T R E A M L I T  U I  ----------
st.set_page_config(page_title="Cover‑Letter Generator", layout="centered")
st.title("📄 Cover‑Letter Generator (Vratika Jodhani)")

st.subheader("🔍 (Optional) Paste Job Description")
job_desc = st.text_area(
    "Paste the LinkedIn (or other) job description text below "
    "to pre‑fill fields automatically:"
)

if st.button("Auto‑fill from Description") and job_desc.strip():
    jt, cn, cv = extract_info(job_desc)
    st.session_state["job_title"] = jt
    st.session_state["company_name"] = cn
    st.session_state["company_value"] = cv
    st.success("Fields auto‑filled. Review or edit as you like ↓")

# ----- Manual / pre‑filled inputs -----
st.subheader("✏️ Cover‑Letter Details")

hiring_manager = st.text_input(
    "Hiring‑manager name (or “Recruitment Team”):",
    value="Recruitment Team"
)
job_title = st.text_input(
    "Job title:",
    value=st.session_state.get("job_title", "")
)
company_name = st.text_input(
    "Company name:",
    value=st.session_state.get("company_name", "")
)
platform = st.text_input(
    "Platform / Source (e.g. LinkedIn):",
    value="LinkedIn"
)
company_value = st.text_area(
    "Company initiative / value:",
    value=st.session_state.get("company_value", "")
)

# ----------  G E N E R A T E  &  D O W N L O A D  ----------
if st.button("Generate Cover Letter"):
    letter = TEMPLATE.format(
        hiring_manager=hiring_manager,
        job_title=job_title,
        company_name=company_name,
        platform=platform,
        company_value=company_value,
    )

    st.subheader("📃 Preview")
    st.text_area("Generated letter (you can copy‑edit here too):",
                 letter, height=420)

    st.download_button(
        label="📥 Download as PDF",
        data=create_pdf(letter),          # bytes created inside session
        file_name="Vratika_Cover_Letter.pdf",
        mime="application/pdf",
    )
