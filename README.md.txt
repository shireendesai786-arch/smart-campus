 Smart Campus Grievance Portal

An AI-powered web application built with Streamlit and Google Gemini LLM designed to streamline campus grievance reporting. The platform intelligent categorizes student complaints, extracts key metadata/location details, assesses urgency levels, and drafts formal escalation emails for prompt administrative action.

🌟 Key Features

📝 Natural Language Grievance Submission: Students can submit detailed complaints in plain language alongside optional location context.

🤖 Intelligent AI Analysis: Powered by Gemini LLM to automatically:

Classify issues into specific campus categories.

Assess urgency levels (Low, Medium, High, Critical).

Extract structured identifiers (Room numbers, Hostel blocks, Lab IDs, Wi-Fi nodes, Equipment IDs, etc.).

Recommend the correct administrative department and action plan.

🚨 Safety & Urgency Alerts: Displays immediate visual banners for critical safety hazards and flags vague complaints that require human review.

✉️ Automated Draft & Escalation: Generates a pre-formatted, editable formal escalation email tailored for the target department.

📤 Multiple Dispatch Methods:

Download complaint drafts locally as .txt files.

Open drafts directly in default desktop/mobile mail clients via mailto: links.

Transmit emails directly through configured SMTP servers.

📁 Project Structure

.
├── app.py                   # Main Streamlit web application entry point
├── config.py                # Configuration settings, API key retrieval & validations
├── schemas.py               # Pydantic data models & typing schemas
├── grievance_analyzer.py    # LLM integration & prompt engineering logic
├── email_service.py         # Email formatting, mailto generation & SMTP logic
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation


🚀 Quick Start

1. Prerequisites

Make sure you have Python 3.9+ installed on your system.

2. Clone the Repository

git clone https://github.com/your-username/smart-campus-grievance-portal.git
cd smart-campus-grievance-portal


3. Create a Virtual Environment & Install Dependencies

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt


4. Configure Environment Variables

Create a .env file in the root directory and add your credentials:

GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-2.5-flash

# Optional: SMTP Server Configuration (for direct email sending)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@domain.com
SMTP_PASSWORD=your_app_password


Note: If GEMINI_API_KEY is omitted from .env, you can also input it directly in the app's sidebar during runtime.

💻 Running the Application

Execute the following command to launch the Streamlit server:

streamlit run app.py


Open your browser and navigate to http://localhost:8501.

🛠️ Usage Workflow

Enter Credentials & Describe Issue: Fill in your student information and provide a detailed description of the grievance.

AI Analysis: Click Analyze Complaint with AI. The portal will classify the urgency, extract metadata (e.g., room numbers, Wi-Fi node IDs), and flag critical safety alerts if applicable.

Review Extracted Data: Inspect structured metrics, recommended authorities, and extracted location identifiers.

Action & Escalation: Edit the generated formal email draft, then download it, open it in your email client, or send it directly using the built-in SMTP engine.

📜 Dependencies

Streamlit — Web UI Framework

Google GenAI SDK — LLM integration

Pydantic — Structured data parsing & schemas

python-dotenv — Environment variable management

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.