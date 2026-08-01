"""Backend Pipeline Orchestrator Module.

Coordinates PDF text extraction, NLP preprocessing, resume & JD parsing, candidate scoring,
executive summary generation, ranking, and output exporting into unified workflow functions.
"""

from pathlib import Path
from typing import List, Dict, Any, Union, Optional, Set
import config
from utils.logger import setup_logger
from utils.extractor import extract_text_from_pdf
from utils.preprocess import preprocess_text
from utils.skills import load_skills_db
from utils.parser import parse_candidate_resume, parse_job_description
from utils.scorer import (
    calculate_match_score,
    get_recommendation,
    generate_candidate_summary,
    rank_candidates,
)
from utils.exporter import export_results

logger = setup_logger("utils.resume_pipeline")


def process_resume(
    pdf_path: Union[str, Path],
    job_description: Union[str, Path, Dict[str, Any]],
    skills_db: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """Orchestrates end-to-end processing for a single resume against a Job Description.

    Pipeline sequence:
    1. Extracts raw text from PDF resume.
    2. Runs NLP preprocessing (tokenization, lowercasing, stopword removal, lemmatization).
    3. Parses candidate profile (Name, Email, Phone, Education, Skills, Experience).
    4. Parses Job Description requirements (Required Skills, Required Experience).
    5. Calculates weighted match score (80% Skills + 20% Experience).
    6. Assigns recommendation status ('Shortlisted', 'Consider', 'Rejected').
    7. Generates a 2–3 sentence executive candidate summary.

    Args:
        pdf_path (Union[str, Path]): Path to the candidate PDF resume.
        job_description (Union[str, Path, Dict[str, Any]]): Raw JD text, path to JD text file,
            or pre-parsed JD dictionary.
        skills_db (Optional[Set[str]]): Preloaded set of technical skills. If None,
            loads skills automatically from default skills.txt.

    Returns:
        Dict[str, Any]: Comprehensive candidate screening record dictionary.
    """
    path = Path(pdf_path).resolve()
    logger.info(f"Processing candidate resume: {path.name}")

    # Step 1: Skills Database
    active_skills_db = skills_db if skills_db is not None else load_skills_db()

    # Step 2: PDF Text Extraction
    raw_text, extract_meta = extract_text_from_pdf(path)

    # Step 3: Parse Candidate Resume
    candidate_info = parse_candidate_resume(
        text=raw_text,
        skills_db=active_skills_db,
        resume_metadata=extract_meta
    )

    # Step 5: Parse Job Description
    if isinstance(job_description, dict) and "required_skills" in job_description:
        parsed_jd = job_description
    else:
        parsed_jd = parse_job_description(job_description, active_skills_db)

    # Step 6: Calculate Scores
    scoring_result = calculate_match_score(
        candidate_skills=candidate_info.get("skills", []),
        required_skills=parsed_jd.get("required_skills", set()),
        candidate_exp_years=candidate_info.get("experience_years", 0.0),
        required_exp_years=parsed_jd.get("required_experience_years", config.DEFAULT_REQUIRED_EXPERIENCE_YEARS)
    )

    recommendation = get_recommendation(scoring_result["final_score"])
    scoring_result["recommendation"] = recommendation

    # Step 7: Generate Executive Candidate Summary
    summary = generate_candidate_summary(candidate_info, scoring_result)

    # Step 8: Consolidate Output Record
    candidate_record = {
        "candidate_name": candidate_info["candidate_name"],
        "email": candidate_info["email"],
        "phone": candidate_info["phone"],
        "education": candidate_info["education"],
        "skills": candidate_info["skills"],
        "experience_years": candidate_info["experience_years"],
        "resume_filename": candidate_info["resume_filename"],
        "resume_path": candidate_info["resume_path"],
        "skill_score": scoring_result["skill_score"],
        "experience_score": scoring_result["experience_score"],
        "final_score": scoring_result["final_score"],
        "matched_skills": scoring_result["matched_skills"],
        "missing_skills": scoring_result["missing_skills"],
        "recommendation": recommendation,
        "summary": summary,
        "extraction_status": extract_meta.get("extraction_status", "Unknown"),
    }

    logger.info(f"Finished processing {path.name}: Score={scoring_result['final_score']}%, Status={recommendation}")
    return candidate_record


def process_resume_batch(
    pdf_paths: List[Union[str, Path]],
    job_description: Union[str, Path, Dict[str, Any]],
    skills_db: Optional[Set[str]] = None,
    export: bool = True,
    csv_output: Optional[Union[str, Path]] = None,
    json_output: Optional[Union[str, Path]] = None
) -> List[Dict[str, Any]]:
    """Processes a batch of PDF resumes against a Job Description, ranks results, and exports CSV/JSON.

    Args:
        pdf_paths (List[Union[str, Path]]): List of PDF resume paths.
        job_description (Union[str, Path, Dict[str, Any]]): Job Description text, path, or parsed dict.
        skills_db (Optional[Set[str]]): Preloaded skills set.
        export (bool): If True, automatically exports ranked results to CSV and JSON.
        csv_output (Optional[Union[str, Path]]): Optional custom CSV output path.
        json_output (Optional[Union[str, Path]]): Optional custom JSON output path.

    Returns:
        List[Dict[str, Any]]: Ranked candidate records in descending score order.
    """
    logger.info(f"Starting batch resume screening for {len(pdf_paths)} candidates.")

    active_skills_db = skills_db if skills_db is not None else load_skills_db()
    results: List[Dict[str, Any]] = []

    # Pre-parse Job Description once for the entire batch
    if isinstance(job_description, dict) and "required_skills" in job_description:
        parsed_jd = job_description
    else:
        parsed_jd = parse_job_description(job_description, active_skills_db)

    for pdf_path in pdf_paths:
        try:
            record = process_resume(pdf_path, parsed_jd, active_skills_db)
            results.append(record)
        except Exception as exc:
            logger.error(f"Error processing resume {pdf_path}: {exc}")

    # Rank candidates by final score descending
    ranked_results = rank_candidates(results)

    if export and ranked_results:
        export_results(ranked_results, csv_path=csv_output, json_path=json_output)

    return ranked_results
