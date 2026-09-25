import streamlit as st
import os
import json
from datetime import datetime
from io import BytesIO

from pypdf import PdfReader
from dotenv import load_dotenv
from google import genai

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI CareerMatch",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    section[data-testid="stSidebar"] {
        padding-top: 1rem;
    }

    .main-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        letter-spacing: -1px;
    }

    .subtitle {
        font-size: 1.1rem;
        opacity: 0.70;
        margin-bottom: 1.8rem;
    }

    .hero-card {
        padding: 1.8rem;
        border-radius: 20px;
        border: 1px solid rgba(128,128,128,0.22);
        margin-bottom: 1.5rem;
    }

    .metric-card {
        padding: 1.3rem;
        border-radius: 18px;
        border: 1px solid rgba(128,128,128,0.22);
        min-height: 120px;
    }

    .metric-title {
        font-size: 0.9rem;
        opacity: 0.65;
    }

    .metric-value {
        font-size: 2.1rem;
        font-weight: 750;
        margin-top: 0.3rem;
    }

    .roadmap-card {
        padding: 1.4rem;
        border-radius: 18px;
        border: 1px solid rgba(128,128,128,0.22);
        margin-bottom: 1rem;
    }

    .skill-badge {
        display: inline-block;
        padding: 0.45rem 0.85rem;
        margin: 0.25rem;
        border-radius: 20px;
        border: 1px solid rgba(128,128,128,0.25);
        font-size: 0.9rem;
    }

    .score-number {
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        line-height: 1;
        margin-top: 0.5rem;
    }

    .score-label {
        text-align: center;
        opacity: 0.65;
        margin-bottom: 1rem;
    }

    .footer {
        text-align: center;
        opacity: 0.55;
        padding: 2rem 0 1rem 0;
        font-size: 0.85rem;
    }

    .section-caption {
        opacity: 0.65;
        font-size: 0.95rem;
        margin-bottom: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:

    st.error(
        "❌ GEMINI_API_KEY was not found. "
        "Please check your .env file."
    )

    st.stop()


# =========================================================
# GEMINI CLIENT
# =========================================================

client = genai.Client(
    api_key=api_key
)


# =========================================================
# SESSION STATE
# =========================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "job_description" not in st.session_state:
    st.session_state.job_description = ""

if "resume_improvement" not in st.session_state:
    st.session_state.resume_improvement = None

if "interview_feedback" not in st.session_state:
    st.session_state.interview_feedback = None

if "analysis_date" not in st.session_state:
    st.session_state.analysis_date = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_score(value):

    try:
        score = int(float(value))
    except:
        score = 0

    return max(
        0,
        min(score, 100)
    )


def extract_resume_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def parse_json_response(response_text):

    if not response_text:

        raise ValueError(
            "Gemini returned an empty response."
        )

    response_text = response_text.strip()

    if response_text.startswith("```json"):

        response_text = response_text[7:]

    elif response_text.startswith("```"):

        response_text = response_text[3:]

    if response_text.endswith("```"):

        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:

        return json.loads(response_text)

    except json.JSONDecodeError:

        start = response_text.find("{")
        end = response_text.rfind("}")

        if start != -1 and end != -1:

            json_text = response_text[
                start:end + 1
            ]

            return json.loads(json_text)

        raise ValueError(
            "Gemini returned malformed JSON."
        )


# =========================================================
# MAIN CAREER ANALYSIS
# =========================================================

def analyze_resume(
    resume_text,
    job_description
):

    prompt = f"""
You are an expert technical recruiter,
career advisor, resume analyst,
and learning roadmap planner.

Analyze the candidate's resume against
the target job description.

IMPORTANT RULES:

1. Use ONLY information present in the resume.
2. Do NOT invent skills, experience, education,
   projects, technologies, certifications,
   achievements, or numbers.
3. Identify skills that clearly match the JD.
4. Identify important JD requirements missing
   from the resume.
5. Identify relevant experience and projects.
6. Give practical resume suggestions.
7. Recommend learning areas based on skill gaps.
8. Create a practical learning roadmap.
9. Prioritize the roadmap according to job relevance.
10. Create a priority action plan.
11. Generate interview questions based on
    the resume and JD.
12. Match score must be between 0 and 100.
13. Base the score on:
    - Relevant skills
    - Relevant projects/experience
    - Required technologies
    - Education/certifications where relevant
    - Overall alignment with the JD
14. Do not give a high score merely because
    the candidate knows generic programming.
15. Return ONLY valid JSON.
16. Do NOT use Markdown.
17. Do NOT use code fences.

Return EXACTLY:

{{
    "match_score": 0,

    "matching_skills": [],

    "missing_skills": [],

    "relevant_experience": [],

    "resume_suggestions": [],

    "learning_recommendations": [],

    "priority_actions": [
        {{
            "priority": "High",
            "action": "",
            "reason": ""
        }}
    ],

    "learning_roadmap": [
        {{
            "stage": "Stage 1",
            "topic": "",
            "duration": "",
            "why": "",
            "topics_to_cover": [],
            "practice": ""
        }}
    ],

    "interview_questions": []
}}

RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# =========================================================
# RESUME COACH
# =========================================================

def improve_resume(
    resume_text,
    job_description
):

    prompt = f"""
You are an expert resume writer
and ATS optimization specialist.

Improve the candidate's resume
for the target job.

STRICT RULES:

1. Use ONLY information in the resume.
2. NEVER invent experience.
3. NEVER invent skills.
4. NEVER invent technologies.
5. NEVER invent achievements.
6. NEVER invent numbers.
7. Do not add technologies simply because
   they appear in the JD.
8. Preserve factual accuracy.
9. Improve wording, clarity, impact,
   and relevance.
10. Use strong action verbs.
11. Keep content concise and ATS-friendly.
12. Return ONLY valid JSON.
13. Do NOT use Markdown.
14. Do NOT use code fences.

Return EXACTLY:

{{
    "professional_summary": "",

    "improved_experience": [
        {{
            "original": "",
            "improved": "",
            "reason": ""
        }}
    ],

    "improved_projects": [
        {{
            "project": "",
            "original": "",
            "improved": "",
            "reason": ""
        }}
    ],

    "keywords_to_highlight": []
}}

RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# =========================================================
# INTERVIEW EVALUATOR
# =========================================================

def evaluate_interview_answer(
    question,
    answer,
    resume_text,
    job_description
):

    prompt = f"""
You are an expert technical interviewer
and career coach.

Evaluate the candidate's answer.

Evaluate:

1. Clarity
2. Technical depth
3. Relevance
4. Strengths
5. Areas for improvement
6. Better answer structure
7. One follow-up question

IMPORTANT:

Do not invent experience for the candidate.

Return ONLY valid JSON.

Return:

{{
    "clarity_score": 0,
    "technical_score": 0,
    "relevance_score": 0,

    "strengths": [],

    "improvements": [],

    "answer_structure": [],

    "follow_up_question": ""
}}

QUESTION:

{question}

CANDIDATE ANSWER:

{answer}

RESUME:

{resume_text}

JOB DESCRIPTION:

{job_description}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# =========================================================
# PDF REPORT
# =========================================================

def create_pdf_report():

    result = st.session_state.analysis

    score = safe_score(
        result.get("match_score", 0)
    )

    matching_skills = result.get(
        "matching_skills",
        []
    )

    missing_skills = result.get(
        "missing_skills",
        []
    )

    experiences = result.get(
        "relevant_experience",
        []
    )

    suggestions = result.get(
        "resume_suggestions",
        []
    )

    learning = result.get(
        "learning_recommendations",
        []
    )

    actions = result.get(
        "priority_actions",
        []
    )

    roadmap = result.get(
        "learning_roadmap",
        []
    )

    questions = result.get(
        "interview_questions",
        []
    )

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=15,
        leading=19,
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=5
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=12,
        textColor=colors.grey
    )

    story = []

    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "AI CareerMatch",
            title_style
        )
    )

    story.append(
        Paragraph(
            "Career Readiness & Job Match Report",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            datetime.now().strftime(
                "Generated on %d %B %Y at %I:%M %p"
            ),
            small_style
        )
    )

    story.append(
        Spacer(1, 12)
    )

    # -----------------------------------------------------
    # SCORE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "Career Match Score",
            heading_style
        )
    )

    score_table = Table(
        [
            [
                Paragraph(
                    f"<b>{score}%</b>",
                    ParagraphStyle(
                        "Score",
                        fontSize=28,
                        alignment=TA_CENTER
                    )
                ),
                Paragraph(
                    "Overall alignment between the candidate's "
                    "resume and the target job description.",
                    body_style
                )
            ]
        ],
        colWidths=[
            45 * mm,
            120 * mm
        ]
    )

    score_table.setStyle(
        TableStyle(
            [
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.8,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    10
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    12
                )
            ]
        )
    )

    story.append(
        score_table
    )

    story.append(
        Spacer(1, 10)
    )

    # -----------------------------------------------------
    # MATCHING SKILLS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "1. Matching Skills",
            heading_style
        )
    )

    if matching_skills:

        for skill in matching_skills:

            story.append(
                Paragraph(
                    f"• {skill}",
                    body_style
                )
            )

    else:

        story.append(
            Paragraph(
                "No matching skills identified.",
                body_style
            )
        )

    # -----------------------------------------------------
    # MISSING SKILLS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "2. Skill Gaps",
            heading_style
        )
    )

    if missing_skills:

        for skill in missing_skills:

            story.append(
                Paragraph(
                    f"• {skill}",
                    body_style
                )
            )

    else:

        story.append(
            Paragraph(
                "No major skill gaps identified.",
                body_style
            )
        )

    # -----------------------------------------------------
    # EXPERIENCE
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "3. Relevant Experience & Projects",
            heading_style
        )
    )

    if experiences:

        for item in experiences:

            story.append(
                Paragraph(
                    f"• {item}",
                    body_style
                )
            )

    else:

        story.append(
            Paragraph(
                "No relevant experience identified.",
                body_style
            )
        )

    # -----------------------------------------------------
    # RESUME SUGGESTIONS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "4. Resume Suggestions",
            heading_style
        )
    )

    if suggestions:

        for item in suggestions:

            story.append(
                Paragraph(
                    f"• {item}",
                    body_style
                )
            )

    # -----------------------------------------------------
    # LEARNING RECOMMENDATIONS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "5. Learning Recommendations",
            heading_style
        )
    )

    if learning:

        for item in learning:

            story.append(
                Paragraph(
                    f"• {item}",
                    body_style
                )
            )

    # -----------------------------------------------------
    # PRIORITY ACTION PLAN
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "6. Priority Action Plan",
            heading_style
        )
    )

    action_rows = [
        [
            Paragraph(
                "<b>Priority</b>",
                body_style
            ),
            Paragraph(
                "<b>Action</b>",
                body_style
            ),
            Paragraph(
                "<b>Reason</b>",
                body_style
            )
        ]
    ]

    for item in actions:

        action_rows.append(
            [
                Paragraph(
                    str(
                        item.get(
                            "priority",
                            "Medium"
                        )
                    ),
                    body_style
                ),
                Paragraph(
                    str(
                        item.get(
                            "action",
                            ""
                        )
                    ),
                    body_style
                ),
                Paragraph(
                    str(
                        item.get(
                            "reason",
                            ""
                        )
                    ),
                    body_style
                )
            ]
        )

    if len(action_rows) > 1:

        action_table = Table(
            action_rows,
            colWidths=[
                25 * mm,
                65 * mm,
                75 * mm
            ],
            repeatRows=1
        )

        action_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    )
                ]
            )
        )

        story.append(
            action_table
        )

    # -----------------------------------------------------
    # ROADMAP
    # -----------------------------------------------------

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "7. Personalized Learning Roadmap",
            heading_style
        )
    )

    for stage in roadmap:

        stage_name = stage.get(
            "stage",
            ""
        )

        topic = stage.get(
            "topic",
            ""
        )

        duration = stage.get(
            "duration",
            ""
        )

        why = stage.get(
            "why",
            ""
        )

        topics = stage.get(
            "topics_to_cover",
            []
        )

        practice = stage.get(
            "practice",
            ""
        )

        roadmap_content = []

        roadmap_content.append(
            Paragraph(
                f"<b>{stage_name} — {topic}</b>",
                body_style
            )
        )

        roadmap_content.append(
            Paragraph(
                f"<b>Duration:</b> {duration}",
                body_style
            )
        )

        roadmap_content.append(
            Paragraph(
                f"<b>Why:</b> {why}",
                body_style
            )
        )

        if topics:

            roadmap_content.append(
                Paragraph(
                    "<b>Topics to Cover:</b>",
                    body_style
                )
            )

            for topic_item in topics:

                roadmap_content.append(
                    Paragraph(
                        f"• {topic_item}",
                        body_style
                    )
                )

        if practice:

            roadmap_content.append(
                Paragraph(
                    f"<b>Practice:</b> {practice}",
                    body_style
                )
            )

        roadmap_table = Table(
            [[roadmap_content]],
            colWidths=[
                165 * mm
            ]
        )

        roadmap_table.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.7,
                        colors.grey
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        10
                    )
                ]
            )
        )

        story.append(
            KeepTogether(
                roadmap_table
            )
        )

        story.append(
            Spacer(1, 10)
        )

    # -----------------------------------------------------
    # INTERVIEW QUESTIONS
    # -----------------------------------------------------

    story.append(
        Paragraph(
            "8. Interview Preparation",
            heading_style
        )
    )

    for i, question in enumerate(
        questions,
        1
    ):

        story.append(
            Paragraph(
                f"<b>{i}.</b> {question}",
                body_style
            )
        )

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Generated by AI CareerMatch",
            small_style
        )
    )

    doc.build(
        story
    )

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# TEXT REPORT
# =========================================================

def generate_report_text():

    result = st.session_state.analysis

    score = safe_score(
        result.get(
            "match_score",
            0
        )
    )

    matching_skills = result.get(
        "matching_skills",
        []
    )

    missing_skills = result.get(
        "missing_skills",
        []
    )

    experiences = result.get(
        "relevant_experience",
        []
    )

    suggestions = result.get(
        "resume_suggestions",
        []
    )

    learning = result.get(
        "learning_recommendations",
        []
    )

    actions = result.get(
        "priority_actions",
        []
    )

    roadmap = result.get(
        "learning_roadmap",
        []
    )

    questions = result.get(
        "interview_questions",
        []
    )

    report = []

    report.append(
        "AI CAREERMATCH — CAREER READINESS REPORT"
    )

    report.append(
        "=" * 55
    )

    report.append(
        f"Generated: "
        f"{datetime.now().strftime('%d %B %Y, %I:%M %p')}"
    )

    report.append("")

    report.append(
        "1. CAREER MATCH"
    )

    report.append(
        "-" * 30
    )

    report.append(
        f"Overall Match Score: {score}%"
    )

    report.append("")

    report.append(
        "2. MATCHING SKILLS"
    )

    report.append(
        "-" * 30
    )

    for skill in matching_skills:

        report.append(
            f"✓ {skill}"
        )

    report.append("")

    report.append(
        "3. SKILL GAPS"
    )

    report.append(
        "-" * 30
    )

    for skill in missing_skills:

        report.append(
            f"⚠ {skill}"
        )

    report.append("")

    report.append(
        "4. RELEVANT EXPERIENCE & PROJECTS"
    )

    report.append(
        "-" * 30
    )

    for item in experiences:

        report.append(
            f"• {item}"
        )

    report.append("")

    report.append(
        "5. RESUME SUGGESTIONS"
    )

    report.append(
        "-" * 30
    )

    for item in suggestions:

        report.append(
            f"• {item}"
        )

    report.append("")

    report.append(
        "6. LEARNING RECOMMENDATIONS"
    )

    report.append(
        "-" * 30
    )

    for item in learning:

        report.append(
            f"• {item}"
        )

    report.append("")

    report.append(
        "7. PRIORITY ACTION PLAN"
    )

    report.append(
        "-" * 30
    )

    for item in actions:

        report.append(
            f"[{item.get('priority', 'Medium')}] "
            f"{item.get('action', '')}"
        )

        report.append(
            f"Reason: {item.get('reason', '')}"
        )

        report.append("")

    report.append(
        "8. PERSONALIZED LEARNING ROADMAP"
    )

    report.append(
        "-" * 30
    )

    for stage in roadmap:

        report.append(
            f"{stage.get('stage', '')}: "
            f"{stage.get('topic', '')}"
        )

        report.append(
            f"Duration: {stage.get('duration', '')}"
        )

        report.append(
            f"Why: {stage.get('why', '')}"
        )

        report.append(
            "Topics:"
        )

        for topic in stage.get(
            "topics_to_cover",
            []
        ):

            report.append(
                f"  • {topic}"
            )

        report.append(
            f"Practice: {stage.get('practice', '')}"
        )

        report.append("")

    report.append(
        "9. INTERVIEW QUESTIONS"
    )

    report.append(
        "-" * 30
    )

    for i, question in enumerate(
        questions,
        1
    ):

        report.append(
            f"{i}. {question}"
        )

    report.append("")

    report.append(
        "=" * 55
    )

    report.append(
        "Generated by AI CareerMatch"
    )

    return "\n".join(
        report
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "## 🎯 AI CareerMatch"
    )

    st.caption(
        "Your AI-powered career copilot"
    )

    st.divider()

    if st.session_state.analysis is not None:

        st.markdown(
            "### 📌 Navigation"
        )

        page = st.radio(
            "Go to",
            [
                "📊 Dashboard",
                "🧩 Skill Analysis",
                "🗺️ Career Roadmap",
                "📝 Resume Coach",
                "🎤 Interview Coach",
                "📄 Career Report"
            ]
        )

    else:

        page = "📊 Dashboard"

    st.divider()

    if st.session_state.analysis is not None:

        score = safe_score(
            st.session_state.analysis.get(
                "match_score",
                0
            )
        )

        st.markdown(
            "### 🎯 Career Readiness"
        )

        st.progress(
            score / 100
        )

        st.metric(
            "Match Score",
            f"{score}%"
        )

    st.divider()

    st.caption(
        "🔐 Gemini API key is stored locally "
        "in your .env file."
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🎯 AI CareerMatch</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your AI-powered Resume Analyzer, Career Coach, '
    'Learning Planner & Interview Coach.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# INPUT AREA
# =========================================================

if st.session_state.analysis is None:

    st.markdown(
        """
        <div class="hero-card">

        <h3>🚀 Start Your Career Analysis</h3>

        <p>
        Upload your resume and paste a target job description.
        AI CareerMatch will analyze your profile and create a
        personalized career action plan.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    input_col1, input_col2 = st.columns(
        2
    )

    with input_col1:

        st.markdown(
            "### 📄 Resume"
        )

        uploaded_file = st.file_uploader(
            "Upload a PDF resume",
            type=["pdf"]
        )

    with input_col2:

        st.markdown(
            "### 💼 Target Job"
        )

        job_description_input = st.text_area(
            "Paste the job description",
            height=220,
            placeholder=(
                "Paste the complete job description here..."
            )
        )

    st.write("")

    analyze_button = st.button(
        "🚀 Analyze My Career Match",
        type="primary",
        use_container_width=True
    )

    if analyze_button:

        if uploaded_file is None:

            st.warning(
                "⚠️ Please upload your resume PDF."
            )

            st.stop()

        if not job_description_input.strip():

            st.warning(
                "⚠️ Please paste the job description."
            )

            st.stop()

        # -------------------------------------------------
        # READ PDF
        # -------------------------------------------------

        with st.spinner(
            "📄 Reading your resume..."
        ):

            try:

                resume_text = extract_resume_text(
                    uploaded_file
                )

            except Exception as e:

                st.error(
                    f"❌ Could not read the PDF:\n\n{str(e)}"
                )

                st.stop()

        if not resume_text:

            st.error(
                "❌ No readable text was found in the PDF."
            )

            st.stop()

        # -------------------------------------------------
        # AI ANALYSIS
        # -------------------------------------------------

        with st.spinner(
            "🤖 Gemini is analyzing your career profile..."
        ):

            try:

                response_text = analyze_resume(
                    resume_text,
                    job_description_input
                )

                result = parse_json_response(
                    response_text
                )

            except Exception as e:

                st.error(
                    "❌ AI analysis failed."
                )

                st.code(
                    str(e)
                )

                st.stop()

        # -------------------------------------------------
        # SAVE STATE
        # -------------------------------------------------

        st.session_state.analysis = result

        st.session_state.resume_text = (
            resume_text
        )

        st.session_state.job_description = (
            job_description_input
        )

        st.session_state.resume_improvement = None

        st.session_state.interview_feedback = None

        st.session_state.analysis_date = (
            datetime.now()
        )

        st.success(
            "✅ Career analysis completed!"
        )

        st.rerun()


# =========================================================
# NO ANALYSIS SCREEN
# =========================================================

if st.session_state.analysis is None:

    st.info(
        """
        👋 Welcome!

        Upload your resume and paste a target job description
        to discover how well your profile matches the role.
        """
    )

    feature_col1, feature_col2, feature_col3 = st.columns(
        3
    )

    with feature_col1:

        st.markdown(
            """
            ### 🎯 Match Analysis

            Compare your existing profile
            against the target role.
            """
        )

    with feature_col2:

        st.markdown(
            """
            ### 🗺️ Career Roadmap

            Get a personalized learning path
            based on your skill gaps.
            """
        )

    with feature_col3:

        st.markdown(
            """
            ### 🎤 Interview Coach

            Practice role-specific questions
            and receive AI feedback.
            """
        )

    st.stop()


# =========================================================
# GET ANALYSIS
# =========================================================

result = st.session_state.analysis


# =========================================================
# SCORE
# =========================================================

score = safe_score(
    result.get(
        "match_score",
        0
    )
)


# =========================================================
# DASHBOARD
# =========================================================

if page == "📊 Dashboard":

    st.header(
        "📊 Career Readiness Dashboard"
    )

    st.caption(
        "Your AI-generated overview for the target role."
    )

    matching_skills = result.get(
        "matching_skills",
        []
    )

    missing_skills = result.get(
        "missing_skills",
        []
    )

    questions = result.get(
        "interview_questions",
        []
    )

    experiences = result.get(
        "relevant_experience",
        []
    )

    # -----------------------------------------------------
    # TOP METRICS
    # -----------------------------------------------------

    metric1, metric2, metric3, metric4 = st.columns(
        4
    )

    with metric1:

        st.metric(
            "🎯 Match Score",
            f"{score}%"
        )

    with metric2:

        st.metric(
            "✅ Matching Skills",
            len(matching_skills)
        )

    with metric3:

        st.metric(
            "⚠️ Skill Gaps",
            len(missing_skills)
        )

    with metric4:

        st.metric(
            "🎤 Interview Questions",
            len(questions)
        )

    st.divider()

    # -----------------------------------------------------
    # SCORE AREA
    # -----------------------------------------------------

    score_left, score_right = st.columns(
        [1, 2]
    )

    with score_left:

        st.markdown(
            '<div class="score-number">'
            f'{score}%'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="score-label">'
            'Overall Career Match'
            '</div>',
            unsafe_allow_html=True
        )

    with score_right:

        st.subheader(
            "📈 Career Readiness"
        )

        st.progress(
            score / 100
        )

        if score >= 80:

            st.success(
                "Your profile shows strong alignment "
                "with the target role."
            )

        elif score >= 60:

            st.warning(
                "You have a reasonable foundation, "
                "but some areas need strengthening."
            )

        else:

            st.error(
                "Several important requirements "
                "need attention."
            )

    st.divider()

    # -----------------------------------------------------
    # STRENGTHS & GAPS
    # -----------------------------------------------------

    left, right = st.columns(
        2
    )

    with left:

        st.subheader(
            "✅ Your Strengths"
        )

        if matching_skills:

            for skill in matching_skills:

                st.success(
                    f"✓ {skill}"
                )

        else:

            st.info(
                "No matching skills identified."
            )

    with right:

        st.subheader(
            "⚠️ Focus Areas"
        )

        if missing_skills:

            for skill in missing_skills:

                st.warning(
                    f"⚠ {skill}"
                )

        else:

            st.success(
                "No major skill gaps identified."
            )

    st.divider()

    # -----------------------------------------------------
    # EXPERIENCE
    # -----------------------------------------------------

    st.subheader(
        "💼 Relevant Experience & Projects"
    )

    if experiences:

        for item in experiences:

            st.markdown(
                f"🔹 {item}"
            )

    else:

        st.info(
            "No relevant experience identified."
        )

    # -----------------------------------------------------
    # ACTION PLAN
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "🚀 Your Next Actions"
    )

    actions = result.get(
        "priority_actions",
        []
    )

    if actions:

        for action in actions[:6]:

            priority = str(
                action.get(
                    "priority",
                    "Medium"
                )
            )

            action_text = action.get(
                "action",
                ""
            )

            reason = action.get(
                "reason",
                ""
            )

            if priority.lower() == "high":

                st.error(
                    f"🔴 **HIGH** — {action_text}\n\n"
                    f"{reason}"
                )

            elif priority.lower() == "medium":

                st.warning(
                    f"🟠 **MEDIUM** — {action_text}\n\n"
                    f"{reason}"
                )

            else:

                st.info(
                    f"🟢 **LOW** — {action_text}\n\n"
                    f"{reason}"
                )


