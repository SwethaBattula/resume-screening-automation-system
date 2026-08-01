"""Script to generate professional Source Code Documentation PDF for Resume Screening Automation System.

Uses ReportLab to build a structured, styled PDF document.
Font sizes: Main Title (16 pt), Section Headings (14 pt), Body Text (12 pt).
Strictly zero emojis used.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def build_pdf():
    pdf_filename = "Source_Code_Documentation.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Styles adhering strictly to requested font sizes:
    # Main Title: 16 pt
    # Section Headings: 14 pt
    # Body Text: 12 pt

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=15
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569'),
        spaceAfter=30
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    subheading_style = ParagraphStyle(
        'SubSectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#334155'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=8,
        alignment=TA_LEFT
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=15,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f8fafc'),
        borderColor=colors.HexColor('#cbd5e1'),
        borderWidth=0.5,
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=8
    )

    table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e293b')
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#ffffff')
    )

    story = []

    # ---------------------------------------------------------
    # 1. TITLE PAGE / HEADER
    # ---------------------------------------------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("Resume Screening Automation System", title_style))
    story.append(Paragraph("Technical Source Code Documentation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceAfter=20))
    
    meta_data = [
        [Paragraph("<b>Document Type:</b>", body_style), Paragraph("Source Code Implementation Architecture", body_style)],
        [Paragraph("<b>Developer:</b>", body_style), Paragraph("Swetha Battula", body_style)],
        [Paragraph("<b>Target Domain:</b>", body_style), Paragraph("Natural Language Processing & HR Tech Automation", body_style)],
        [Paragraph("<b>Repository:</b>", body_style), Paragraph("https://github.com/SwethaBattula/resume-screening-automation-system", body_style)],
        [Paragraph("<b>Status:</b>", body_style), Paragraph("Production Ready / Hackathon Submission", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[130, 374])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#e2e8f0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1'))
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 30))

    # ---------------------------------------------------------
    # 2. PROJECT OVERVIEW
    # ---------------------------------------------------------
    story.append(Paragraph("2. Project Overview", heading_style))
    story.append(Paragraph("<b>Purpose:</b> The Resume Screening Automation System is designed to automate the initial candidate evaluation phase by parsing multi-format PDF resumes, extracting technical skills using NLP and regex phrase boundaries, analyzing professional experience, and scoring applicants against specific Job Descriptions.", body_style))
    story.append(Paragraph("<b>Problem Statement:</b> Traditional manual resume screening is highly labor-intensive, slow, subjective, and prone to human bias. HR teams processing hundreds of technical applicants often face bottlenecks and inconsistent evaluations.", body_style))
    story.append(Paragraph("<b>Solution Overview:</b> This system provides an end-to-end backend processing engine and an interactive Streamlit presentation layer. It extracts resume text, preprocesses content via spaCy/NLTK, maps skills against a 240+ technical skills repository, computes a weighted score (80% Skill Match + 20% Experience Match), generates 2-3 sentence executive summaries, and exports shortlists to CSV and JSON formats.", body_style))

    # ---------------------------------------------------------
    # 3. OBJECTIVES
    # ---------------------------------------------------------
    story.append(Paragraph("3. Objectives", heading_style))
    story.append(Paragraph("• Automate multi-strategy PDF text extraction with pdfplumber and PyPDF2 fallback.", bullet_style))
    story.append(Paragraph("• Implement NLP preprocessing including lowercase conversion, tokenization, stopword filtering, and lemmatization.", bullet_style))
    story.append(Paragraph("• Perform phrase-boundary technical skill matching using pre-compiled LRU-cached regex patterns.", bullet_style))
    story.append(Paragraph("• Implement contact-proximity candidate name extraction to prevent false heading matches.", bullet_style))
    story.append(Paragraph("• Compute candidate scores using an extensible 80% skill + 20% experience weighted model.", bullet_style))
    story.append(Paragraph("• Provide a zero-pandas Streamlit recruiter dashboard for candidate ranking and detailed scorecard viewing.", bullet_style))
    story.append(Paragraph("• Generate standardized CSV and JSON screening reports for integration with downstream HR tools.", bullet_style))

    story.append(Spacer(1, 10))

    # ---------------------------------------------------------
    # 4. TECHNOLOGY STACK
    # ---------------------------------------------------------
    story.append(Paragraph("4. Technology Stack", heading_style))
    story.append(Paragraph("The system is constructed using modern Python backend tools and specialized NLP libraries.", body_style))

    tech_data = [
        [Paragraph("Technology", table_header), Paragraph("Role & Category", table_header), Paragraph("Description", table_header)],
        [Paragraph("Python 3.11", table_text), Paragraph("Core Language", table_text), Paragraph("Primary backend implementation language.", table_text)],
        [Paragraph("Streamlit", table_text), Paragraph("Frontend Dashboard", table_text), Paragraph("Interactive recruiter dashboard and presentation layer.", table_text)],
        [Paragraph("spaCy (en_core_web_sm)", table_text), Paragraph("NLP Engine", table_text), Paragraph("Entity recognition, tokenization, and lemmatization.", table_text)],
        [Paragraph("NLTK", table_text), Paragraph("NLP Utilities", table_text), Paragraph("Fallback stopword processing and text normalization.", table_text)],
        [Paragraph("pdfplumber", table_text), Paragraph("PDF Extraction", table_text), Paragraph("Layout-aware PDF text extraction engine.", table_text)],
        [Paragraph("PyPDF2 / pypdf", table_text), Paragraph("PDF Fallback", table_text), Paragraph("Secondary PDF parser for unreadable streams.", table_text)],
        [Paragraph("Scikit-learn", table_text), Paragraph("ML & Analytics", table_text), Paragraph("Feature processing and similarity calculation utilities.", table_text)]
    ]
    t_tech = Table(tech_data, colWidths=[110, 120, 274])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8fafc')])
    ]))
    story.append(t_tech)

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 5. PROJECT ARCHITECTURE
    # ---------------------------------------------------------
    story.append(Paragraph("5. Project Architecture", heading_style))
    story.append(Paragraph("The application follows a clean layered architecture separating presentation, orchestration, domain processing, and data access layers:", body_style))
    story.append(Paragraph("• <b>Presentation Layer (app.py):</b> Streamlit web dashboard built strictly with native layout components (st.columns, st.container, st.markdown, st.write, st.progress) without pandas dependencies.", bullet_style))
    story.append(Paragraph("• <b>Orchestration Layer (utils/resume_pipeline.py):</b> Exposes batch process APIs (process_resume, process_resume_batch) coordinating all backend steps.", bullet_style))
    story.append(Paragraph("• <b>Text Extraction Layer (utils/extractor.py):</b> Multi-strategy PDF extractor using pdfplumber with PyPDF2 fallback.", bullet_style))
    story.append(Paragraph("• <b>NLP & Parsing Layer (utils/preprocess.py, utils/parser.py):</b> spaCy/NLTK pipeline, contact-proximity name extraction, email/phone regex, and date-range experience parsing.", bullet_style))
    story.append(Paragraph("• <b>Skill Matching Engine (utils/skills.py):</b> Dataset loader (240+ skills) and LRU-cached regex phrase-boundary matcher.", bullet_style))
    story.append(Paragraph("• <b>Scoring & Summary Engine (utils/scorer.py):</b> Extensible 80/20 scoring model, recommendation classifier, and 2-3 sentence executive candidate summary generator.", bullet_style))
    story.append(Paragraph("• <b>Export Layer (utils/exporter.py):</b> Formatter generating flat records, CSV strings, and JSON reports.", bullet_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 6. PROJECT FOLDER STRUCTURE
    # ---------------------------------------------------------
    story.append(Paragraph("6. Project Folder Structure", heading_style))
    tree_text = """ResumeScreeningAutomation/
