import base64
import io
import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from PIL import Image
import pdf2image
import google.generativeai as genai
from werkzeug.security import generate_password_hash, check_password_hash

# Ensure this is called first
st.set_page_config(page_title="ATS Resume Expert")

# Import session management functions
from session_manager import set_session, clear_session, load_session

os.environ['PATH'] += os.pathsep + r'C:\Program Files (x86)\poppler\Library\bin'

genai.configure(api_key=os.getenv("GENAI_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

@st.cache_data
def input_pdf_setup(file_content):
    if file_content:
        try:
            images = pdf2image.convert_from_bytes(file_content)
            if not images:
                st.error("No images found in PDF file.")
                return None

            first_page = images[0]

            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode()
                }
            ]
            return pdf_parts
        except pdf2image.exceptions.PDFPageCountError as e:
            st.error("Error processing PDF file: " + str(e))
            return None
        except Exception as e:
            st.error("An unexpected error occurred: " + str(e))
            return None
    else:
        st.error("The uploaded PDF file is empty")
        return None

@st.cache_data
def get_resumes_from_db(user_id, offset=0, limit=10):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, file_name, uploaded_at FROM resumes WHERE user_id = ? LIMIT ? OFFSET ?", (user_id, limit, offset))
    resumes = c.fetchall()
    conn.close()
    return resumes

@st.cache_data
def get_resume_data_from_db(resume_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT file_name, file_data FROM resumes WHERE id = ?", (resume_id,))
    resume = c.fetchone()
    conn.close()
    return resume

def save_resume_to_db(user_id, file_name, file_data):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute("SELECT COUNT(*) FROM resumes WHERE user_id = ? AND file_name = ? AND file_data = ?", (user_id, file_name, file_data))
    count = c.fetchone()[0]
    
    if count == 0:
        c.execute("INSERT INTO resumes (user_id, file_name, file_data, uploaded_at) VALUES (?, ?, ?, ?)", 
                  (user_id, file_name, file_data, timestamp))
        conn.commit()
    conn.close()

def delete_resume_from_db(resume_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
    conn.commit()
    conn.close()

def create_user(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
        conn.commit()
        user_id = c.lastrowid
    except sqlite3.IntegrityError:
        user_id = None
    conn.close()
    return user_id

def authenticate_user(email, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    if user and check_password_hash(user[1], password):
        return user[0]
    else:
        return None

def handle_resume_action(selected_option, resume_options):
    if selected_option:
        selected_resume_id = resume_options.get(selected_option)
        if "Use" in selected_option:
            resume_data = get_resume_data_from_db(selected_resume_id)
            if resume_data:
                st.session_state['resume_data'] = input_pdf_setup(resume_data[1])
                st.write(f"Using resume: {selected_option}")
            else:
                st.error("Failed to load resume data.")

def load_more_resumes():
    st.session_state['resume_offset'] += 10
    st.experimental_rerun()

# Load session state
load_session()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

if 'email' not in st.session_state:
    st.session_state['email'] = ""

if 'resume_offset' not in st.session_state:
    st.session_state['resume_offset'] = 0

if st.session_state['logged_in']:
    menu = ["Logout"]
else:
    menu = ["Login", "Sign Up"]

choice = st.sidebar.selectbox("Menu", menu, key="menu_selectbox")

if choice == "Sign Up" and not st.session_state['logged_in']:
    st.subheader("Create New Account")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up", key="signup_button"):
        user_id = create_user(signup_email, signup_password)
        if user_id:
            st.success("You have successfully created an account")
        else:
            st.error("User already exists")

elif choice == "Login" and not st.session_state['logged_in']:
    st.subheader("Login")
    login_email = st.text_input("Email", key="login_email")
    login_password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_button"):
        user_id = authenticate_user(login_email, login_password)
        if user_id:
            set_session(user_id, login_email)
            st.experimental_rerun()
        else:
            st.error("Invalid email or password")

if st.session_state['logged_in']:
    st.write(f"Logged in as {st.session_state['email']}")
    if st.sidebar.button("Logout", key="logout_button"):
        clear_session()
        st.experimental_rerun()

    input_text = st.text_area("Job Description: ", key="input_text")
    uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], key="pdf_uploader")
    
    if uploaded_file is not None:
        file_content = uploaded_file.read()
        if file_content:
            save_resume_to_db(st.session_state['user_id'], uploaded_file.name, file_content)
            st.session_state['resume_data'] = input_pdf_setup(file_content)
            st.write("PDF Uploaded Successfully")
        else:
            st.error("Uploaded file is empty")
    
    resumes = get_resumes_from_db(st.session_state['user_id'], st.session_state['resume_offset'])

    if resumes:
        st.subheader("Previously Uploaded Resumes")
        for resume_id, file_name, uploaded_at in resumes:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"{file_name} (Uploaded At: {uploaded_at})")
            with col2:
                if st.button(f"Use", key=f"use_button_{resume_id}"):
                    resume_data = get_resume_data_from_db(resume_id)
                    if resume_data:
                        st.session_state['resume_data'] = input_pdf_setup(resume_data[1])
                        st.write(f"Using resume: {file_name}")
                    else:
                        st.error("Failed to load resume data.")
            with col3:
                if st.button(f"Delete", key=f"delete_button_{resume_id}"):
                    delete_resume_from_db(resume_id)
                    st.experimental_rerun()

        if st.button("Load More Resumes", key="load_more_button"):
            load_more_resumes()
    else:
        st.write("No resumes found.")

    if st.button("Tell me about my resume", key="tell_me_about_resume_button"):
        if 'resume_data' not in st.session_state:
            st.write("Please upload or load a resume first.")
        else:
            input_prompt1 = """
                You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
                Please share your professional evaluation on whether the candidate's profile aligns with the role. 
                Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
            """
            
            if st.session_state['resume_data']:
                response = get_gemini_response(input_text, st.session_state['resume_data'], input_prompt1)
                st.subheader("The response is: ")
                st.write(response)

    if st.button("Percentage match", key="percentage_match_button"):
        if 'resume_data' not in st.session_state:
            st.write("Please upload or load a resume first.")
        else:
            input_prompt2 = """
                You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
                your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
                the job description. First the output should come as percentage and then keywords missing and last final thoughts.
            """
            
            if st.session_state['resume_data']:
                response = get_gemini_response(input_text, st.session_state['resume_data'], input_prompt2)
                st.subheader("The response is: ")
                st.write(response)
else:
    st.subheader("Please log in to continue")