# =========================================================
# SKILL ANALYSIS
# =========================================================

elif page == "🧩 Skill Analysis":

    st.header(
        "🧩 Skill Gap Analysis"
    )

    st.caption(
        "Understand what you already have versus "
        "what the target role requires."
    )

    matching_skills = result.get(
        "matching_skills",
        []
    )

    missing_skills = result.get(
        "missing_skills",
        []
    )

    col1, col2 = st.columns(
        2
    )

    with col1:

        st.metric(
            "✅ Matching Skills",
            len(matching_skills)
        )

    with col2:

        st.metric(
            "⚠️ Missing Skills",
            len(missing_skills)
        )

    st.divider()

    st.subheader(
        "✅ Skills You Already Have"
    )

    if matching_skills:

        skill_columns = st.columns(
            3
        )

        for i, skill in enumerate(
            matching_skills
        ):

            with skill_columns[
                i % 3
            ]:

                st.success(
                    f"✓ {skill}"
                )

    else:

        st.info(
            "No matching skills identified."
        )

    st.divider()

    st.subheader(
        "⚠️ Skills You Need to Develop"
    )

    if missing_skills:

        skill_columns = st.columns(
            3
        )

        for i, skill in enumerate(
            missing_skills
        ):

            with skill_columns[
                i % 3
            ]:

                st.error(
                    f"⚠ {skill}"
                )

    else:

        st.success(
            "No major skill gaps identified."
        )

    st.divider()

    st.subheader(
        "💼 Relevant Experience & Projects"
    )

    experiences = result.get(
        "relevant_experience",
        []
    )

    if experiences:

        for item in experiences:

            st.markdown(
                f"🔹 {item}"
            )

    else:

        st.info(
            "No relevant experience identified."
        )

    st.divider()

    st.subheader(
        "📝 Resume Suggestions"
    )

    suggestions = result.get(
        "resume_suggestions",
        []
    )

    if suggestions:

        for item in suggestions:

            st.markdown(
                f"💡 {item}"
            )

    else:

        st.info(
            "No resume suggestions generated."
        )


