"""Resume Scoring, Candidate Ranking, and Summary Generator Module.

Implements an extensible weighted scoring model (80% Skill Match + 20% Experience Match),
recommendation categorization (Shortlisted, Consider, Rejected), candidate ranking, and
concise 2–3 sentence candidate summary generation.
"""

from typing import Dict, Any, Set, List, Union
import config
from utils.logger import setup_logger

logger = setup_logger("utils.scorer")


def calculate_match_score(
    candidate_skills: Union[Set[str], List[str]],
    required_skills: Union[Set[str], List[str]],
    candidate_exp_years: float = 0.0,
    required_exp_years: float = config.DEFAULT_REQUIRED_EXPERIENCE_YEARS
) -> Dict[str, Any]:
    """Calculates extensible weighted match score between candidate profile and Job Description.

    Formula:
        Skill Score = (Matched Skills / Required Skills) * 100  (capped at 100.0)
        Experience Score = (Candidate Exp / Required Exp) * 100  (capped at 100.0)
        Final Score = (Skill Score * 0.80) + (Experience Score * 0.20)

    Gracefully handles empty Job Descriptions or zero required skills.

    Args:
        candidate_skills (Union[Set[str], List[str]]): Candidate's extracted technical skills.
        required_skills (Union[Set[str], List[str]]): JD required technical skills.
        candidate_exp_years (float): Candidate's years of experience.
        required_exp_years (float): JD target required experience years.

    Returns:
        Dict[str, Any]: Detailed scoring breakdown containing:
            - 'skill_score': float skill match score (0-100)
            - 'experience_score': float experience match score (0-100)
            - 'final_score': float overall weighted match score (0-100)
            - 'matched_skills': List[str] skills present in both candidate & JD
            - 'missing_skills': List[str] skills required by JD but missing in candidate
    """
    cand_set = set(candidate_skills) if isinstance(candidate_skills, list) else candidate_skills
    req_set = set(required_skills) if isinstance(required_skills, list) else required_skills

    if not req_set:
        logger.warning("Required skills set is empty. Returning 0.0 match score.")
        return {
            "skill_score": 0.0,
            "experience_score": 0.0,
            "final_score": 0.0,
            "matched_skills": [],
            "missing_skills": [],
        }

    matched_set = cand_set.intersection(req_set)
    missing_set = req_set.difference(cand_set)

    skill_score = min(100.0, (len(matched_set) / len(req_set)) * 100.0)

    if required_exp_years <= 0.0:
        experience_score = 100.0
    else:
        experience_score = min(100.0, (max(0.0, candidate_exp_years) / required_exp_years) * 100.0)

    final_score = (skill_score * config.WEIGHT_SKILLS) + (experience_score * config.WEIGHT_EXPERIENCE)
    final_score = round(final_score, 2)
    skill_score = round(skill_score, 2)
    experience_score = round(experience_score, 2)

    return {
        "skill_score": skill_score,
        "experience_score": experience_score,
        "final_score": final_score,
        "matched_skills": sorted(list(matched_set)),
        "missing_skills": sorted(list(missing_set)),
    }


def get_recommendation(score: float) -> str:
    """Categorizes final candidate score into recommendation tier.

    Thresholds:
    - >= 80.0: 'Shortlisted'
    - 60.0 – 79.99: 'Consider'
    - < 60.0: 'Rejected'

    Args:
        score (float): Final match score (0–100).

    Returns:
        str: Recommendation category string.
    """
    if score >= config.THRESHOLD_SHORTLISTED:
        return config.RECOMMENDATION_SHORTLISTED
    elif score >= config.THRESHOLD_CONSIDER:
        return config.RECOMMENDATION_CONSIDER
    else:
        return config.RECOMMENDATION_REJECTED


def generate_candidate_summary(
    candidate_data: Dict[str, Any],
    score_data: Dict[str, Any]
) -> str:
    """Generates a concise 2–3 sentence executive summary for a candidate.

    Args:
        candidate_data (Dict[str, Any]): Candidate metadata (name, exp, edu, skills).
        score_data (Dict[str, Any]): Candidate scoring metrics & recommendation.

    Returns:
        str: Concise 2–3 sentence professional summary string.
    """
    name = candidate_data.get("candidate_name", "The candidate")
    exp_years = candidate_data.get("experience_years", 0.0)
    edu_list = candidate_data.get("education", [])
    skills_list = candidate_data.get("skills", [])

    final_score = score_data.get("final_score", 0.0)
    recommendation = score_data.get("recommendation", get_recommendation(final_score))
    matched = score_data.get("matched_skills", [])

    edu_str = f" possessing a background in {', '.join(edu_list[:2])}" if edu_list else ""
    exp_str = f"{exp_years} years of professional experience" if exp_years > 0 else "entry-level experience"

    # Sentence 1: Profile intro
    s1 = f"{name} brings approximately {exp_str}{edu_str}."

    # Sentence 2: Key skills & alignment
    if matched:
        top_matched = ", ".join(matched[:4])
        s2 = f"Demonstrates strong technical alignment with key matched skills including {top_matched}."
    elif skills_list:
        top_skills = ", ".join(skills_list[:4])
        s2 = f"Exhibits a skill set featuring {top_skills}, though matching key JD requirements was limited."
    else:
        s2 = "Minimal technical skill matches were identified in the submitted resume text."

    # Sentence 3: Scoring evaluation & recommendation decision
    s3 = f"Achieved an overall match score of {final_score}% and is categorized as '{recommendation}'."

    return f"{s1} {s2} {s3}"


def rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sorts processed candidate records by final match score in descending order.

    Args:
        candidates (List[Dict[str, Any]]): List of processed candidate profile dictionaries.

    Returns:
        List[Dict[str, Any]]: Candidate records sorted by final_score (descending).
    """
    return sorted(
        candidates,
        key=lambda c: (c.get("final_score", 0.0), c.get("candidate_name", "")),
        reverse=True
    )
