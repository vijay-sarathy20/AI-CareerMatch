# 🤖 AI CareerMatch — AI-Powered Resume & Job Description Analyzer

AI CareerMatch is a Generative AI-powered career assistant that analyzes a candidate's resume against a target job description and provides personalized insights to improve job readiness.

The application uses Google Gemini to understand the resume and job requirements, identify skill gaps, suggest resume improvements, create a personalized learning roadmap, and generate interview preparation questions.

---

## 🚀 Project Overview

Job seekers often struggle to understand:

* How well their resume matches a specific job description
* Which skills they already have
* Which skills are missing
* Whether their existing experience is relevant to the role
* What they should improve in their resume
* What they should learn before applying
* How they can prepare for the interview

AI CareerMatch addresses these problems by combining **Generative AI, Resume Analysis, Skill Gap Analysis, Career Recommendations, and Interview Preparation** into a single application.

The user simply uploads their resume in PDF format and pastes a job description. The application then generates a personalized career analysis.

---

## ✨ Key Features

### 📄 1. Resume Analysis

Upload a resume in PDF format and extract the text automatically.

The application analyzes:

* Technical skills
* Soft skills
* Education
* Work experience
* Projects
* Certifications
* Relevant experience

---

### 🎯 2. Resume–Job Description Matching

The application compares the candidate's resume with the target job description and generates a career readiness score.

It identifies:

* Overall match score
* Matching skills
* Missing skills
* Relevant experience
* Areas requiring improvement

This helps candidates understand how closely their current profile aligns with a particular role.

---

### 🧠 3. Skill Gap Analysis

AI CareerMatch identifies the difference between the candidate's current skill set and the skills expected by the job description.

The analysis separates skills into:

* Skills already demonstrated
* Skills that are missing
* Skills that should be prioritized

This gives candidates a clearer direction for their preparation.

---

### 📝 4. Resume Coach

The Resume Coach analyzes the existing resume and provides suggestions to improve it for the target role.

It focuses on areas such as:

* Resume summary
* Skills section
* Project descriptions
* Experience descriptions
* Achievement statements
* Job-description alignment
* Keyword optimization

The goal is to make the resume more relevant and easier for recruiters and Applicant Tracking Systems (ATS) to understand.

---

### 🗺️ 5. Personalized Learning Roadmap

Based on the identified skill gaps, the application generates a personalized learning roadmap.

The roadmap includes:

* Skill/topic to learn
* Why the skill is important
* Recommended learning priority
* Practical learning direction
* Suggested projects or practice areas

This converts the analysis into an actionable learning plan.

---

### 🎤 6. Interview Coach

AI CareerMatch also provides interview preparation based on the target job role.

It can generate questions covering areas such as:

* Technical concepts
* Resume-based questions
* Project-related questions
* Job-specific questions
* Behavioral questions

The application also provides an interface to evaluate interview answers and receive AI-generated feedback.

---

### 📊 7. Career Readiness Dashboard

The application presents the analysis through an interactive dashboard.

It provides a quick overview of:

* Career readiness score
* Matching skills
* Missing skills
* Relevant experience
* Priority areas
* Recommended actions

This allows users to understand their profile at a glance.

---

### 📑 8. Downloadable Career Report

Users can generate a professional report containing their AI CareerMatch analysis.

The application supports:

* Downloadable PDF report
* Downloadable text report

The report can be used as a reference while preparing for a job application.

---

## 🔄 Application Workflow

```text
                 ┌──────────────────┐
                 │   Upload Resume   │
                 │       PDF         │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Extract Resume   │
                 │      Text        │
                 └────────┬─────────┘
                          │
                          │
                 ┌────────▼─────────┐
                 │ Paste Job        │
                 │ Description      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Google Gemini AI │
                 │     Analysis     │
                 └────────┬─────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
   Match Analysis    Skill Gap       Experience
                     Analysis          Analysis
          │               │                │
          └───────────────┼────────────────┘
                          │
                          ▼
              ┌──────────────────────┐
              │ Personalized Career  │
              │    Recommendations   │
              └──────────┬───────────┘
                         │
             ┌───────────┼────────────┐
             │           │            │
             ▼           ▼            ▼
        Resume Coach  Learning     Interview
                     Roadmap         Coach
             │           │            │
             └───────────┼────────────┘
                         │
                         ▼
                Downloadable Report
```

---

## 🛠️ Tech Stack

### Programming Language

* **Python**

### Frontend / Application

* **Streamlit**

### Generative AI

* **Google Gemini API**
* **Google GenAI Python SDK**

### PDF Processing

* **pypdf**

### Environment Management

* **python-dotenv**

### Report Generation

* **ReportLab**

### Development Tools