# =========================================================
# CAREER ROADMAP
# =========================================================

elif page == "🗺️ Career Roadmap":

    st.header(
        "🗺️ Personalized Career Roadmap"
    )

    st.caption(
        "A learning path generated from the gap between "
        "your current profile and target role."
    )

    st.subheader(
        "📚 Recommended Learning"
    )

    learning = result.get(
        "learning_recommendations",
        []
    )

    for item in learning:

        st.markdown(
            f"📌 {item}"
        )

    st.divider()

    roadmap = result.get(
        "learning_roadmap",
        []
    )

    if roadmap:

        for i, stage in enumerate(
            roadmap,
            1
        ):

            stage_name = stage.get(
                "stage",
                f"Stage {i}"
            )

            topic = stage.get(
                "topic",
                "Learning Topic"
            )

            duration = stage.get(
                "duration",
                "Not specified"
            )

            why = stage.get(
                "why",
                ""
            )

            topics = stage.get(
                "topics_to_cover",
                []
            )

            practice = stage.get(
                "practice",
                ""
            )

            with st.expander(
                f"🚀 {stage_name} — {topic} | ⏱️ {duration}",
                expanded=(i == 1)
            ):

                st.markdown(
                    f"### {topic}"
                )

                st.markdown(
                    f"**⏱️ Estimated Duration:** {duration}"
                )

                st.markdown(
                    f"**🎯 Why this matters:** {why}"
                )

                if topics:

                    st.markdown(
                        "#### 📖 Topics to Cover"
                    )

                    for topic_item in topics:

                        st.markdown(
                            f"• {topic_item}"
                        )

                if practice:

                    st.markdown(
                        "#### 🛠️ Practical Work"
                    )

                    st.info(
                        practice
                    )

    else:

        st.info(
            "No personalized roadmap generated."
        )


