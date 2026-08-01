# 📄 Resume Screening Automation System

An AI-powered, end-to-end **Resume Screening Automation System** that automates multi-resume PDF parsing, NLP-based skill extraction, candidate ranking, weighted match scoring, and shortlisting. Built with **Python**, **spaCy**, **NLTK**, and **Streamlit**.

---

## 📌 Project Overview

Modern recruitment workflows suffer from manual resume screening bottlenecks, inconsistent candidate evaluations, and high time-to-hire metrics. 

The **Resume Screening Automation System** was built to solve these challenges by providing an intelligent, scalable, and reproducible backend screening engine coupled with an intuitive interactive web dashboard. It enables hiring teams to upload job descriptions alongside hundreds of PDF resumes, automatically extract key applicant metadata (Name, Email, Phone, Education, Experience Years, Skills), score candidates using an extensible weighted algorithm (80% Skill Match + 20% Experience Match), generate executive applicant summaries, and export actionable CSV and JSON candidate rankings.

---

## ✨ Features

- **📄 Multi-PDF Resume Upload**: Extract text seamlessly using `pdfplumber` with automatic `pypdf` / `PyPDF2` fallbacks.
- **📋 Job Description Parser**: Parse required skills and target experience requirements directly from plain text files or raw text input.
- **🔤 NLP Preprocessing Pipeline**: Perform lowercasing, punctuation stripping, stopword removal, tokenization, and lemmatization using `spaCy` and `NLTK`.
- **👤 Hierarchical Candidate Parser**: Robust candidate Name extraction (spaCy `PERSON` NER $\rightarrow$ Top lines $\rightarrow$ Filename stem), Email/Phone regex, Education degree detection, and Date-Range Experience calculation (`"Jan 2021 – Present"`, `"2018 - 2023"`).
- **🛠️ Categorized Skill Extraction**: Match single-word and multi-word technical skills against a preloaded dataset of 300+ skills using compiled regex boundary phrase matching.
- **⚖️ Extensible Weighted Candidate Scoring**:
  $$\text{Final Score} = (\text{Skill Match Score} \times 0.80) + (\text{Experience Score} \times 0.20)$$
- **🏆 Candidate Ranking & Recommendation**: Categorize applicants into `Shortlisted` ($\ge 80\%$), `Consider` ($60 - 79\%$), and `Rejected` ($< 60\%$).
- **✍️ Executive Candidate Summary**: Automatically generate concise 2–3 sentence executive profile summaries.
- **📊 Interactive Streamlit Dashboard**: Clean web UI featuring summary metrics, searchable candidate tables, interactive applicant detail cards, and score breakdowns.
- **📥 CSV & JSON Export**: One-click downloading of candidate screening results formatted as `shortlisted_candidates.csv` and `shortlisted_candidates.json`.

---

## 🛠️ Tech Stack

| Domain | Technologies & Libraries |
| :--- | :--- |
| **Language** | Python 3.11+ |
| **Web Dashboard** | Streamlit |
| **NLP & Text Preprocessing** | spaCy (`en_core_web_sm`), NLTK, Scikit-learn |
| **PDF Extraction Engine** | pdfplumber, PyPDF2 / pypdf |
| **Data Processing & I/O** | Pandas, CSV, JSON |
| **Testing & Verification** | Python `unittest` |

---

## 📁 Project Architecture

```
ResumeScreeningAutomation/
│
├── app.py                 # Streamlit Frontend Web Application
├── config.py              # Centralized configuration (weights, paths, thresholds, logging)
├── main.py                # CLI execution pipeline entry point
├── requirements.txt       # Production python dependency specifications
├── README.md              # Project documentation
│
├── utils/
│   ├── __init__.py        # Package exports
│   ├── logger.py          # Standardized Python logging utility
│   ├── extractor.py       # PDF text extraction (pdfplumber + PyPDF2 fallback)
│   ├── preprocess.py      # NLP text cleaning, tokenization, & lemmatization
│   ├── skills.py          # Categorized skills dataset loader & phrase matcher
│   ├── parser.py          # Candidate details & Job Description parser
│   ├── scorer.py          # Weighted match scoring, ranking & summary generator
│   ├── resume_pipeline.py # Pipeline orchestrator (process_resume & process_resume_batch)
│   └── exporter.py        # CSV & JSON report export engine
│
├── data/
│   ├── skills.txt         # Predefined technical skills dataset (300+ skills)
│   └── sample_job_description.txt
│
├── tests/
│   └── test_backend.py    # 18 automated unit & edge-case integration tests
│
└── output/                # Output directory for exported reports
    ├── shortlisted_candidates.csv
    └── shortlisted_candidates.json
```

---

## 🔄 Workflow

```
       [ Upload Job Description (.txt) ]       [ Upload Resume PDFs (.pdf) ]
                      │                                      │
                      └──────────────────┬───────────────────┘
                                         ▼
                             [ PDF Text Extraction ]
                             (pdfplumber / PyPDF2)
                                         ▼
                            [ NLP Preprocessing ]
                       (spaCy & NLTK Lemmatization)
                                         ▼
                            [ Candidate Parsing ]
                   (Name, Email, Phone, Edu, Date Ranges)
                                         ▼
                             [ Skill Phrase Matching ]
                            (300+ Technical Skills)
                                         ▼
                            [ Weighted Score Calc ]
                         (80% Skills + 20% Experience)
                                         ▼
                             [ Candidate Ranking ]
                     (Shortlisted / Consider / Rejected)
                                         ▼
                          [ Interactive Dashboard ]
                           (Streamlit Web Interface)
                                         ▼
                           [ Report Generation ]
                            (CSV & JSON Export)
```

---

## 🚀 Installation & Usage

### 1. Clone the Repository

```bash
git clone https://github.com/SwethaBattula/resume-screening-automation-system.git
cd resume-screening-automation-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Run the Streamlit Web Application

```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

### 4. Run CLI Entry Point (Optional)

```bash
python main.py
```

### 5. Run Automated Test Suite

```bash
python -m unittest discover -s tests
```

---

## 🖼️ Screenshots

> *Add application screenshots below once deployed.*

| Screening Dashboard | Candidate Detail Card |
| :---: | :---: |
| ![Dashboard Placeholder](https://via.placeholder.com/800x450.png?text=Streamlit+Dashboard+Overview) | ![Detail Card Placeholder](https://via.placeholder.com/800x450.png?text=Candidate+Detail+Card) |

---

## 🔮 Future Enhancements

- **📷 OCR Integration**: Integrate Tesseract OCR (`pytesseract` / `pdf2image`) for scanned image-based PDF resumes.
- **🧠 Semantic Vector Search**: Embed candidate profiles and job descriptions using Transformer embeddings (e.g. Sentence-BERT) for contextual semantic matching beyond keyword/phrase matching.
- **🤖 LLM Integration**: Incorporate Large Language Models (Gemini / OpenAI API) for automated interview question generation and deep qualitative candidate summaries.
- **⚡ ATS Platform Integration**: Build REST APIs (FastAPI) and webhooks to connect with Applicant Tracking Systems like Greenhouse, Lever, or Workday.
- **☁️ Cloud Deployment**: Containerize with Docker and deploy to AWS ECS / GCP Cloud Run with PostgreSQL database persistence.

---

## 👩‍💻 Author

**Swetha Battula**
- **GitHub**: [@SwethaBattula](https://github.com/SwethaBattula)
