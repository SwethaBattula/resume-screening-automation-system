"""Results Exporter Module.

Exports evaluated candidate screening results to CSV and JSON formats (files or strings)
using standard Python libraries.
"""

from pathlib import Path
import json
import csv
import io
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


def format_candidate_table_records(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Formats candidate records into clean representation for UI tables.

    Args:
        candidates (List[Dict[str, Any]]): Processed candidate dictionaries.

    Returns:
        List[Dict[str, Any]]: Formatted table records.
    """
    table_records: List[Dict[str, Any]] = []
    for r in candidates:
        table_records.append({
            "Candidate Name": r.get("candidate_name", "Unknown"),
            "Email": r.get("email", "N/A"),
            "Experience": f"{r.get('experience_years', 0.0)} yrs",
            "Matched Skills": ", ".join(r.get("matched_skills", [])) if r.get("matched_skills") else "None",
            "Final Score": f"{r.get('final_score', 0.0)}%",
            "Recommendation": r.get("recommendation", "N/A"),
            "Resume Filename": r.get("resume_filename", "N/A"),
        })
    return table_records


def generate_csv_string(candidates: List[Dict[str, Any]]) -> str:
    """Generates CSV formatted string from candidate results.

    Args:
        candidates (List[Dict[str, Any]]): Processed candidate dictionaries.

    Returns:
        str: CSV content string.
    """
    records = prepare_export_records(candidates)
    if not records:
        return ""

    buffer = io.StringIO()
    fieldnames = list(records[0].keys())
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(records)
    return buffer.getvalue()


def generate_json_string(candidates: List[Dict[str, Any]]) -> str:
    """Generates JSON formatted string from candidate results.

    Args:
        candidates (List[Dict[str, Any]]): Processed candidate dictionaries.

    Returns:
        str: Formatted JSON content string.
    """
    return json.dumps(candidates, indent=2, ensure_ascii=False)


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

    csv_content = generate_csv_string(candidates)

    try:
        with open(target_path, "w", newline="", encoding="utf-8") as f:
            f.write(csv_content)
        logger.info(f"Successfully exported {len(candidates)} candidate record(s) to CSV: {target_path}")
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

    json_content = generate_json_string(candidates)

    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(json_content)
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
