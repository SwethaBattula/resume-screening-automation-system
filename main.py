"""Main CLI Entry Point for Resume Screening Automation System Backend.

Demonstrates end-to-end backend processing of multiple PDF resumes against a Job Description,
ranking candidate profiles, and generating CSV & JSON output reports.
"""

import sys
from pathlib import Path
from typing import List

import config
from utils.logger import setup_logger
from utils.skills import load_skills_db
from utils.resume_pipeline import process_resume_batch

logger = setup_logger("main")


def create_sample_resumes_if_missing(resumes_dir: Path) -> List[Path]:
    """Generates sample PDF resumes if none are present in the directory for testing.

    Args:
        resumes_dir (Path): Target directory for resume files.

    Returns:
        List[Path]: List of PDF resume paths available for screening.
    """
    resumes_dir.mkdir(parents=True, exist_ok=True)
    existing_pdfs = list(resumes_dir.glob("*.pdf"))

    if existing_pdfs:
        return existing_pdfs

    logger.info(f"No PDF resumes found in {resumes_dir}. Generating synthetic test resumes...")

    sample_candidates = [
        {
            "filename": "alice_johnson_senior_python_developer.pdf",
            "text": """
            Alice Johnson
            Email: alice.johnson@example.com | Phone: (555) 234-5678
            Location: San Francisco, CA

            PROFESSIONAL SUMMARY
            Senior Software Engineer with 6+ years of experience specializing in Python backend architecture,
            machine learning pipelines, and cloud microservices.

            EXPERIENCE
            Lead Backend Engineer - TechCorp (2020 - Present)
            - Built scalable REST APIs using FastAPI, Flask, and PostgreSQL handling 10M daily requests.
            - Deployed ML models using PyTorch, Scikit-Learn, Docker, and Kubernetes on AWS.

            Backend Engineer - DataSoft (2018 - 2020)
            - Implemented ETL pipelines using Pandas, NumPy, Redis, and PySpark.

            EDUCATION
            Master of Science in Computer Science - Stanford University (2018)

            SKILLS
            Python, FastAPI, Flask, Django, SQL, PostgreSQL, Redis, Machine Learning, Deep Learning,
            PyTorch, Scikit-Learn, Pandas, NumPy, Docker, Kubernetes, AWS, Git, CI/CD, Microservices, REST API
            """
        },
        {
            "filename": "bob_smith_data_scientist.pdf",
            "text": """
            Bob Smith
            Email: bob.smith@devmail.org | Phone: +1-555-987-6543

            SUMMARY
            Data Scientist with 3.5 years experience building NLP and ML predictive models.

            EXPERIENCE
            Data Scientist - AI Solutions (2021 - Present)
            - Developed NLP text classification models using spaCy, NLTK, and Transformers.
            - Built data pipelines using Python, SQL, PostgreSQL, and Scikit-Learn.

            EDUCATION
            Bachelor of Science in Data Science - UC Berkeley (2020)

            TECHNICAL SKILLS
            Python, SQL, PostgreSQL, MongoDB, Machine Learning, Natural Language Processing,
            spaCy, NLTK, Scikit-Learn, Pandas, NumPy, Docker, Git, REST API
            """
        },
        {
            "filename": "charlie_brown_junior_dev.pdf",
            "text": """
            Charlie Brown
            Email: charlie.b@webmail.com | Phone: 555-456-7890

            PROFILE
            Junior Web Developer with 1 year of experience building frontend applications.

            EXPERIENCE
            Junior Frontend Developer - WebWorks (2023 - Present)
            - Developed user interfaces using HTML, CSS, JavaScript, React, and Bootstrap.

            EDUCATION
            Bachelor of Arts in Communication - State College (2022)

            SKILLS
            JavaScript, React, HTML, CSS, Bootstrap, Git
            """
        }
    ]

    generated_paths = []

    # Attempt PDF generation using reportlab if available, fallback to simple FPDF/PyPDF2 synthetic files
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        for cand in sample_candidates:
            pdf_path = resumes_dir / cand["filename"]
            c = canvas.Canvas(str(pdf_path), pagesize=letter)
            textobject = c.beginText(40, 750)
            textobject.setFont("Helvetica", 10)
            for line in cand["text"].strip().split("\n"):
                textobject.textLine(line.strip())
            c.drawText(textobject)
            c.save()
            generated_paths.append(pdf_path)
            logger.info(f"Generated sample PDF resume: {pdf_path.name}")
    except ImportError:
        logger.warning("reportlab package not available for sample PDF creation. Will use mock text loader.")

    return generated_paths or list(resumes_dir.glob("*.pdf"))


def main() -> None:
    """Main execution workflow for Resume Screening Backend System."""
    logger.info("==========================================================")
    logger.info(" Starting Resume Screening Automation System Backend ")
    logger.info("==========================================================")

    # 1. Load Skills Database
    skills_db = load_skills_db(config.SKILLS_FILE_PATH)
    logger.info(f"Loaded {len(skills_db)} skills into memory database.")

    # 2. Check Job Description
    jd_path = config.SAMPLE_JD_PATH
    if not jd_path.exists():
        logger.error(f"Sample Job Description not found at {jd_path}")
        sys.exit(1)

    logger.info(f"Using Job Description from: {jd_path}")

    # 3. Locate / Create Sample Resumes
    resumes_dir = config.DATA_DIR / "sample_resumes"
    pdf_paths = create_sample_resumes_if_missing(resumes_dir)

    if not pdf_paths:
        logger.warning(f"No PDF resumes available in {resumes_dir}. Please place .pdf files in data/sample_resumes/")
        return

    logger.info(f"Found {len(pdf_paths)} PDF resume(s) for screening.")

    # 4. Run Batch Screening Pipeline
    ranked_candidates = process_resume_batch(
        pdf_paths=pdf_paths,
        job_description=jd_path,
        skills_db=skills_db,
        export=True,
        csv_output=config.DEFAULT_CSV_OUTPUT,
        json_output=config.DEFAULT_JSON_OUTPUT
    )

    # 5. Display Summary Results
    logger.info("\n" + "=" * 60)
    logger.info(" SCREENING RESULTS & CANDIDATE RANKING ")
    logger.info("=" * 60)

    for rank, cand in enumerate(ranked_candidates, 1):
        logger.info(
            f"Rank #{rank}: {cand['candidate_name']} | "
            f"Score: {cand['final_score']}% | "
            f"Recommendation: {cand['recommendation']} | "
            f"Exp: {cand['experience_years']} yrs | "
            f"Matched Skills: {len(cand['matched_skills'])}/{len(cand['matched_skills']) + len(cand['missing_skills'])}"
        )
        logger.info(f"   Summary: {cand['summary']}")
        logger.info("-" * 60)

    logger.info(f"CSV Exported to:  {config.DEFAULT_CSV_OUTPUT}")
    logger.info(f"JSON Exported to: {config.DEFAULT_JSON_OUTPUT}")
    logger.info("Backend processing completed successfully!")


if __name__ == "__main__":
    main()
