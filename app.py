"""Streamlit Frontend Application for Resume Screening Automation System.

Provides a recruiter-style dashboard presentation layer built with native Streamlit components
(st.columns, st.container, st.markdown, st.write, st.progress) and custom CSS styling.
Does not import pandas directly or indirectly.
"""

import tempfile
from pathlib import Path
from typing import List, Dict, Any

import streamlit as st

# Backend Imports
from utils.skills import load_skills_db
from utils.resume_pipeline import process_resume_batch
from utils.exporter import (
    format_candidate_table_records,
    generate_csv_string,
    generate_json_string,
)
from utils.scorer import get_screening_summary_metrics
import config


# Page Configuration
st.set_page_config(
    page_title="Resume Screening Automation System",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Inject Custom CSS for Modern Dark Dashboard & Streamlit Chrome Removal
st.markdown(
    """
    <style>
    /* Hide Streamlit Chrome & Headers */
    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; display: none; }
    [data-testid="stToolbar"] { visibility: hidden; display: none; }
    [data-testid="stStatusWidget"] { visibility: hidden; display: none; }
    [data-testid="stDecoration"] { display: none; }
    .stDeployButton { display: none !important; }
    button[kind="header"] { display: none !important; }
    [data-testid="stAppDeployButton"] { display: none !important; }

    /* Main Layout Adjustments */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }
    
    /* Hero Header Banner */
    .hero-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-top: 8px;
        margin-bottom: 16px;
    }
    .tech-tag {
        background-color: #334155;
        color: #e2e8f0;
        font-size: 0.8rem;
        padding: 4px 10px;
        border-radius: 6px;
        display: inline-block;
        margin-right: 8px;
        font-weight: 500;
    }

    /* Dashboard Cards */
    .card-total {
        background-color: #1e293b;
        border: 1px solid #475569;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .card-shortlisted {
        background-color: rgba(34, 197, 94, 0.1);
        border: 1px solid #22c55e;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .card-consider {
        background-color: rgba(245, 158, 11, 0.1);
        border: 1px solid #f59e0b;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .card-rejected {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .card-label {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    .card-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 4px;
    }

    /* Candidate Initials Avatar Circle */
    .avatar-circle {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: #ffffff;
        font-weight: 700;
        font-size: 0.95rem;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 1px solid #60a5fa;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Status Badges */
    .badge {
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-shortlisted {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid #22c55e;
    }
    .badge-consider {
        background-color: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid #f59e0b;
    }
    .badge-rejected {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid #ef4444;
    }

    /* Skill Tags */
    .skill-tag-matched {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid #3b82f6;
        font-size: 0.8rem;
        padding: 3px 10px;
        border-radius: 6px;
        display: inline-block;
        margin: 3px;
        font-weight: 500;
    }
    .skill-tag-missing {
        background-color: rgba(239, 68, 68, 0.1);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.3);
        font-size: 0.8rem;
        padding: 3px 10px;
        border-radius: 6px;
        display: inline-block;
        margin: 3px;
    }
    .skill-tag-more {
        background-color: #334155;
        color: #cbd5e1;
        border: 1px solid #475569;
        font-size: 0.78rem;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        margin: 3px;
        font-weight: 500;
    }

    /* Footer */
    .app-footer {
        margin-top: 48px;
        padding-top: 20px;
        border-top: 1px solid #334155;
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_cached_skills_db():
    """Loads and caches technical skills database once into memory."""
    return load_skills_db(config.SKILLS_FILE_PATH)


def get_candidate_initials(name: str) -> str:
    """Generates 2-letter uppercase initials from candidate name."""
    if not name or name == "Unknown Candidate":
        return "UC"
    parts = [p.strip() for p in name.split() if p.strip()]
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[-1][0]}".upper()
    elif len(parts) == 1:
        return parts[0][:2].upper()
    return "CD"


def main():
    """Main Streamlit Frontend Application Execution."""
    
    # 1. Professional Hero Section
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-title">Resume Screening Automation System</div>
            <div class="hero-subtitle">
                An AI-powered system for automated resume parsing, NLP technical skill extraction, weighted candidate scoring, and candidate ranking.
            </div>
            <div>
                <span class="tech-tag">Python</span>
                <span class="tech-tag">Streamlit</span>
                <span class="tech-tag">spaCy</span>
                <span class="tech-tag">NLTK</span>
                <span class="tech-tag">PDF Processing</span>
                <span class="tech-tag">Scikit-learn</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Load Skills DB
    skills_db = get_cached_skills_db()

    # Sidebar Controls
    st.sidebar.markdown("### Screening Setup")
    st.sidebar.markdown("Upload a Job Description and PDF resumes to execute automated candidate screening.")

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

    # Compact Sidebar Info Cards
    st.sidebar.divider()
    st.sidebar.markdown("### Screening Criteria")
    st.sidebar.markdown(
        """
        <div style="background-color: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 12px;">
            <div style="font-size: 0.85rem; font-weight: 600; color: #38bdf8;">Weighted Scoring Model</div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 4px;">• Technical Skill Match: <b>80%</b></div>
            <div style="font-size: 0.8rem; color: #94a3b8;">• Experience Match: <b>20%</b></div>
        </div>
        <div style="background-color: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155;">
            <div style="font-size: 0.85rem; font-weight: 600; color: #38bdf8;">Threshold Boundaries</div>
            <div style="font-size: 0.8rem; color: #4ade80; margin-top: 4px;">• Shortlisted: Score ≥ 80%</div>
            <div style="font-size: 0.8rem; color: #fbbf24;">• Consider: 60% ≤ Score < 80%</div>
            <div style="font-size: 0.8rem; color: #f87171;">• Rejected: Score < 60%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    # Start Screening Button
    start_screening = st.sidebar.button("Start Screening", type="primary", use_container_width=True)

    # Store state for persistent results across re-renders
    if "results" not in st.session_state:
        st.session_state["results"] = None

    # Trigger Processing Workflow
    if start_screening:
        if not uploaded_jd_file:
            st.error("Missing Job Description! Please upload a valid .txt Job Description file in the sidebar.")
            return

        if not uploaded_resume_files:
            st.error("No Resumes Uploaded! Please upload at least one PDF resume file to screen.")
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
                        export=False
                    )
                    progress_bar.progress(100, text="Screening completed successfully!")
                    st.session_state["results"] = results
                    st.success(f"Successfully screened {len(results)} candidate resume(s)!")
                except Exception as exc:
                    st.error(f"An error occurred during screening pipeline execution: {str(exc)}")
                    return

    # Display Results if available
    results = st.session_state["results"]

    if not results:
        st.info("Please upload a Job Description and PDF Resumes in the sidebar, then click 'Start Screening'.")
        # Render Footer
        st.markdown(
            """
            <div class="app-footer">
                <b>Resume Screening Automation System</b><br>
                Built with Python, Streamlit, spaCy, and NLP<br>
                Developed by <b>Swetha Battula</b>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # Check for extraction warnings
    warnings = [r for r in results if r.get("extraction_status") in ("Empty File", "Empty Text") or "Error" in r.get("extraction_status", "")]
    if warnings:
        for w in warnings:
            st.warning(f"Warning for file '{w['resume_filename']}': Status = '{w['extraction_status']}'. Minimal or no text extracted.")

    st.divider()

    # Executive Overview Metric Cards
    metrics = get_screening_summary_metrics(results)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="card-total">
                <div class="card-label">Total Candidates</div>
                <div class="card-value">{metrics['total']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        st.markdown(
            f"""
            <div class="card-shortlisted">
                <div class="card-label" style="color: #4ade80;">Shortlisted (≥80%)</div>
                <div class="card-value" style="color: #4ade80;">{metrics['shortlisted']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="card-consider">
                <div class="card-label" style="color: #fbbf24;">Consider (60-79%)</div>
                <div class="card-value" style="color: #fbbf24;">{metrics['consider']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="card-rejected">
                <div class="card-label" style="color: #f87171;">Rejected (<60%)</div>
                <div class="card-value" style="color: #f87171;">{metrics['rejected']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # Main Tab Layout: Recruiter Candidate Rankings Dashboard & Candidate Detail Card
    tab_rankings, tab_details = st.tabs(["Candidate Rankings", "Detailed Candidate Card"])

    # TAB 1: Recruiter Candidate Rankings Cards
    with tab_rankings:
        st.subheader("Candidate Rankings")

        for rank_idx, cand in enumerate(results, 1):
            with st.container():
                c_left, c_mid, c_right = st.columns([1.2, 3.8, 4.0])
                
                # Initials Avatar & Rank Number
                initials = get_candidate_initials(cand["candidate_name"])
                with c_left:
                    st.markdown(
                        f"""
                        <div style="display: flex; align-items: center; gap: 12px; padding-top: 8px;">
                            <span style="font-weight: 700; color: #94a3b8; font-size: 1.1rem;">#{rank_idx}</span>
                            <div class="avatar-circle">{initials}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Candidate Name, Experience & Progress Bar
                with c_mid:
                    st.markdown(f"#### **{cand['candidate_name']}**")
                    st.caption(f"Experience: **{cand['experience_years']} Years** | File: `{cand['resume_filename']}`")
                    
                    score_val = float(cand["final_score"])
                    st.progress(min(max(score_val / 100.0, 0.0), 1.0), text=f"Match Score: {score_val}%")
                
                # Recommendation Status Pill & Top 5 Matched Skills
                with c_right:
                    rec = cand["recommendation"]
                    if rec == "Shortlisted":
                        pill_html = '<span class="badge badge-shortlisted">Shortlisted</span>'
                    elif rec == "Consider":
                        pill_html = '<span class="badge badge-consider">Consider</span>'
                    else:
                        pill_html = '<span class="badge badge-rejected">Rejected</span>'
                        
                    st.markdown(f'<div style="text-align: right; margin-bottom: 8px;">{pill_html}</div>', unsafe_allow_html=True)
                    
                    matched = cand.get("matched_skills", [])
                    if matched:
                        top_skills = matched[:5]
                        remaining_count = len(matched) - 5
                        tags_html = "".join([f'<span class="skill-tag-matched">{s}</span>' for s in top_skills])
                        if remaining_count > 0:
                            tags_html += f'<span class="skill-tag-more">+{remaining_count} more</span>'
                        st.markdown(f'<div><span style="font-size:0.8rem; color:#94a3b8;">Matched Skills:</span><br>{tags_html}</div>', unsafe_allow_html=True)
                    else:
                        st.caption("No matching JD skills found.")
                
                st.divider()

        # Export Reports Section
        st.subheader("Export Results")
        d1, d2 = st.columns(2)

        csv_data = generate_csv_string(results)
        d1.download_button(
            label="Download CSV Report",
            data=csv_data,
            file_name="shortlisted_candidates.csv",
            mime="text/csv",
            use_container_width=True
        )

        json_data = generate_json_string(results)
        d2.download_button(
            label="Download JSON Report",
            data=json_data,
            file_name="shortlisted_candidates.json",
            mime="application/json",
            use_container_width=True
        )

    # TAB 2: Detailed Candidate Card
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

            st.markdown("#### Education")
            if cand["education"]:
                for edu in cand["education"]:
                    st.markdown(f"• {edu}")
            else:
                st.caption("No specific degree keywords detected.")

            st.markdown("#### Skills Overview")
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.markdown("**Matched Skills (JD Overlap):**")
                if cand["matched_skills"]:
                    tags_html = "".join([f'<span class="skill-tag-matched">{s}</span>' for s in cand["matched_skills"]])
                    st.markdown(tags_html, unsafe_allow_html=True)
                else:
                    st.caption("No matching JD skills found.")
            with s_col2:
                st.markdown("**Missing Required Skills:**")
                if cand["missing_skills"]:
                    tags_html = "".join([f'<span class="skill-tag-missing">{s}</span>' for s in cand["missing_skills"]])
                    st.markdown(tags_html, unsafe_allow_html=True)
                else:
                    st.caption("No missing skills!")

        with col_right:
            st.markdown("#### Screening Scorecard")

            rec = cand["recommendation"]
            if rec == "Shortlisted":
                st.markdown('<div class="badge badge-shortlisted" style="font-size: 1.1rem; margin-bottom: 16px;">Status: Shortlisted</div>', unsafe_allow_html=True)
            elif rec == "Consider":
                st.markdown('<div class="badge badge-consider" style="font-size: 1.1rem; margin-bottom: 16px;">Status: Consider</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="badge badge-rejected" style="font-size: 1.1rem; margin-bottom: 16px;">Status: Rejected</div>', unsafe_allow_html=True)

            st.metric("Final Match Score", f"{cand['final_score']}%")
            st.metric("Skill Match Score", f"{cand['skill_score']}%")
            st.metric("Experience Score", f"{cand['experience_score']}%")
            st.metric("Total Experience", f"{cand['experience_years']} Years")

            st.divider()
            st.markdown("#### Contact & File Metadata")
            st.text(f"Email: {cand['email']}")
            st.text(f"Phone: {cand['phone']}")
            st.text(f"File:  {cand['resume_filename']}")

    # Footer
    st.markdown(
        """
        <div class="app-footer">
            <b>Resume Screening Automation System</b><br>
            Built with Python, Streamlit, spaCy, and NLP<br>
            Developed by <b>Swetha Battula</b>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
