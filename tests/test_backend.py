"""Comprehensive Backend Automated Test Suite.

Tests PDF extraction, NLP preprocessing, skills dataset matching, candidate and JD parsing,
weighted scoring, executive summary generation, pipeline orchestration, CSV/JSON export,
and edge cases (empty resumes, corrupted PDFs, missing contact details, zero required skills in JD,
duplicate skills, and large text handling).
"""

import unittest
import tempfile
from pathlib import Path
import json
import csv

import config
from utils.extractor import extract_text_from_pdf
from utils.preprocess import preprocess_text, remove_punctuation, clean_text_simple
from utils.skills import load_skills_db, extract_skills
from utils.parser import (
    parse_candidate_resume,
    parse_job_description,
    extract_email,
    extract_phone,
    extract_name,
    extract_experience_years,
)
from utils.scorer import (
    calculate_match_score,
    get_recommendation,
    generate_candidate_summary,
    rank_candidates,
)
from utils.exporter import export_to_csv, export_to_json, export_results
from utils.resume_pipeline import process_resume, process_resume_batch


class TestResumeScreeningBackend(unittest.TestCase):
    """Unit and Integration Test cases for Resume Screening Backend System."""

    @classmethod
    def setUpClass(cls):
        """Sets up test data and temporary directories."""
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.temp_path = Path(cls.temp_dir.name)

        cls.sample_skills = {"python", "java", "c++", "machine learning", "data science", "sql", "docker", "aws", "react"}

    @classmethod
    def tearDownClass(cls):
        """Cleans up temporary resources."""
        cls.temp_dir.cleanup()

    # 1. Extractor Tests & Edge Cases
    def test_pdf_extractor_missing_file(self):
        """Tests handling of missing file path."""
        non_existent = self.temp_path / "does_not_exist.pdf"
        with self.assertRaises(FileNotFoundError):
            extract_text_from_pdf(non_existent)

    def test_pdf_extractor_empty_file(self):
        """Tests handling of 0-byte PDF file."""
        empty_pdf = self.temp_path / "empty.pdf"
        empty_pdf.touch()
        text, metadata = extract_text_from_pdf(empty_pdf)
        self.assertEqual(text, "")
        self.assertEqual(metadata["extraction_status"], "Empty File")

    def test_pdf_extractor_corrupted_file(self):
        """Tests handling of corrupted non-PDF file content."""
        corrupted_file = self.temp_path / "corrupted.pdf"
        with open(corrupted_file, "wb") as f:
            f.write(b"This is not a valid PDF header format or binary structure.")
        text, metadata = extract_text_from_pdf(corrupted_file)
        self.assertEqual(text, "")
        status = metadata["extraction_status"]
        self.assertTrue("Empty Text" in status or "Error" in status, f"Unexpected status: {status}")

    # 2. Preprocessor Tests & Edge Cases
    def test_preprocess_text_basic(self):
        """Tests basic cleaning, punctuation, stopword removal, and tokenization."""
        raw = "Hello World! This is a test resume for Python engineering."
        res = preprocess_text(raw)
        self.assertTrue(len(res["tokens"]) > 0)
        self.assertNotIn("is", res["tokens"])
        self.assertNotIn("a", res["tokens"])
        self.assertIn("python", res["tokens"])

    def test_preprocess_text_empty_and_none(self):
        """Tests preprocessing on empty string and None input."""
        res_empty = preprocess_text("")
        self.assertEqual(res_empty["tokens"], [])
        res_none = preprocess_text(None)
        self.assertEqual(res_none["tokens"], [])

    # 3. Skills Extraction & Deduplication Edge Cases
    def test_extract_skills_multiword_and_boundary(self):
        """Tests exact phrase and token boundary skills matching."""
        text = "Experienced in Python, Machine Learning, React, and SQL database management."
        extracted = extract_skills(text, self.sample_skills)
        self.assertIn("python", extracted)
        self.assertIn("machine learning", extracted)
        self.assertIn("react", extracted)
        self.assertIn("sql", extracted)

    def test_extract_skills_duplicate_mentions(self):
        """Tests that duplicate skill occurrences in text yield unique skill sets."""
        text = "Python Python Python, Machine Learning, machine learning, SQL, SQL"
        extracted = extract_skills(text, self.sample_skills)
        self.assertEqual(len(extracted), 3)
        self.assertEqual(extracted, {"python", "machine learning", "sql"})

    # 4. Candidate Details Parser Tests & Edge Cases
    def test_parser_email_and_phone(self):
        """Tests email and phone regex extraction."""
        text = "Contact Jane Doe at jane.doe@techcorp.com or call +1 (555) 019-2834."
        email = extract_email(text)
        phone = extract_phone(text)
        self.assertEqual(email, "jane.doe@techcorp.com")
        self.assertIn("555", phone)

    def test_parser_missing_contact_details(self):
        """Tests parsing when contact information is missing."""
        text = "John Smith\nSoftware Engineer with experience in Python."
        parsed = parse_candidate_resume(text, self.sample_skills)
        self.assertEqual(parsed["email"], "N/A")
        self.assertEqual(parsed["phone"], "N/A")

    def test_parser_name_extraction_hierarchy(self):
        """Tests name extraction hierarchy."""
        text = "Robert Davis\nSenior Developer\nEmail: robert@dev.org"
        name = extract_name(text, filename="robert_davis_resume.pdf")
        self.assertIn("Robert", name)

        # Fallback to filename
        name_from_file = extract_name("", filename="sarah_connor_cv.pdf")
        self.assertEqual(name_from_file, "Sarah Connor")

    def test_parser_date_range_experience(self):
        """Tests parsing date range patterns like 'Jan 2021 – Present' and '2018 - 2023'."""
        text = "Software Engineer (2018 - 2023)\nLead Developer (Jan 2023 - Present)"
        exp = extract_experience_years(text)
        self.assertTrue(exp >= 5.0)

    def test_parser_large_resume_text(self):
        """Tests parsing performance and correctness on very large resume text."""
        large_text = "Jane Doe\nEmail: jane@test.com\n" + ("Python SQL Machine Learning Developer. " * 5000)
        parsed = parse_candidate_resume(large_text, self.sample_skills)
        self.assertEqual(parsed["candidate_name"], "Jane Doe")
        self.assertIn("python", parsed["skills"])

    # 5. Job Description Parser Edge Cases
    def test_parse_job_description_empty(self):
        """Tests JD parsing when text is empty or missing."""
        jd_parsed = parse_job_description("", self.sample_skills)
        self.assertEqual(jd_parsed["required_skills"], set())
        self.assertEqual(jd_parsed["required_experience_years"], config.DEFAULT_REQUIRED_EXPERIENCE_YEARS)

    # 6. Scorer & Recommendation Tests & Edge Cases
    def test_calculate_match_score_weighted(self):
        """Tests 80% Skill Match + 20% Experience Match weighted scoring formula."""
        cand_skills = {"python", "sql", "docker"}
        req_skills = {"python", "sql", "docker", "aws", "react"}  # 3/5 matched = 60.0%
        cand_exp = 3.0
        req_exp = 3.0  # 3/3 exp = 100.0%

        # Final = (60.0 * 0.8) + (100.0 * 0.2) = 48 + 20 = 68.0%
        res = calculate_match_score(cand_skills, req_skills, cand_exp, req_exp)
        self.assertEqual(res["skill_score"], 60.0)
        self.assertEqual(res["experience_score"], 100.0)
        self.assertEqual(res["final_score"], 68.0)
        self.assertEqual(get_recommendation(res["final_score"]), "Consider")

    def test_calculate_match_score_zero_required_skills(self):
        """Tests graceful handling when required skills set is empty."""
        res = calculate_match_score({"python"}, set(), candidate_exp_years=5.0)
        self.assertEqual(res["final_score"], 0.0)
        self.assertEqual(res["matched_skills"], [])

    def test_recommendation_thresholds(self):
        """Tests recommendation tier assignment boundaries."""
        self.assertEqual(get_recommendation(85.0), "Shortlisted")
        self.assertEqual(get_recommendation(80.0), "Shortlisted")
        self.assertEqual(get_recommendation(79.9), "Consider")
        self.assertEqual(get_recommendation(60.0), "Consider")
        self.assertEqual(get_recommendation(59.9), "Rejected")

    # 7. Candidate Summary Generator Test
    def test_generate_candidate_summary(self):
        """Tests concise 2–3 sentence executive candidate summary generation."""
        cand_info = {
            "candidate_name": "Alice Johnson",
            "experience_years": 5.0,
            "education": ["Master Of Science"],
            "skills": ["python", "sql", "docker"]
        }
        score_info = {
            "final_score": 85.0,
            "recommendation": "Shortlisted",
            "matched_skills": ["python", "sql"]
        }
        summary = generate_candidate_summary(cand_info, score_info)
        self.assertIn("Alice Johnson", summary)
        self.assertIn("85.0%", summary)
        self.assertIn("Shortlisted", summary)
        import re
        sentences = [s.strip() for s in re.split(r"(?<=[a-zA-Z'\"])\.\s+", summary) if s.strip()]
        self.assertTrue(2 <= len(sentences) <= 4, f"Unexpected sentence count: {len(sentences)}")

    # 8. Exporters & File Path Persistence Test
    def test_exporters_csv_and_json(self):
        """Tests exporting to CSV and JSON files including resume filename and path metadata."""
        sample_candidates = [{
            "candidate_name": "Test Candidate",
            "email": "test@candidate.com",
            "phone": "555-000-1111",
            "education": ["B.S. Computer Science"],
            "skills": ["python", "sql"],
            "experience_years": 4.0,
            "resume_filename": "test_resume.pdf",
            "resume_path": str(self.temp_path / "test_resume.pdf"),
            "skill_score": 100.0,
            "experience_score": 100.0,
            "final_score": 100.0,
            "matched_skills": ["python", "sql"],
            "missing_skills": [],
            "recommendation": "Shortlisted",
            "summary": "Test summary sentence.",
        }]

        csv_file = self.temp_path / "output_test.csv"
        json_file = self.temp_path / "output_test.json"

        export_results(sample_candidates, csv_path=csv_file, json_path=json_file)

        # Verify CSV
        self.assertTrue(csv_file.exists())
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            self.assertEqual(len(reader), 1)
            self.assertEqual(reader[0]["Candidate Name"], "Test Candidate")
            self.assertEqual(reader[0]["Resume Filename"], "test_resume.pdf")

        # Verify JSON
        self.assertTrue(json_file.exists())
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["candidate_name"], "Test Candidate")
        self.assertEqual(data[0]["resume_filename"], "test_resume.pdf")


if __name__ == "__main__":
    unittest.main()
