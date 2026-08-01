"""Candidate Resume and Job Description Parser Module.

Extracts structured information from resume text (Name, Email, Phone, Education, Skills,
Date-Range & Explicit Experience Years) and parses Job Description requirements.
"""

from pathlib import Path
import re
from datetime import datetime
from typing import Dict, Any, Set, List, Union, Optional
import config
from utils.logger import setup_logger
from utils.skills import extract_skills
from utils.preprocess import _get_spacy_nlp

logger = setup_logger("utils.parser")

# Regex Patterns
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}|\+\d{10,12}|\b\d{10}\b"
)

DEGREE_KEYWORDS = [
    "ph.d", "phd", "doctorate", "master of science", "master of arts", "master of technology",
    "m.s.", "ms", "m.tech", "mtech", "bachelor of science", "bachelor of technology",
    "bachelor of engineering", "b.s.", "bs", "b.tech", "btech", "b.e.", "be",
    "degree", "computer science", "information technology", "software engineering",
    "data science", "mathematics", "physics", "electrical engineering"
]

NON_NAME_WORDS = {
    # Document section headers & meta words
    "resume", "curriculum", "vitae", "cv", "contact", "email", "phone", "profile",
    "summary", "objective", "experience", "education", "skills", "projects", "work",
    "personal", "details", "page", "github", "linkedin", "address", "city", "state",
    "location", "portfolio", "tel", "mobile", "cell", "telephone",
    # Tech skills & keywords
    "java", "python", "javascript", "typescript", "c++", "c#", "html", "css", "sql", "aws",
    "docker", "kubernetes", "react", "angular", "vue", "node", "django", "flask", "fastapi",
    "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "mongodb", "postgresql",
    "mysql", "oracle", "redis", "git", "gitlab", "jira", "ci/cd", "linux", "unix",
    "azure", "gcp", "devops", "cloud", "api", "rest", "graphql", "microservices", "data",
    "science", "machine", "learning", "ai", "nlp", "deep", "framework", "library", "database",
    # Common job titles & roles
    "developer", "engineer", "intern", "architect", "analyst", "administrator", "consultant",
    "manager", "lead", "senior", "junior", "principal", "staff", "associate", "specialist",
    "fullstack", "full-stack", "frontend", "backend", "software", "web", "system", "systems",
    "network", "security", "qa", "test", "tester"
}


def extract_email(text: str) -> Optional[str]:
    """Extracts email address from text using regular expressions.

    Args:
        text (str): Input text string.

    Returns:
        Optional[str]: Extracted email string or None if not found.
    """
    if not text:
        return None
    matches = EMAIL_REGEX.findall(text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    """Extracts phone number from text using regular expressions.

    Args:
        text (str): Input text string.

    Returns:
        Optional[str]: Extracted phone number string or None if not found.
    """
    if not text:
        return None
    matches = PHONE_REGEX.findall(text)
    if matches:
        clean_phone = matches[0].strip()
        if len(clean_phone) >= 7:
            return clean_phone
    return None


def extract_education(text: str) -> List[str]:
    """Extracts education degrees and fields of study from text.

    Args:
        text (str): Input text string.

    Returns:
        List[str]: List of matched education degree keywords/phrases.
    """
    if not text:
        return []
    lowercased = text.lower()
    found_degrees: Set[str] = set()

    for keyword in DEGREE_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, lowercased):
            found_degrees.add(keyword.upper() if len(keyword) <= 4 else keyword.title())

    return sorted(list(found_degrees))


