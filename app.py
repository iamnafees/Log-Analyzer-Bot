import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import pandas as pd
import datetime
from fpdf import FPDF
from io import BytesIO

# --- Load API Key ---
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

# --- Page Config ---
st.set_page_config("🧠 Log Analyzer Assistant", layout="centered", page_icon="🧠")

# --- Custom CSS ---
st.markdown("""
    <style>
        html, body, .main {
            background-color: #f2d9d9;
        }
        .stApp { padding: 0; }
        h1, h2, h3, .markdown-text-container h1 {
            color: #1e3d59;
            font-family: 'Segoe UI', sans-serif;
        }
        .stButton button {
            background-color: #2ecc71;
            color: white;
            font-weight: bold;
            border-radius: 12px;
            padding: 10px 24px;
            font-size: 16px;
            transition: 0.3s ease;
        }
        .stButton button:hover {
            background-color: #27ae60;
        }
        .severity-box {
            padding: 20px;
            border-radius: 12px;
            color: white;
            text-align: center;
            margin-bottom: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .stTextInput > div > div > input,
        .stTextArea textarea {
            border-radius: 10px;
            border: 1px solid #ccc;
            padding: 10px;
            font-size: 16px;
            font-family: monospace;
        }
        .stRadio > div {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("🧠 Log Analyzer Bot")
st.markdown("Upload a `.log` file and I’ll analyze it like a friendly AI assistant.")

# --- Session State ---
if "step" not in st.session_state:
    st.session_state.step = 0
if "log_text" not in st.session_state:
    st.session_state.log_text = ""
if "filename" not in st.session_state:
    st.session_state.filename = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "user_question" not in st.session_state:
    st.session_state.user_question = ""
if "followup_response" not in st.session_state:
    st.session_state.followup_response = ""
if "feedback_saved" not in st.session_state:
    st.session_state.feedback_saved = False

# --- Upload File ---
st.subheader("📁 Upload Your Log File")
uploaded_file = st.file_uploader("Choose a `.log` file to analyze:", type=["log"])

if uploaded_file:
    log_text = uploaded_file.read().decode("utf-8")
    if uploaded_file.name != st.session_state.filename:
        st.session_state.log_text = log_text
        st.session_state.filename = uploaded_file.name
        st.session_state.step = 1
        st.rerun()

# --- Step 1: Preview ---
if st.session_state.step == 1:
    st.subheader("🔍 Log Preview")
    with st.expander("Click to preview log snippet"):
        st.text_area("Log Snippet", st.session_state.log_text[:3000], height=300)
    if st.button("✅ Yes, analyze it"):
        st.session_state.step = 2
        st.rerun()

# --- Utility Functions ---
def count_severity(log_text):
    levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
    return {lvl: log_text.upper().count(lvl) for lvl in levels}

def generate_prompt(log_text):
    return f"""
Hi Gemini! You're acting as a helpful log analysis assistant.

Please do the following:
1. Review the log for any errors, exceptions, or warnings.
2. Summarize the health of the system.
3. Mention any unusual patterns or repeating issues.
4. Suggest follow-up questions I can ask to dig deeper.

Speak like a friendly human assistant.

Here’s the log:
\"\"\"{log_text[:10000]}\"\"\"
"""

def ask_gemini(prompt):
    return model.generate_content(prompt).text.strip()

def clean_text(text):
    # Replace curly quotes and unsupported characters with plain ASCII
    return text.replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")

# --- Step 2: Analysis ---
if st.session_state.step == 2:
    st.subheader("🤖 Gemini Log Analysis")
    with st.spinner("Analyzing log..."):
        try:
            summary = ask_gemini(generate_prompt(st.session_state.log_text))
            st.session_state.summary = summary
            st.markdown(summary)
        except Exception as e:
            st.error("❌ Gemini API Error. Try again later.")
            st.exception(e)

    # --- Follow-up Question ---
    st.subheader("💬 Ask a Follow-up Question")
    st.markdown("Examples:\n- What caused the ERROR at 12:45?\n- Are there repeating issues?\n- Should I worry about these warnings?\n- What could be the possible root cause?")
    user_question = st.text_input("Ask me anything about the log:")

    if user_question:
        st.session_state.user_question = user_question
        follow_prompt = f"""
You're continuing the log analysis.

Log:
\"\"\"{st.session_state.log_text[:10000]}\"\"\"

User asked: {user_question}

Give a clear, human-friendly answer.
"""
        with st.spinner("Thinking..."):
            try:
                response = ask_gemini(follow_prompt)
                st.session_state.followup_response = response
                st.markdown(response)
            except Exception as e:
                st.error("❌ Gemini Error during follow-up.")
                st.exception(e)

    # --- PDF Export ---
    st.subheader("📥 Download Report")

    class PDF(FPDF):
        def chapter_title(self, title):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, title, ln=True, align="L")
            self.ln(5)

        def chapter_body(self, body):
            self.set_font("Arial", "", 12)
            self.multi_cell(0, 10, body)
            self.ln()

    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title("Gemini Log Analysis Summary")
    pdf.chapter_body(clean_text(st.session_state.summary))

    if st.session_state.user_question and st.session_state.followup_response:
        pdf.chapter_title(f"Follow-up: {st.session_state.user_question}")
        pdf.chapter_body(clean_text(st.session_state.followup_response))

    pdf_output = pdf.output(dest="S").encode("latin1")
    pdf_buffer = BytesIO(pdf_output)

    st.download_button(
        label="📥 Download Log Analysis as PDF",
        data=pdf_buffer,
        file_name="log_analysis_report.pdf",
        mime="application/pdf"
    )

    # --- Severity Breakdown ---
    st.subheader("📊 Severity Breakdown")
    severity = count_severity(st.session_state.log_text)
    colors = {
        "INFO": "#3498db", "WARNING": "#f39c12",
        "ERROR": "#e74c3c", "CRITICAL": "#8e44ad"
    }
    icons = {
        "INFO": "ℹ️", "WARNING": "⚠️",
        "ERROR": "❌", "CRITICAL": "🚨"
    }

    cols = st.columns(len(severity))
    for idx, level in enumerate(severity):
        with cols[idx]:
            st.markdown(f"""
            <div class="severity-box" style="background-color:{colors[level]}">
                <div style="font-size:32px;">{icons[level]}</div>
                <div style="font-size:20px; font-weight:600;">{level}</div>
                <div style="font-size:26px;">{severity[level]}</div>
            </div>
            """, unsafe_allow_html=True)

    # --- Feedback ---
    st.subheader("🗣️ Feedback")
    feedback = st.radio("Was this analysis helpful?", ("👍 Yes", "👎 No"))
    if feedback:
        feedback_df = pd.DataFrame([{
            "filename": uploaded_file.name,
            "timestamp": datetime.datetime.now(),
            "feedback": feedback
        }])
        feedback_df.to_csv("user_feedback.csv", mode="a", index=False, header=False)
        st.success("✅ Submitted feedback successfully. Thank you!")



