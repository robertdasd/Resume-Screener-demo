
# 📥 Import Required Libraries
import os
import streamlit as st
import pdfplumber
from openai import OpenAI

# 🌐 Configure the Page
st.set_page_config(
    page_title="AI Resume Screening Assistant",
    page_icon="🤖",
    layout="wide"
)

# 🔑 Load the API Key safely
# In the cloud it comes from Streamlit Secrets.
# In Colab it comes from an environment variable.
try:
    API_KEY = st.secrets["KEY"]
except Exception:
    API_KEY = os.environ.get("KEY")

if not API_KEY:
    st.error("API key not found. Please add KEY to the secrets.")
    st.stop()

# 🎯 Application Title
st.title("🤖 AI Resume Screening Assistant")

st.write(
    "Upload a resume, enter a job description, and let AI analyze the candidate's suitability for the role."
)
st.divider()

# 📄 Resume Upload
st.header("📄 Upload Resume")

uploaded_resume = st.file_uploader(
    label="Choose a PDF Resume",
    type=["pdf"]
)

# 💼 Job Description
st.header("💼 Job Description")

job_description = st.text_area(
    label="Enter the Job Description",
    height=200,
    placeholder="Paste the job description here..."
)

# 🚀 Analyze Button
analyze_button = st.button(
    "🚀 Analyze Resume",
    use_container_width=True
)

# 📄 Function to Extract Text from a PDF Resume

def extract_resume_text(uploaded_resume):
    """
    Extracts text from an uploaded PDF resume.

    Parameters:
        uploaded_resume: Uploaded PDF file

    Returns:
        Extracted resume text as a string.
    """

    resume_text = ""

    with pdfplumber.open(uploaded_resume) as pdf:

        # Read each page of the PDF
        for page in pdf.pages:

            text = page.extract_text()

            # Ignore empty pages
            if text:
                resume_text += text + "\n"

    return resume_text

# 🤖 Function to Analyze Resume

def analyze_resume(resume_text, job_description):

    # Create the AI client
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

    # AI Model
    MODEL_NAME = "openrouter/free"

    # Create the prompt
    prompt = f"""
You are an experienced HR Recruiter.

Compare the following resume with the job description and generate a professional screening report.

Resume:
{resume_text}

Job Description:
{job_description}

Include the following sections:

1. Candidate Summary
2. Matching Skills
3. Missing Skills
4. Strengths
5. Areas for Improvement
6. Overall Recommendation
7. Suitability Score (out of 100)
"""

    # Send the request to the AI model
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Return the AI-generated report
    return response.choices[0].message.content

# 🚀 Analyze Resume

if analyze_button:

    # Check whether a resume has been uploaded
    if uploaded_resume is None:
        st.warning("⚠️ Please upload a resume.")
        st.stop()

    # Check whether a job description has been entered
    if not job_description.strip():
        st.warning("⚠️ Please enter the job description.")
        st.stop()

    # Display a loading message
    with st.spinner("🤖 Analyzing Resume..."):

        # Extract text from the uploaded resume
        resume_text = extract_resume_text(uploaded_resume)

        # Scanned PDFs have no readable text
        if not resume_text.strip():
            st.warning("⚠️ No text found in this PDF. It may be a scanned image. Please upload a text-based PDF.")
            st.stop()

        # Generate the AI report
        try:
            report = analyze_resume(resume_text, job_description)
        except Exception as e:
            st.error(f"⚠️ The AI service returned an error: {e}")
            st.stop()

    # Display the result
    st.success("✅ Resume Analysis Completed!")

    st.header("📊 Resume Screening Report")

    st.markdown(report)