def extract_name(text: str, filename: Optional[str] = None) -> str:
    """Extracts candidate name using an improved 5-level fallback hierarchy.

    Hierarchy:
    1. Proximity to contact info (email/phone): inspect lines near email/phone for a valid name.
    2. spaCy Named Entity Recognition (PERSON entity) on non-noise header text.
    3. First 8 non-empty lines heuristic (capitalized line, excluding noise words, tech keywords, & titles).
    4. Cleaned filename (e.g., 'sofia_brown_resume.pdf' -> 'Sofia Brown').
    5. Fallback string: 'Unknown Candidate'.

    Args:
        text (str): Raw resume text.
        filename (Optional[str]): Source PDF filename.

    Returns:
        str: Extracted candidate name.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()] if text else []

    # Level 1: Proximity to Contact Information (Email / Phone)
    if lines:
        contact_line_indices = []
        for idx, line in enumerate(lines[:10]):
            if EMAIL_REGEX.search(line) or PHONE_REGEX.search(line):
                contact_line_indices.append(idx)

        candidate_indices = []
        for c_idx in contact_line_indices:
            for offset in [-1, -2, 1, 2, 0]:
                t_idx = c_idx + offset
                if 0 <= t_idx < min(len(lines), 10) and t_idx not in candidate_indices:
                    candidate_indices.append(t_idx)

        for idx in candidate_indices:
            line = lines[idx]
            clean_line = EMAIL_REGEX.sub("", line)
            clean_line = PHONE_REGEX.sub("", clean_line).strip()
            clean_line = re.sub(r"[\(\)\|\:\,\-\•]", " ", clean_line).strip()
            words = clean_line.split()

            if 1 <= len(words) <= 4:
                lower_words = [w.lower() for w in words]
                if not any(w in NON_NAME_WORDS for w in lower_words):
                    if all(len(w) >= 2 and all(c.isalpha() or c in ".-'" for c in w) for w in words):
                        return " ".join(words).title()

    # Level 2: spaCy NER
    if text:
        nlp = _get_spacy_nlp()
        if nlp is not None:
            try:
                doc = nlp(text[:1000])
                for ent in doc.ents:
                    if ent.label_ == "PERSON":
                        name_candidate = ent.text.strip()
                        clean_tokens = [w for w in name_candidate.split() if w.lower() not in NON_NAME_WORDS]
                        if 1 <= len(clean_tokens) <= 4 and not EMAIL_REGEX.search(name_candidate) and not PHONE_REGEX.search(name_candidate):
                            if all(len(w) >= 2 and all(c.isalpha() or c in ".-'" for c in w) for w in clean_tokens):
                                return " ".join(clean_tokens).title()
            except Exception as exc:
                logger.warning(f"spaCy NER name extraction failed: {exc}")

    # Level 3: Top Lines Heuristic
    for line in lines[:8]:
        clean_line = EMAIL_REGEX.sub("", line)
        clean_line = PHONE_REGEX.sub("", clean_line).strip()
        clean_line = re.sub(r"[\(\)\|\:\,\-\•]", " ", clean_line).strip()
        words = clean_line.split()
        if 1 <= len(words) <= 4:
            lower_words = [w.lower() for w in words]
            if not any(w in NON_NAME_WORDS for w in lower_words):
                if all(len(w) >= 2 and all(c.isalpha() or c in ".-'" for c in w) for w in words):
                    return " ".join(words).title()

    # Level 4: Filename Cleanup
    if filename:
        stem = Path(filename).stem
        cleaned_stem = re.sub(r"(?i)(resume|cv|curriculum|vitae|_|-|\d+)", " ", stem).strip()
        words = cleaned_stem.split()
        if words:
            lower_words = [w.lower() for w in words]
            clean_words = [w for w, lw in zip(words, lower_words) if lw not in ("resume", "cv", "curriculum", "vitae")]
            if clean_words:
                return " ".join(clean_words).title()

    # Level 5: Fallback
    return "Unknown Candidate"


def extract_experience_years(text: str) -> float:
    """Extracts total years of professional experience from explicit text and date ranges.

    Combines explicit statements (e.g. '5+ years experience') with parsed date range
    intervals (e.g. 'Jan 2021 – Present', '2018 - 2023') to compute estimated total experience.

    Args:
        text (str): Input resume text.

    Returns:
        float: Estimated total years of experience (rounded to 1 decimal place).
    """
    if not text:
        return 0.0

    explicit_years: List[float] = []

    # Pattern for explicit year mentions: e.g., "5+ years", "3.5 yrs", "8 years of experience"
    exp_pattern = re.compile(
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|work)",
        re.IGNORECASE
    )
    for match in exp_pattern.findall(text):
        try:
            explicit_years.append(float(match))
        except ValueError:
            pass

    # Date range parsing: e.g. "2018 - 2022", "Jan 2020 - Present", "05/2019 to 11/2021"
    current_year = datetime.now().year
    date_range_pattern = re.compile(
        r"\b(19\d\d|20\d\d)\s*(?:-|–|—|to)\s*(19\d\d|20\d\d|present|current|now)\b",
        re.IGNORECASE
    )

    range_years = 0.0
    for start_str, end_str in date_range_pattern.findall(text):
        try:
            start_yr = int(start_str)
            if end_str.lower() in ("present", "current", "now"):
                end_yr = current_year
            else:
                end_yr = int(end_str)
            diff = max(0, end_yr - start_yr)
            if diff <= 45:  # Filter unreasonable date spans
                range_years += diff
        except ValueError:
            pass

    total_years = max(explicit_years) if explicit_years else range_years
    return round(total_years, 1)


def parse_candidate_resume(
    text: str,
    skills_db: Set[str],
    resume_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Parses raw candidate resume text into a structured profile dictionary.

    Args:
        text (str): Raw resume text.
        skills_db (Set[str]): Preloaded skills dataset.
        resume_metadata (Optional[Dict[str, Any]]): Metadata dict containing 'resume_filename'
            and 'resume_path'.

    Returns:
        Dict[str, Any]: Parsed candidate data dictionary with keys:
            'candidate_name', 'email', 'phone', 'education', 'skills',
            'experience_years', 'resume_filename', 'resume_path'.
    """
    metadata = resume_metadata or {}
    filename = metadata.get("resume_filename")
    filepath = metadata.get("resume_path", "Unknown Path")

    name = extract_name(text, filename)
    email = extract_email(text) or "N/A"
    phone = extract_phone(text) or "N/A"
    education = extract_education(text)
    skills = sorted(list(extract_skills(text, skills_db)))
    exp_years = extract_experience_years(text)

    return {
        "candidate_name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "skills": skills,
        "experience_years": exp_years,
        "resume_filename": filename or "Unknown File",
        "resume_path": filepath,
    }


