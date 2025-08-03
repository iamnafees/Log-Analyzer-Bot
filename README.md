Project Documentation

Log Analyzer Bot

📌 Project Overview
The Log Analyzer Bot enables developers and support engineers to upload system .log files and receive intelligent summaries, issue detection, and severity-level breakdowns, powered by Google’s Gemini 1.5 Flash model.
It supports real-time analysis through a user-friendly Streamlit interface and allows follow-up questions for deeper insights. The tool also logs feedback to continuously improve quality and support audit trails.

🛠️ Technology Stack
Frontend/UI: Streamlit (Python-based UI)
Backend: Python
LLM Model: Gemini 1.5 Flash (via google-generativeai API)
Deployment: Localhost (via Streamlit, default port: 8501)

⚙️ System Workflow
Log Upload: User uploads a .log file via the Streamlit UI.

Log Preview: The first 3,000 characters of the log are shown for review.
Gemini Analysis: The AI model summarizes the log, detects issues, and recommends actions.
Follow-Up Chat: Users can ask follow-up questions (e.g., about specific errors or timestamps).
Download Report: A downloadable PDF report is generated with the AI summary and follow-up responses.
Severity Breakdown: Counts and visual display of INFO, WARNING, ERROR, and CRITICAL logs.
Feedback Collection: User indicates if the summary was helpful (Yes / No).
Logging: All interactions are saved in logs/user_feedback.csv.

🧠 LLM Model Used
Model: Gemini 1.5 Flash (Free-tier)
Provider: Google
API Library: google-generativeai (Python SDK)


📂 Input Formats Supported
.log files (uploaded via file uploader)
Up to 10,000 characters from the log are passed to Gemini for analysis

📝 Feedback Logging
Fields Captured:
Timestamp
Filename
User Feedback (Yes / No)
Storage Location:
logs/user_feedback.csv (new data is auto-appended)

Format Example:
pgsql
Copy
Edit
filename,timestamp,feedback
error_logs.log,2025-08-01 18:40:33,Yes
