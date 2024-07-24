# ATS Resume Expert

ATS Resume Expert is a web application built with Streamlit that allows users to upload resumes, receive feedback, and check the compatibility of their resumes with job descriptions. The application also supports user authentication and session management.

## Features

- User authentication (login and sign-up)
- Upload and manage resumes
- Evaluate resumes against job descriptions
- Provide professional feedback on resumes
- Check the percentage match of resumes with job descriptions

## Technologies Used

- Python
- Streamlit
- SQLite
- Google Generative AI (for generating feedback)
- PDF2Image (for processing PDF files)
- Streamlit Cookies Manager (for session management)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/ats-resume-expert.git
    cd ats-resume-expert
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your Google Generative AI API key:

    ```env
    GENAI_API_KEY=your_api_key_here
    ```

5. Set up the SQLite database:

    ```bash
    sqlite3 users.db < schema.sql
    ```

## Usage

1. Run the Streamlit app:

    ```bash
    streamlit run app.py
    ```

2. Open your web browser and go to `http://localhost:8501`.

3. Sign up for a new account or log in with an existing account.

4. Upload your resume (PDF format).

5. Enter the job description and choose to receive feedback or check the percentage match of your resume with the job description.

## File Structure

```plaintext
ats-resume-expert/
├── app.py                    # Main application script
├── session_manager.py        # Session management script
├── requirements.txt          # Required Python packages
├── schema.sql                # SQL schema for setting up the database
├── .env                      # Environment variables file
├── .gitignore                # Git ignore file
└── README.md                 # This README file
```
## Contributions
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
