import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fpdf import FPDF

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("AIzaSyCUnkK8IiXelG-myzZtlirk21yCYAyy9l0")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Streamlit UI
st.set_page_config(page_title="SmartResume Generator", layout="centered")

st.title("📄 SmartResume Generator")
st.subheader("Generate AI-powered professional resumes!")

# Form Inputs
profile_image = st.file_uploader("Upload Profile Picture (Optional, 1:1 aspect ratio recommended)", type=["png", "jpg", "jpeg"])
name = st.text_input("Full Name *")
email = st.text_input("Email Address *")
phone = st.text_input("Phone Number *")
linkedin = st.text_input("LinkedIn Profile URL")
github = st.text_input("GitHub Profile URL (if any)")
summary = st.text_area("Professional Summary (Optional, a brief 2-3 sentences)")
skills = st.text_area("Skills (comma-separated) *")
experience = st.text_area("Work Experience (Mention roles, duration, and responsibilities)")
education = st.text_area("Education Details (Include degrees and institutions) *")
certifications = st.text_area("Certifications (Comma-separated or newline for multiple)")
achievements = st.text_area("Achievements (List your key career highlights)")
projects = st.text_area("Projects (Describe key projects with technologies used)")
submit = st.button("Generate Resume")

# Function to generate resume using Gemini API
def generate_resume():
    formatted_skills = "\n- " + "\n- ".join(skills.split(","))  # Fix for f-string error
    
    prompt = f"""
    Generate a concise, professional resume with proper formatting:
    
    **Personal Details:**
    - Name: {name}
    - Email: {email}
    - Phone: {phone}
    - LinkedIn: {linkedin if linkedin else "N/A"}
    - GitHub: {github if github else "N/A"}

    **Professional Summary:**
    {summary if summary else "N/A"}

    **Skills:** {formatted_skills}

    **Work Experience:**
    {experience if experience else "N/A"}

    **Education:**
    {education}

    **Certifications:**
    {certifications if certifications else "N/A"}

    **Achievements:**
    {achievements if achievements else "N/A"}

    **Projects:**
    {projects if projects else "N/A"}

    Structure it professionally with clear headings and bullet points.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text if response else "Error: No response from Gemini API."
    except Exception as e:
        return f"Error: {str(e)}"

# Function to create a PDF file
def create_pdf(resume_text, profile_image):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set Title Font
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt="Resume", ln=True, align="C")
    pdf.ln(10)

    # Add profile image if uploaded
    if profile_image:
        image_path = "profile_image.jpg"
        with open(image_path, "wb") as f:
            f.write(profile_image.getbuffer())
        
        pdf.image(image_path, x=80, y=20, w=50, h=50)
        pdf.ln(60)

    # Set Font for Body
    pdf.set_font("Arial", size=12)

    # Format Resume Text with Section Titles
    sections = resume_text.split("\n\n")
    for section in sections:
        lines = section.split("\n")
        if lines:
            # Bold Section Title
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(200, 8, txt=lines[0], ln=True)
            pdf.ln(2)
            
            # Regular Font for Content
            pdf.set_font("Arial", size=12)
            for line in lines[1:]:
                pdf.multi_cell(0, 7, txt=line)
            pdf.ln(5)

    # Save PDF
    pdf_file = "generated_resume.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Display Resume
if submit:
    # Validate required fields
    if not name or not email or not phone or not skills or not education:
        st.error("⚠️ Please fill in all required fields marked with *!")
    else:
        with st.spinner("Generating Resume..."):
            resume_content = generate_resume()
            if resume_content.startswith("Error"):
                st.error(resume_content)
            else:
                st.subheader("📝 Your AI-Generated Resume:")
                st.write(resume_content)

                # Create PDF
                pdf_path = create_pdf(resume_content, profile_image)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📥 Download Resume as PDF",
                        data=pdf_file,
                        file_name="SmartResume.pdf",
                        mime="application/pdf"
                    )
