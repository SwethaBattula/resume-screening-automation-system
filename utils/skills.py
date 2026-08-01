"""Technical Skills Extraction Module.

Loads predefined skills dataset from skills.txt and provides accurate phrase and token-boundary
skill extraction from text documents with compiled regex caching.
"""

from pathlib import Path
import re
from functools import lru_cache
from typing import Set, Union, Optional
import config
from utils.logger import setup_logger

logger = setup_logger("utils.skills")


@lru_cache(maxsize=2048)
def _compile_skill_pattern(skill: str) -> re.Pattern:
    """Compiles and caches regex boundary pattern for a skill string."""
    escaped_skill = re.escape(skill)
    pattern_str = r"(?:^|[\s,.\/;:\(\)\[\]\{\}\-\–\—])" + escaped_skill + r"(?:$|[\s,.\/;:\(\)\[\]\{\}\-\–\—])"
    return re.compile(pattern_str)


def load_skills_db(skills_file_path: Optional[Union[str, Path]] = None) -> Set[str]:
    """Loads and normalizes predefined technical skills dataset from file.

    Ignores empty lines and comment headers starting with '#'.

    Args:
        skills_file_path (Optional[Union[str, Path]]): Path to skills.txt file.
            Defaults to config.SKILLS_FILE_PATH if None.

    Returns:
        Set[str]: Set of lowercased, stripped technical skill phrases.
    """
    path = Path(skills_file_path or config.SKILLS_FILE_PATH).resolve()

    skills: Set[str] = set()

    if not path.exists():
        logger.error(f"Skills file not found at path: {path}")
        return skills

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str and not line_str.startswith("#"):
                    skills.add(line_str.lower())
        logger.info(f"Loaded {len(skills)} technical skills from {path.name}")
    except Exception as exc:
        logger.error(f"Failed to load skills dataset from {path}: {exc}")

    return skills


def extract_skills(text: Optional[str], skills_db: Set[str]) -> Set[str]:
    """Extracts technical skills from text using word boundary matching.

    Supports both single-word skills (e.g. 'python', 'java', 'sql') and
    multi-word phrases (e.g. 'machine learning', 'data science', 'react js').
    Handles special skill symbols such as 'c++', 'c#', '.net', 'ci/cd', 'node.js'.

    Args:
        text (Optional[str]): Text string to search for skills.
        skills_db (Set[str]): Preloaded set of lowercased technical skills.

    Returns:
        Set[str]: Set of matched lowercased skill names found in the text.
    """
    if not text or not skills_db:
        return set()

    lowercased_text = text.lower()
    matched_skills: Set[str] = set()

    # Sort skills by length descending so longer phrases match first
    sorted_skills = sorted(list(skills_db), key=len, reverse=True)

    for skill in sorted_skills:
        pattern = _compile_skill_pattern(skill)
        if pattern.search(lowercased_text):
            matched_skills.add(skill)

    return matched_skills