# =========================================================
# RESUME COACH
# =========================================================

elif page == "📝 Resume Coach":

    st.header(
        "📝 AI Resume Coach"
    )

    st.caption(
        "Improve your resume while keeping every claim "
        "factually grounded in your original resume."
    )

    if st.session_state.resume_improvement is None:

        st.info(
            """
            The AI will:

            • Improve your professional summary
            • Rewrite relevant experience
            • Improve project descriptions
            • Identify useful keywords

            It will NOT invent experience, skills,
            technologies, achievements, or numbers.
            """
        )

        if st.button(
            "✨ Improve My Resume",
            type="primary",
            use_container_width=True
        ):

            with st.spinner(
                "🤖 AI is improving your resume..."
            ):

                try:

                    response = improve_resume(
                        st.session_state.resume_text,
                        st.session_state.job_description
                    )

                    improved = parse_json_response(
                        response
                    )

                    st.session_state.resume_improvement = (
                        improved
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "❌ Resume improvement failed."
                    )

                    st.code(
                        str(e)
                    )

    if st.session_state.resume_improvement is not None:

        improved = (
            st.session_state.resume_improvement
        )

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        st.subheader(
            "👤 Improved Professional Summary"
        )

        summary = improved.get(
            "professional_summary",
            ""
        )

        if summary:

            st.info(
                summary
            )

        # -------------------------------------------------
        # EXPERIENCE
        # -------------------------------------------------

        st.subheader(
            "💼 Improved Experience"
        )

        experience = improved.get(
            "improved_experience",
            []
        )

        for i, item in enumerate(
            experience,
            1
        ):

            with st.expander(
                f"Experience Improvement {i}"
            ):

                st.markdown(
                    "**Original**"
                )

                st.write(
                    item.get(
                        "original",
                        ""
                    )
                )

                st.markdown(
                    "**✨ Improved**"
                )

                st.success(
                    item.get(
                        "improved",
                        ""
                    )
                )

                st.markdown(
                    "**💡 Why?**"
                )

                st.write(
                    item.get(
                        "reason",
                        ""
                    )
                )

        # -------------------------------------------------
        # PROJECTS
        # -------------------------------------------------

        st.subheader(
            "🚀 Improved Projects"
        )

        projects = improved.get(
            "improved_projects",
            []
        )

        for i, project in enumerate(
            projects,
            1
        ):

            project_name = project.get(
                "project",
                f"Project {i}"
            )

            with st.expander(
                f"🚀 {project_name}"
            ):

                st.markdown(
                    "**Original**"
                )

                st.write(
                    project.get(
                        "original",
                        ""
                    )
                )

                st.markdown(
                    "**✨ Improved**"
                )

                st.success(
                    project.get(
                        "improved",
                        ""
                    )
                )

                st.markdown(
                    "**💡 Why?**"
                )

                st.write(
                    project.get(
                        "reason",
                        ""
                    )
                )

        # -------------------------------------------------
        # KEYWORDS
        # -------------------------------------------------

        st.subheader(
            "🔑 Keywords to Highlight"
        )

        keywords = improved.get(
            "keywords_to_highlight",
            []
        )

        if keywords:

            keyword_columns = st.columns(
                3
            )

            for i, keyword in enumerate(
                keywords
            ):

                with keyword_columns[
                    i % 3
                ]:

                    st.success(
                        f"🔑 {keyword}"
                    )

        # -------------------------------------------------
        # GENERATE AGAIN
        # -------------------------------------------------

        if st.button(
            "🔄 Generate New Suggestions"
        ):

            st.session_state.resume_improvement = None

            st.rerun()


