"""Streamlit Frontend Application for Resume Screening Automation System.

Integrates seamlessly with the backend modules (utils.resume_pipeline, utils.skills, utils.exporter)
to provide an interactive web interface for uploading Job Descriptions and PDF resumes,
visualizing candidate match scores, reading candidate summaries, and downloading CSV/JSON reports.
"""

import tempfile
from pathlib import Path
import json
import csv
import io
from typing import List, Dict, Any

import streamlit as st

# Backend Imports
from utils.skills import load_skills_db
from utils.resume_pipeline import process_resume_batch
from utils.exporter import prepare_export_records
import config


# Page Configuration
st.set_page_config(
    page_title="Resume Screening Automation System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_cached_skills_db():
    """Loads and caches technical skills database once into memory."""
    return load_skills_db(config.SKILLS_FILE_PATH)


def main():
    """Main Streamlit Frontend Application Execution."""
    st.title("📄 Resume Screening Automation System")
    st.caption("AI-Powered Resume Parsing, NLP Skill Matching & Candidate Ranking System")

    # Load Skills DB
    skills_db = get_cached_skills_db()

    # Sidebar Controls
    st.sidebar.header("📋 Screening Setup")
    st.sidebar.markdown("Upload a Job Description and candidate PDF resumes to start screening.")

    # 1. Job Description Uploader
    uploaded_jd_file = st.sidebar.file_uploader(
        "Upload Job Description (.txt)",
        type=["txt"],
        help="Select a plain text file containing job requirements and required skills."
    )

    # 2. Resumes Uploader
    uploaded_resume_files = st.sidebar.file_uploader(
        "Upload Resume PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="Select one or multiple candidate PDF resume files."
    )

    # Sidebar Info Box
    st.sidebar.divider()
    st.sidebar.markdown("### ⚙️ Scoring Architecture")
    st.sidebar.info(
        "• **Skill Match (80%)**: Exact & phrase-boundary technical skill overlap.\n"
        "• **Experience Match (20%)**: Candidate experience vs target JD experience.\n"
        "• **Shortlisted**: Score ≥ 80%\n"
        "• **Consider**: 60% ≤ Score < 80%\n"
        "• **Rejected**: Score < 60%"
    )

    # Start Screening Button
    start_screening = st.sidebar.button("🚀 Start Screening", type="primary", use_container_width=True)

    # Store state for persistent results across re-renders
    if "results" not in st.session_state:
        st.session_state["results"] = None

    # Trigger Processing Workflow
    if start_screening:
        # Error Check 1: Missing Job Description
        if not uploaded_jd_file:
            st.error("⚠️ Missing Job Description! Please upload a valid .txt Job Description file in the sidebar.")
            return

        # Error Check 2: No Resumes Uploaded
        if not uploaded_resume_files:
            st.error("⚠️ No Resumes Uploaded! Please upload at least one PDF resume file to screen.")
            return

        # Process uploaded files in a temporary directory
        with st.spinner("Preparing temporary files for backend pipeline..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Save JD File
                jd_temp_file = temp_path / uploaded_jd_file.name
                with open(jd_temp_file, "wb") as f:
                    f.write(uploaded_jd_file.getvalue())

                # Save Resume PDF Files
                pdf_paths: List[Path] = []
                progress_bar = st.progress(0, text="Saving uploaded resumes...")
                num_files = len(uploaded_resume_files)

                for idx, resume_file in enumerate(uploaded_resume_files, 1):
                    resume_temp_path = temp_path / resume_file.name
                    with open(resume_temp_path, "wb") as f:
                        f.write(resume_file.getvalue())
                    pdf_paths.append(resume_temp_path)
                    progress_bar.progress(
                        int((idx / num_files) * 30),
                        text=f"Uploaded {idx}/{num_files}: {resume_file.name}"
                    )

                # Run Backend Screening Pipeline
                progress_bar.progress(40, text="Running PDF extraction & NLP preprocessing...")
                
                try:
                    results = process_resume_batch(
                        pdf_paths=pdf_paths,
                        job_description=jd_temp_file,
                        skills_db=skills_db,
                        export=False  # Handled in Streamlit session state
                    )
                    progress_bar.progress(100, text="Screening completed successfully!")
                    st.session_state["results"] = results
                    st.success(f"🎉 Successfully screened {len(results)} candidate resume(s)!")
                except Exception as exc:
                    st.error(f"❌ An error occurred during screening pipeline execution: {str(exc)}")
                    return

    # Display Results if available
    results = st.session_state["results"]

    if not results:
        st.info("👈 Please upload a Job Description and PDF Resumes in the sidebar, then click **Start Screening**.")
        return

    # Check for extraction warnings (empty / corrupted files)
    warnings = [r for r in results if r.get("extraction_status") in ("Empty File", "Empty Text") or "Error" in r.get("extraction_status", "")]
    if warnings:
        for w in warnings:
            st.warning(f"⚠️ Warning for file **{w['resume_filename']}**: Status = '{w['extraction_status']}'. Minimal or no text extracted.")

    st.divider()

    # Executive Overview Metrics
    total_candidates = len(results)
    shortlisted = len([r for r in results if r["recommendation"] == "Shortlisted"])
    consider = len([r for r in results if r["recommendation"] == "Consider"])
    rejected = len([r for r in results if r["recommendation"] == "Rejected"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Candidates", total_candidates)
    m2.metric("Shortlisted (≥80%)", shortlisted, delta_color="normal")
    m3.metric("Consider (60-79%)", consider, delta_color="off")
    m4.metric("Rejected (<60%)", rejected, delta_color="inverse")

    st.divider()

    # Main Tab Layout: Results Table & Candidate Detail View
    tab_table, tab_details = st.tabs(["📊 Candidate Rankings Table", "🔍 Detailed Candidate Card"])

    # TAB 1: Candidates Table
    with tab_table:
        st.subheader("Candidate Screening Results")

        # Format dataframe for clean Streamlit table display
        table_records = []
        for r in results:
            table_records.append({
                "Candidate Name": r["candidate_name"],
                "Email": r["email"],
                "Experience": f"{r['experience_years']} yrs",
                "Matched Skills": ", ".join(r["matched_skills"]) if r["matched_skills"] else "None",
                "Final Score": f"{r['final_score']}%",
                "Recommendation": r["recommendation"],
                "Resume Filename": r["resume_filename"],
            })

        st.dataframe(
            table_records,
            column_config={
                "Final Score": st.column_config.TextColumn("Final Score", help="Weighted 80% Skill + 20% Exp Match Score"),
                "Recommendation": st.column_config.TextColumn("Recommendation"),
            },
            use_container_width=True,
            hide_index=True
        )

        # Download Buttons Section
        st.subheader("📥 Export Results")
        d1, d2 = st.columns(2)

        # Prepare CSV Data
        flat_records = prepare_export_records(results)
        csv_buffer = io.StringIO()
        fieldnames = list(flat_records[0].keys()) if flat_records else []
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_records)

        d1.download_button(
            label="📄 Download CSV Report",
            data=csv_buffer.getvalue(),
            file_name="shortlisted_candidates.csv",
            mime="text/csv",
            use_container_width=True
        )

        # Prepare JSON Data
        json_str = json.dumps(results, indent=2, ensure_ascii=False)

        d2.download_button(
            label="📦 Download JSON Report",
            data=json_str,
            file_name="shortlisted_candidates.json",
            mime="application/json",
            use_container_width=True
        )

    # TAB 2: Candidate Detail Card
    with tab_details:
        st.subheader("Detailed Candidate Profile")

        candidate_names = [r["candidate_name"] for r in results]
        selected_name = st.selectbox("Select a Candidate:", candidate_names)

        # Find selected candidate record
        cand = next((r for r in results if r["candidate_name"] == selected_name), results[0])

        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown(f"### **{cand['candidate_name']}**")
            st.info(f"**Executive Summary:**\n\n{cand['summary']}")

            st.markdown("#### **Education**")
            if cand["education"]:
                for edu in cand["education"]:
                    st.markdown(f"• {edu}")
            else:
                st.caption("No specific degree keywords detected.")

            st.markdown("#### **Skills Overview**")
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.markdown("**Matched Skills (JD Overlap):**")
                if cand["matched_skills"]:
                    for s in cand["matched_skills"]:
                        st.markdown(f"✅ `{s}`")
                else:
                    st.caption("No matching JD skills found.")
            with s_col2:
                st.markdown("**Missing Required Skills:**")
                if cand["missing_skills"]:
                    for s in cand["missing_skills"]:
                        st.markdown(f"❌ `{s}`")
                else:
                    st.caption("No missing skills!")

        with col_right:
            st.markdown("#### **Screening Scorecard**")

            rec = cand["recommendation"]
            if rec == "Shortlisted":
                st.success(f"### Status: {rec}")
            elif rec == "Consider":
                st.warning(f"### Status: {rec}")
            else:
                st.error(f"### Status: {rec}")

            st.metric("Final Score", f"{cand['final_score']}%")
            st.metric("Skill Match Score", f"{cand['skill_score']}%")
            st.metric("Experience Score", f"{cand['experience_score']}%")
            st.metric("Total Experience", f"{cand['experience_years']} Years")

            st.divider()
            st.markdown("**Contact & File Metadata**")
            st.text(f"Email: {cand['email']}")
            st.text(f"Phone: {cand['phone']}")
            st.text(f"File:  {cand['resume_filename']}")


if __name__ == "__main__":
    main()