def extract_jd_required_skills(raw_text: str, skills_db: Set[str]) -> Set[str]:
    """Extracts required skills from Job Description, prioritizing explicit skills sections.

    Args:
        raw_text (str): Raw JD text.
        skills_db (Set[str]): Preloaded skills dataset.

    Returns:
        Set[str]: Extracted set of required skills.
    """
    if not raw_text or not skills_db:
        return set()

    # Search for explicit required skills / technical skills section
    section_pattern = re.compile(
        r"(?:required\s*(?:technical\s*)?skills|requirements|technical\s*skills|key\s*skills|qualifications)[\s:-]+(.*?)(?=\n\s*\n[A-Z]|\Z)",
        re.IGNORECASE | re.DOTALL
    )
    matches = section_pattern.findall(raw_text)
    if matches:
        focused_text = " ".join(matches)
        focused_skills = extract_skills(focused_text, skills_db)
        if len(focused_skills) >= 3:
            return focused_skills

    return extract_skills(raw_text, skills_db)


def parse_job_description(
    jd_input: Union[str, Path],
    skills_db: Set[str]
) -> Dict[str, Any]:
    """Parses Job Description from raw text string or file path.

    Args:
        jd_input (Union[str, Path]): Raw JD text string or Path to JD file.
        skills_db (Set[str]): Preloaded skills dataset.

    Returns:
        Dict[str, Any]: Parsed JD requirements dictionary containing:
            - 'required_skills': Set[str] of extracted required skills.
            - 'required_experience_years': float target experience years.
            - 'raw_text': str raw JD content.
    """
    raw_text = ""

    if isinstance(jd_input, Path):
        if jd_input.is_file():
            try:
                with open(jd_input, "r", encoding="utf-8") as f:
                    raw_text = f.read()
                logger.info(f"Loaded Job Description from file {jd_input.name}")
            except Exception as exc:
                logger.error(f"Failed to read JD file {jd_input}: {exc}")
                raw_text = ""
        else:
            raw_text = ""
    elif isinstance(jd_input, str) and jd_input.strip():
        try:
            potential_path = Path(jd_input)
            if potential_path.is_file():
                with open(potential_path, "r", encoding="utf-8") as f:
                    raw_text = f.read()
                logger.info(f"Loaded Job Description from file {potential_path.name}")
            else:
                raw_text = jd_input
        except (OSError, ValueError):
            raw_text = jd_input
    else:
        raw_text = ""

    required_skills = extract_jd_required_skills(raw_text, skills_db)
    required_exp = extract_experience_years(raw_text)
    if required_exp <= 0.0:
        required_exp = config.DEFAULT_REQUIRED_EXPERIENCE_YEARS

    return {
        "required_skills": required_skills,
        "required_experience_years": required_exp,
        "raw_text": raw_text,
    }