# =========================================================
# INTERVIEW COACH
# =========================================================

elif page == "🎤 Interview Coach":

    st.header(
        "🎤 AI Interview Coach"
    )

    st.caption(
        "Practice questions generated specifically "
        "from your resume and target role."
    )

    questions = result.get(
        "interview_questions",
        []
    )

    if not questions:

        st.info(
            "No interview questions were generated."
        )

    else:

        selected_question = st.selectbox(
            "🎯 Select an interview question",
            questions
        )

        st.markdown(
            "### 💬 Your Answer"
        )

        user_answer = st.text_area(
            "Type your answer as if you are speaking to the interviewer.",
            height=200,
            placeholder=(
                "Start typing your answer..."
            )
        )

        if st.button(
            "🎤 Evaluate My Answer",
            type="primary",
            use_container_width=True
        ):

            if not user_answer.strip():

                st.warning(
                    "⚠️ Please enter your answer."
                )

            else:

                with st.spinner(
                    "🤖 AI interviewer is evaluating your answer..."
                ):

                    try:

                        response = evaluate_interview_answer(
                            selected_question,
                            user_answer,
                            st.session_state.resume_text,
                            st.session_state.job_description
                        )

                        feedback = parse_json_response(
                            response
                        )

                        st.session_state.interview_feedback = (
                            feedback
                        )

                    except Exception as e:

                        st.error(
                            "❌ Interview evaluation failed."
                        )

                        st.code(
                            str(e)
                        )

        # -------------------------------------------------
        # FEEDBACK
        # -------------------------------------------------

        if st.session_state.interview_feedback:

            feedback = (
                st.session_state.interview_feedback
            )

            st.divider()

            st.subheader(
                "📊 AI Evaluation"
            )

            clarity = safe_score(
                feedback.get(
                    "clarity_score",
                    0
                )
            )

            technical = safe_score(
                feedback.get(
                    "technical_score",
                    0
                )
            )

            relevance = safe_score(
                feedback.get(
                    "relevance_score",
                    0
                )
            )

            score1, score2, score3 = st.columns(
                3
            )

            with score1:

                st.metric(
                    "🗣️ Clarity",
                    f"{clarity}/100"
                )

                st.progress(
                    clarity / 100
                )

            with score2:

                st.metric(
                    "🧠 Technical Depth",
                    f"{technical}/100"
                )

                st.progress(
                    technical / 100
                )

            with score3:

                st.metric(
                    "🎯 Relevance",
                    f"{relevance}/100"
                )

                st.progress(
                    relevance / 100
                )

            st.divider()

            st.subheader(
                "✅ What You Did Well"
            )

            for strength in feedback.get(
                "strengths",
                []
            ):

                st.success(
                    f"✓ {strength}"
                )

            st.subheader(
                "💡 Areas to Improve"
            )

            for improvement in feedback.get(
                "improvements",
                []
            ):

                st.warning(
                    f"⚡ {improvement}"
                )

            st.subheader(
                "🧠 Better Answer Structure"
            )

            for i, step in enumerate(
                feedback.get(
                    "answer_structure",
                    []
                ),
                1
            ):

                st.markdown(
                    f"**{i}.** {step}"
                )

            follow_up = feedback.get(
                "follow_up_question",
                ""
            )

            if follow_up:

                st.subheader(
                    "🔁 Follow-up Question"
                )

                st.info(
                    follow_up
                )

            if st.button(
                "🔄 Try Another Answer"
            ):

                st.session_state.interview_feedback = None

                st.rerun()


