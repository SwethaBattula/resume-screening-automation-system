"""Centralized Configuration Module for Resume Screening Automation System.

Provides paths, scoring weights, threshold values, and logger configurations.
"""

from pathlib import Path
import logging

# Base directories
BASE_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = BASE_DIR / "data"
OUTPUT_DIR: Path = BASE_DIR / "output"

# Default File Paths
SKILLS_FILE_PATH: Path = DATA_DIR / "skills.txt"
SAMPLE_JD_PATH: Path = DATA_DIR / "sample_job_description.txt"
DEFAULT_CSV_OUTPUT: Path = OUTPUT_DIR / "shortlisted_candidates.csv"
DEFAULT_JSON_OUTPUT: Path = OUTPUT_DIR / "shortlisted_candidates.json"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Scoring Weight Configuration (80% Skill Match, 20% Experience Match)
WEIGHT_SKILLS: float = 0.80
WEIGHT_EXPERIENCE: float = 0.20
DEFAULT_REQUIRED_EXPERIENCE_YEARS: float = 3.0

# Recommendation Thresholds
THRESHOLD_SHORTLISTED: float = 80.0
THRESHOLD_CONSIDER: float = 60.0

RECOMMENDATION_SHORTLISTED: str = "Shortlisted"
RECOMMENDATION_CONSIDER: str = "Consider"
RECOMMENDATION_REJECTED: str = "Rejected"

# Logging Configuration
LOG_LEVEL: int = logging.INFO
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
