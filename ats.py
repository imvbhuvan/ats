from dotenv import load_dotenv
load_dotenv()

import base64
import streamlit as st
import os
import io
import re
from PIL import Image 
import pdf2image
import pandas as pd
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Convert the PDF to images
        images = pdf2image.convert_from_bytes(uploaded_file.read())

        pdf_parts = []
        for i, page in enumerate(images):
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts.append({
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            })

        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

def extract_information_from_resume(response):
    text = response

    # Define regular expressions for each field
    name_pattern = re.compile(r'Name : (.+)', re.IGNORECASE)
    email_pattern = re.compile(r'Email : (.+)', re.IGNORECASE)
    contact_number_pattern = re.compile(r'Contact Number : (.+)', re.IGNORECASE)
    percentage_match_pattern = re.compile(r'Percentage Match : (.+)', re.IGNORECASE)

    # Extract information using regular expressions
    name_match = name_pattern.search(text)
    email_match = email_pattern.search(text)
    contact_number_match = contact_number_pattern.search(text)
    percentage_match_match = percentage_match_pattern.search(text)

    # Check if matches are found and extract values
    name = name_match.group(1) if name_match else None
    email = email_match.group(1) if email_match else None
    contact = contact_number_match.group(1) if contact_number_match else None
    percentage_match = percentage_match_match.group(1) if percentage_match_match else None

    return name, email, contact, percentage_match


input_prompt = """
You are a proficient ATS (Applicant Tracking System) scanner with extensive expertise in data science and ATS operations. Your objective is to assess resumes in comparison to the provided job description, focusing on extracting candidate information such as Name, email, and Contact number.

The candidate's name should follow the format of First name and Last name. The email should encompass various combinations of names with '@' and '.com' or any other domain name address. The contact number should adhere to the format of a country code starting with "+" followed by 10 digits.

Your task involves evaluating the job description against the resume, determining the percentage of match by comprehending the job requirements outlined in the description. Additionally, you need to assess the candidate's skills, experience, certificates, etc., to calculate the overall percentage match.

Present the output in the specified format:
Name:
Email:
Contact Number:
Percentage Match:

Ensure adherence to the prescribed output format without any deviation.
"""


# Streamlit App

st.set_page_config(page_title="Resume Parsing System", page_icon=":rocket:")

# Define header image
header_image_path = r"C:\Users\imvbh\Desktop\LLMs\ats\header.webp"
header_image = Image.open(header_image_path)
st.image(header_image, caption="Hello, Welcome to Resume Analyzer", use_column_width=True)
#st.set_page_config(page_title="Resume Parsing System")
st.header("Resume Parsing System 📃")

input_text = st.text_area("Job Description: ", key="input")
uploaded_files = st.file_uploader("Upload resumes (PDF)📄", type=["pdf"], accept_multiple_files=True)


if uploaded_files is not None:
    st.write(f"{len(uploaded_files)} PDFs Uploaded Successfully 🎉")

if st.button("Process Resumes 🚀"):
    if uploaded_files is not None:
        resume_data = []

        for file in uploaded_files:
            pdf_content = input_pdf_setup(file)
            response = get_gemini_response(input_text, pdf_content, input_prompt)
            name, email, contact_number, percentage_match = extract_information_from_resume(response)

            #print(response)

            resume_data.append({
                "Name": name,
                "Email": email,
                "Contact": contact_number,
                "Percentage Match": percentage_match
            })

        # Display the extracted data in the UI
        df_resume_data = pd.DataFrame(resume_data)
        st.subheader("Extracted Data from Resumes: ")
        st.write(df_resume_data)

        # Save the extracted data to an Excel file if an Excel file is provided
        df_resume_data.to_excel("Details.xlsx", index=False)
        st.success("The Resumes Data has been successfully saved to Details.xlsx 🎉")

    else:
        st.warning("Please upload one or more resumes.")