# =========================================================
# CAREER REPORT
# =========================================================

elif page == "📄 Career Report":

    st.header(
        "📄 Career Readiness Report"
    )

    st.caption(
        "Download a professional report of your "
        "AI CareerMatch analysis."
    )

    report_text = generate_report_text()

    # -----------------------------------------------------
    # REPORT PREVIEW
    # -----------------------------------------------------

    st.subheader(
        "👀 Report Preview"
    )

    with st.container(
        height=450
    ):

        st.text(
            report_text
        )

    st.divider()

    # -----------------------------------------------------
    # DOWNLOAD BUTTONS
    # -----------------------------------------------------

    try:

        pdf_data = create_pdf_report()

        download_col1, download_col2 = st.columns(
            2
        )

        with download_col1:

            st.download_button(
                label="📥 Download Professional PDF",
                data=pdf_data,
                file_name="AI_CareerMatch_Report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

        with download_col2:

            st.download_button(
                label="📄 Download Text Report",
                data=report_text,
                file_name="AI_CareerMatch_Report.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.success(
            "✅ Your professional career report is ready."
        )

    except Exception as e:

        st.error(
            "❌ PDF generation failed."
        )

        st.code(
            str(e)
        )

        st.download_button(
            label="📄 Download Text Report",
            data=report_text,
            file_name="AI_CareerMatch_Report.txt",
            mime="text/plain",
            use_container_width=True
        )


# =========================================================
# DEVELOPER VIEW
# =========================================================

st.divider()

with st.expander(
    "🔎 Developer View — Raw AI Analysis"
):

    st.json(
        result
    )


# =========================================================
# START NEW ANALYSIS
# =========================================================

st.divider()

reset_col1, reset_col2 = st.columns(
    [3, 1]
)

with reset_col2:

    if st.button(
        "🗑️ New Analysis"
    ):

        st.session_state.analysis = None

        st.session_state.resume_text = ""

        st.session_state.job_description = ""

        st.session_state.resume_improvement = None

        st.session_state.interview_feedback = None

        st.session_state.analysis_date = None

        st.rerun()


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

        🎯 AI CareerMatch &nbsp;|&nbsp;
        Powered by Gemini &nbsp;|&nbsp;
        Built with Python + Streamlit

    </div>
    """,
    unsafe_allow_html=True
)