"""Results Exporter Module.

Exports evaluated candidate screening results to CSV (output/shortlisted_candidates.csv)
and JSON (output/shortlisted_candidates.json) formats using standard Python libraries.
"""

from pathlib import Path
import json
import csv
from typing import List, Dict, Any, Union, Tuple, Optional
import config
from utils.logger import setup_logger

logger = setup_logger("utils.exporter")


def prepare_export_records(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transforms raw candidate pipeline dictionaries into flat export records.

    Args:
        candidates (List[Dict[str, Any]]): Processed candidate dictionaries.

    Returns:
        List[Dict[str, Any]]: Flattened records suitable for CSV/JSON export.
    """
    records: List[Dict[str, Any]] = []

    for cand in candidates:
        education_str = ", ".join(cand.get("education", []))
        matched_skills_str = ", ".join(cand.get("matched_skills", []))
        all_skills_str = ", ".join(cand.get("skills", []))

        record = {
            "Candidate Name": cand.get("candidate_name", "Unknown Candidate"),
            "Email": cand.get("email", "N/A"),
            "Phone": cand.get("phone", "N/A"),
            "Education": education_str,
            "Experience (Years)": cand.get("experience_years", 0.0),
            "Matched Skills": matched_skills_str,
            "All Skills": all_skills_str,
            "Skill Match Score": cand.get("skill_score", 0.0),
            "Experience Score": cand.get("experience_score", 0.0),
            "Final Score": cand.get("final_score", 0.0),
            "Recommendation": cand.get("recommendation", "N/A"),
            "Summary": cand.get("summary", ""),
            "Resume Filename": cand.get("resume_filename", "N/A"),
            "File Path": cand.get("resume_path", "N/A"),
        }
        records.append(record)

    return records


def export_to_csv(
    candidates: List[Dict[str, Any]],
    output_path: Optional[Union[str, Path]] = None
) -> Path:
    """Exports candidate evaluation results to a CSV file.

    Args:
        candidates (List[Dict[str, Any]]): Processed candidate dictionaries.
        output_path (Optional[Union[str, Path]]): Target CSV file path.
            Defaults to config.DEFAULT_CSV_OUTPUT if None.

    Returns:
        Path: Path to the generated CSV file.
    """
    target_path = Path(output_path or config.DEFAULT_CSV_OUTPUT).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    records = prepare_export_records(candidates)
    fieldnames = [
        "Candidate Name",
        "Email",
        "Phone",
        "Education",
        "Experience (Years)",
        "Matched Skills",
        "All Skills",
        "Skill Match Score",
        "Experience Score",
        "Final Score",
        "Recommendation",
        "Summary",
        "Resume Filename",
        "File Path",
    ]

    try:
        with open(target_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(records)
        logger.info(f"Successfully exported {len(records)} candidate record(s) to CSV: {target_path}")
    except Exception as exc:
        logger.error(f"Failed to export results to CSV at {target_path}: {exc}")
        raise

    return target_path


def export_to_json(
    candidates: List[Dict[str, Any]],
    output_path: Optional[Union[str, Path]] = None
) -> Path:
    """Exports candidate evaluation results to a JSON file.

    Args:
        candidates (List[Dict[str, Any]]): Processed candidate dictionaries.
        output_path (Optional[Union[str, Path]]): Target JSON file path.
            Defaults to config.DEFAULT_JSON_OUTPUT if None.

    Returns:
        Path: Path to the generated JSON file.
    """
    target_path = Path(output_path or config.DEFAULT_JSON_OUTPUT).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(candidates, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully exported {len(candidates)} candidate record(s) to JSON: {target_path}")
    except Exception as exc:
        logger.error(f"Failed to export results to JSON at {target_path}: {exc}")
        raise

    return target_path


def export_results(
    candidates: List[Dict[str, Any]],
    csv_path: Optional[Union[str, Path]] = None,
    json_path: Optional[Union[str, Path]] = None
) -> Tuple[Path, Path]:
    """Convenience function to export candidate evaluation results to both CSV and JSON formats.

    Args:
        candidates (List[Dict[str, Any]]): Processed candidate dictionaries.
        csv_path (Optional[Union[str, Path]]): Target CSV file path.
        json_path (Optional[Union[str, Path]]): Target JSON file path.

    Returns:
        Tuple[Path, Path]: Generated (CSV Path, JSON Path).
    """
    csv_file = export_to_csv(candidates, csv_path)
    json_file = export_to_json(candidates, json_path)
    return csv_file, json_file