├── app.py                      # Streamlit Presentation Layer
├── main.py                     # CLI Entry Point & Batch Execution Demo
├── config.py                   # Centralized Configuration & Scoring Weights
├── utils/                      # Backend Modular Engine
│   ├── __init__.py             # Package Initialization
│   ├── extractor.py            # PDF Text Extraction (pdfplumber + PyPDF2 fallback)
│   ├── preprocess.py           # spaCy / NLTK Text Preprocessing Engine
│   ├── parser.py               # Resume Contact, Education, & Experience Parser
│   ├── skills.py               # LRU-cached Technical Skill Matcher
│   ├── scorer.py               # Weighted Match Scorer & Summary Generator
│   ├── resume_pipeline.py      # Master Pipeline Orchestrator
│   ├── exporter.py            # CSV / JSON Exporter & Record Formatter
│   └── logger.py              # Centralized Logging System
├── data/                       # Datasets & Benchmark Job Description
│   ├── skills.txt              # Categorized Skills Database (240+ skills)
│   └── sample_job_description.txt # Benchmark Job Description
├── tests/                      # Automated Test Suite
│   └── test_backend.py         # 18 Edge-Case Unit Tests
├── output/                     # Exported Screening Results Directory
├── requirements.txt            # Package Dependencies Specification
└── README.md                   # Repository Overview & User Guide"""

    story.append(Paragraph(tree_text.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 7. MODULE DESCRIPTION
    # ---------------------------------------------------------
    story.append(Paragraph("7. Module Description", heading_style))
    
    modules = [
        ("app.py", "Streamlit presentation layer. Renders recruiter ranking cards, match progress bars, initials avatars, detailed profile tabs, and CSV/JSON download buttons without importing pandas."),
        ("main.py", "CLI driver script. Loads configuration, executes batch resume processing against the benchmark Job Description, prints formatted rankings, and exports reports."),
        ("config.py", "Centralized configuration module. Stores scoring weights (SKILL_WEIGHT=0.80, EXP_WEIGHT=0.20), thresholds (80% Shortlisted, 60% Consider), paths, and logging formats."),
        ("utils/extractor.py", "Handles PDF text extraction. Tries pdfplumber first to preserve visual layouts, falling back to PyPDF2 if stream objects are corrupted."),
        ("utils/preprocess.py", "NLP preprocessing pipeline. Performs lowercasing, punctuation removal, stopword filtering, tokenization, and spaCy/NLTK lemmatization."),
        ("utils/parser.py", "Extracts structured candidate profile data: Email regex, Phone regex, Education degree detection, date-range experience calculation, and contact-proximity candidate name extraction."),
        ("utils/skills.py", "Loads skills.txt dataset into memory and uses @lru_cache regex compilation to perform word-boundary and multi-word phrase technical skill matching."),
        ("utils/scorer.py", "Calculates weighted match scores, assigns recommendations (Shortlisted/Consider/Rejected), calculates summary metrics, and generates 2-3 sentence executive candidate summaries."),
        ("utils/resume_pipeline.py", "Exposes process_resume() and process_resume_batch() to coordinate text extraction, parsing, scoring, and output generation."),
        ("utils/exporter.py", "Converts candidate results into flat dictionaries, tabular display records, CSV strings/files, and JSON strings/files.")
    ]

    for mod_name, mod_desc in modules:
        story.append(Paragraph(f"<b>{mod_name}:</b> {mod_desc}", body_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 8. RESUME SCREENING WORKFLOW
    # ---------------------------------------------------------
    story.append(Paragraph("8. Resume Screening Workflow", heading_style))
    story.append(Paragraph("The system executes a sequential pipeline for candidate screening:", body_style))

    workflow_steps = [
        "1. Upload Job Description (.txt file or raw text input)",
        "2. Upload Multiple PDF Resumes",
        "3. Multi-Strategy PDF Text Extraction (pdfplumber primary, PyPDF2 fallback)",
        "4. NLP Preprocessing (lowercasing, punctuation removal, stopword filtering, lemmatization)",
        "5. Candidate Information Parsing (Name, Email, Phone, Education, Experience)",
        "6. Technical Skill Extraction (regex boundary matching against skills database)",
        "7. Focused JD Skill Extraction (prioritizes explicit required skills sections)",
        "8. Skill Match Calculation (Candidate matched skills vs JD required skills)",
        "9. Experience Analysis (Explicit experience mentions & parsed date-range calculation)",
        "10. Weighted Candidate Scoring (80% Skill Match + 20% Experience Match)",
        "11. Recommendation Classification & Executive Summary Generation",
        "12. Candidate Ranking & Recruiter Dashboard Visualization",
        "13. Multi-Format Report Export (CSV & JSON download buttons)"
    ]
    for step in workflow_steps:
        story.append(Paragraph(step, bullet_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 9. CANDIDATE SCORING ALGORITHM
    # ---------------------------------------------------------
    story.append(Paragraph("9. Candidate Scoring Algorithm", heading_style))
    story.append(Paragraph("The candidate evaluation model uses an extensible weighted scoring framework:", body_style))
    story.append(Paragraph("• <b>Skill Match Score (80% Weight):</b> Computed as the percentage overlap between candidate extracted technical skills and JD required skills:<br/>&nbsp;&nbsp;&nbsp;&nbsp;<i>Skill Score = (Matched Skills Count / Required JD Skills Count) * 100</i>", bullet_style))
    story.append(Paragraph("• <b>Experience Score (20% Weight):</b> Computed as candidate experience years relative to JD required experience years (capped at 100%):<br/>&nbsp;&nbsp;&nbsp;&nbsp;<i>Exp Score = min(100.0, (Candidate Exp / Required Exp) * 100)</i>", bullet_style))
    story.append(Paragraph("• <b>Final Score Formula:</b><br/>&nbsp;&nbsp;&nbsp;&nbsp;<i>Final Score = (Skill Score * 0.80) + (Experience Score * 0.20)</i>", bullet_style))
    story.append(Paragraph("• <b>Recommendation Boundaries:</b>", subheading_style))
    story.append(Paragraph("&nbsp;&nbsp;- <b>Shortlisted:</b> Final Score &ge; 80.0%", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;- <b>Consider:</b> 60.0% &le; Final Score &lt; 80.0%", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;- <b>Rejected:</b> Final Score &lt; 60.0%", bullet_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 10. FRONTEND FEATURES
    # ---------------------------------------------------------
    story.append(Paragraph("10. Frontend Features", heading_style))
    story.append(Paragraph("The Streamlit dashboard (app.py) provides a modern presentation layer designed for HR recruiters:", body_style))
    story.append(Paragraph("• <b>Hero Header Banner:</b> Prominent title, project overview subtitle, and technology stack tags.", bullet_style))
    story.append(Paragraph("• <b>Sidebar Setup:</b> File uploaders for Job Description (.txt) and multiple PDF resumes, along with compact scoring criteria reference cards.", bullet_style))
    story.append(Paragraph("• <b>Dashboard Cards:</b> Summary metrics showing Total Candidates, Shortlisted, Consider, and Rejected counts.", bullet_style))
    story.append(Paragraph("• <b>Candidate Rankings Tab:</b> Recruiter-style candidate cards featuring rank numbers, CSS initials avatars, st.progress match bars, top 5 matched skills (+N more), and recommendation status badges.", bullet_style))
    story.append(Paragraph("• <b>Detailed Candidate Profile Tab:</b> Candidate selector dropdown displaying Executive Summary, Education, Matched Skills, Missing Required Skills, Scorecard metrics, and contact metadata.", bullet_style))
    story.append(Paragraph("• <b>Export Section:</b> Download buttons for CSV and JSON reports.", bullet_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 11. ERROR HANDLING
    # ---------------------------------------------------------
    story.append(Paragraph("11. Error Handling", heading_style))
    story.append(Paragraph("The system implements robust error handling across all pipeline stages:", body_style))
    story.append(Paragraph("• <b>Corrupted PDF Files:</b> Handled via try-except blocks; if pdfplumber fails, PyPDF2 fallback is attempted. If both fail, an error status is returned gracefully.", bullet_style))
    story.append(Paragraph("• <b>Empty Resume Files:</b> Detected by file size checks (0 bytes) and empty text validations, raising warnings without crashing batch processing.", bullet_style))
    story.append(Paragraph("• <b>Missing Job Description:</b> Checked by frontend and backend; default target experience (2.0 yrs) is used if required experience is unparsed.", bullet_style))
    story.append(Paragraph("• <b>Missing Candidate Details:</b> Name fallback hierarchy defaults to 'Unknown Candidate', missing emails/phones default to 'N/A'.", bullet_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 12. TESTING & VALIDATION
    # ---------------------------------------------------------
    story.append(Paragraph("12. Testing & Validation", heading_style))
    story.append(Paragraph("The codebase includes comprehensive test coverage and validation workflows:", body_style))
    story.append(Paragraph("• <b>Automated Test Suite (tests/test_backend.py):</b> Contains 18 unit and edge-case integration tests covering empty PDFs, corrupted PDFs, missing contact info, empty job descriptions, and large text inputs. Executed via <i>python -m unittest discover -s tests</i>.", bullet_style))
    story.append(Paragraph("• <b>CLI Execution Verification:</b> Executed via <i>python main.py</i> to verify batch execution against benchmark resumes.", bullet_style))
    story.append(Paragraph("• <b>Frontend Verification:</b> Verified via <i>python -m streamlit run app.py</i> ensuring zero pandas dependencies and clean UI rendering.", bullet_style))

    story.append(Spacer(1, 20))

    # ---------------------------------------------------------
    # 13. SCREENSHOTS SECTION (PLACEHOLDERS)
    # ---------------------------------------------------------
    story.append(Paragraph("13. Screenshots Section", heading_style))
    story.append(Paragraph("Below are designated placeholders for application screenshots:", body_style))

    screenshots = [
        "13.1 Home Screen & Upload Interface",
        "13.2 Candidate Rankings Dashboard Cards",
        "13.3 Detailed Candidate Profile & Scorecard",
        "13.4 Export Reports Section (CSV & JSON)"
    ]
    for sc_title in screenshots:
        story.append(Paragraph(sc_title, subheading_style))
        story.append(Paragraph("[ Place screenshot image here ]", ParagraphStyle('BoxText', parent=body_style, textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER)))
        story.append(Spacer(1, 60))  # Blank space for manual insertion

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 14. FUTURE ENHANCEMENTS
    # ---------------------------------------------------------
    story.append(Paragraph("14. Future Enhancements", heading_style))
    story.append(Paragraph("• <b>OCR Integration:</b> Add Tesseract/EasyOCR to parse image-based and scanned PDF resumes.", bullet_style))
    story.append(Paragraph("• <b>Semantic Vector Search:</b> Incorporate Sentence-Transformers / BERT embeddings for semantic skill matching beyond exact keyword matching.", bullet_style))
    story.append(Paragraph("• <b>LLM Assistance:</b> Integrate LLM APIs for qualitative resume synthesis and interview question generation.", bullet_style))
    story.append(Paragraph("• <b>ATS Integration:</b> Build REST APIs connecting with ATS platforms like Workday and Greenhouse.", bullet_style))
    story.append(Paragraph("• <b>Cloud Deployment:</b> Containerize application via Docker for AWS Elastic Container Service / Streamlit Cloud deployment.", bullet_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 15. GITHUB REPOSITORY
    # ---------------------------------------------------------
    story.append(Paragraph("15. GitHub Repository", heading_style))
    story.append(Paragraph("The complete source code, test suite, datasets, and documentation are published on GitHub:", body_style))
    story.append(Paragraph("<b>Repository Link:</b> https://github.com/SwethaBattula/resume-screening-automation-system", body_style))
    story.append(Paragraph("<b>Default Branch:</b> main", body_style))

    story.append(Spacer(1, 15))

    # ---------------------------------------------------------
    # 16. CONCLUSION
    # ---------------------------------------------------------
    story.append(Paragraph("16. Conclusion", heading_style))
    story.append(Paragraph("The Resume Screening Automation System delivers a production-ready, modular, and highly efficient solution for technical resume screening. By combining multi-strategy PDF text extraction, spaCy/NLTK NLP preprocessing, phrase-boundary skill matching, weighted candidate scoring, and a clean Streamlit presentation layer, the application significantly reduces initial recruitment overhead while maintaining objective, reproducible candidate rankings.", body_style))

    # Build PDF Document
    doc.build(story)
    print(f"PDF successfully generated: {os.path.abspath(pdf_filename)}")


if __name__ == "__main__":
    build_pdf()