* Python
* Command Prompt
* Git
* GitHub

---

## 🧩 Architecture

The application follows a simple AI-powered pipeline:

```text
User
 │
 ├── Resume PDF
 │
 └── Job Description
          │
          ▼
   Resume Text Extraction
          │
          ▼
    Prompt Construction
          │
          ▼
      Gemini API
          │
          ▼
    AI Career Analysis
          │
          ├── Match Score
          ├── Matching Skills
          ├── Missing Skills
          ├── Experience Analysis
          ├── Resume Suggestions
          ├── Learning Recommendations
          └── Interview Preparation
          │
          ▼
    Streamlit Dashboard
          │
          ▼
    PDF / Text Report
```

---

## 📂 Project Structure

```text
AI-CareerMatch/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Files excluded from Git
│
├── .env                   # API key (local only - not uploaded)
│
└── venv/                  # Python virtual environment (not uploaded)
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-CareerMatch.git
```

Move into the project directory:

```bash
cd AI-CareerMatch
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 API Key Configuration

AI CareerMatch uses the **Google Gemini API** for Generative AI analysis.

Create a `.env` file in the project root directory:

```text
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your own Gemini API key.

### ⚠️ Security

**Never upload your `.env` file or API key to GitHub.**

The project uses `.gitignore` to prevent sensitive files from being committed.

Example `.gitignore`:

```text
venv/
.env
__pycache__/
*.pyc
.streamlit/
```

---

## ▶️ Running the Application

After activating the virtual environment and configuring the API key, run:

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 💡 Example Use Case

Imagine a candidate wants to apply for a:

**Data Scientist**

job.

The candidate uploads their resume and pastes the company's job description.

For example, the resume may contain:

```text
Python
SQL
Machine Learning
Pandas
TensorFlow
```

While the job description may require:

```text
Python
SQL
Machine Learning
Pandas
Power BI
AWS
Docker
```

AI CareerMatch can then identify:

### Matching Skills

```text
Python
SQL
Machine Learning
Pandas
```

### Skill Gaps

```text
Power BI
AWS
Docker
```

The candidate can then use the generated roadmap to prioritize learning and interview preparation.

---

## 🎯 Why This Project?

This project demonstrates how Generative AI can be applied to a practical career-development problem.

Instead of simply generating text, the application uses an LLM to:

1. Understand unstructured resume information
2. Understand job requirements
3. Compare candidate capabilities with job requirements
4. Identify skill gaps
5. Generate personalized recommendations
6. Create an actionable learning roadmap
7. Support interview preparation

---

## 🧠 Generative AI Concepts Used

This project demonstrates practical usage of Generative AI concepts including:

* Large Language Models (LLMs)
* Prompt Engineering
* Structured AI Output
* Resume Information Extraction
* Context-based Analysis
* Skill Gap Identification
* AI-generated Recommendations
* AI-based Interview Feedback
* LLM-powered Career Assistance

---

## 📈 Future Enhancements

Potential future improvements include:

* ATS resume score analysis
* Multiple job description comparison
* Resume rewriting with AI
* LinkedIn profile analysis
* Job recommendation system
* Job application tracking
* Interview voice analysis
* Integration with job portals
* Persistent user profiles
* Vector database / RAG-based career knowledge system
* Resume version management
* Skill progress tracking
* Advanced analytics dashboard

---

## 🔒 Privacy & Security

The application is designed to keep API credentials outside the source code.

Sensitive configuration such as the Gemini API key is stored in an environment file and excluded from Git using `.gitignore`.

Users should avoid uploading resumes containing unnecessary sensitive personal information.

---

## 📚 Learning Outcomes

Through this project, the following skills were practiced:

* Python application development
* Streamlit application development
* Generative AI integration
* Google Gemini API integration
* Prompt engineering
* PDF text extraction
* JSON-based AI response handling
* Environment variable management
* Report generation using Python
* Git and GitHub project management
* Building an end-to-end AI application

---

## 🚀 Project Status

**Status: Completed — Initial Version**

The current version includes:

* Resume PDF upload
* Job description input
* Gemini-powered resume analysis
* Career readiness scoring
* Matching skill identification
* Skill gap analysis
* Resume improvement suggestions
* Personalized learning roadmap
* Interview preparation
* Interview answer evaluation
* PDF report generation
* Text report generation
* Streamlit dashboard

---

## 👨‍💻 Author

**Vijay Sarathy K S**

Computer Science Engineering Graduate

Interested in:

* Data Science
* Artificial Intelligence
* Machine Learning
* Deep Learning
* Generative AI

---

## ⭐ If You Find This Project Useful

If you find this project interesting, consider giving the repository a ⭐ on GitHub.
