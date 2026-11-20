# 🎬 PromoAI — AI-Powered Microdrama Promo Finder

> **A production-ready prototype for Kuku AI Generalist Campus Placement Assignment (Problem 1: Find the Promos).**  
> Analyzes multi-episode vertical microdrama screenplays and automatically identifies, validates, and ranks high-engagement 20–60 second promotional moments (ads).

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Frontend-Streamlit-red.svg)](https://streamlit.io/)
[![AI Provider](https://img.shields.io/badge/AI-Google%20Gemini%20API-orange.svg)](https://aistudio.google.com/)
[![Tests](https://img.shields.io/badge/Tests-44%2F44%20Passing-brightgreen.svg)]()
[![Architecture](https://img.shields.io/badge/Architecture-Modular%20Monolith-purple.svg)]()

---

## 📌 Table of Contents

1. [Problem Statement & Overview](#-problem-statement--overview)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [Architecture & Project Structure](#-architecture--project-structure)
5. [Deterministic Scoring Formula](#-deterministic-scoring-formula)
6. [Installation & Setup (Windows)](#-installation--setup-windows)
7. [Running the Application](#-running-the-application)
8. [Demonstration Workflow (Interview Ready)](#-demonstration-workflow-interview-ready)
9. [Automated Testing Suite](#-automated-testing-suite)
10. [Security & Verification Guidelines](#-security--verification-guidelines)
11. [Limitations & Future Improvements](#-limitations--future-improvements)

---

## 🎯 Problem Statement & Overview

Microdramas are fast-paced, vertical-format serialized shows (typically 1–2 minutes per episode) published on platforms like **Kuku FM**. To acquire new viewers through social and video ads, marketing teams need engaging 20–60 second promotional clips.

**Manual promo selection is:**
- **Time-consuming:** Editors must comb through dozens of scripts or watch hours of footage.
- **Inconsistent:** Different editors apply different subjective criteria for what makes a strong hook.
- **Prone to missed opportunities:** Subtle cliffhangers, confrontations, and multi-episode narrative arcs are easily overlooked.

**PromoAI solves this by:**
1. Parsing screenplay files episode-by-episode, extracting scenes, timestamps, character dialogue, and dramatic tags.
2. Leveraging Google Gemini LLM for creative semantic discovery (hooks, confrontations, revelations, suspense).
3. Applying **deterministic Python algorithms** to calculate durations, enforce scoring formulas, rank candidates, and cross-reference quotes against the original text.
4. Distinguishing verified source timestamps from estimated ones to eliminate hallucinated content.
5. Providing human-in-the-loop editorial controls (approve, reject, edit, annotate, export).

---

## ✨ Key Features

- **Safe Multi-File Ingestion:** Accepts individual `.txt` files or `.zip` archives. Includes strict zip-slip path traversal guards, executable file filtering, and encoding detection.
- **Screenplay Parser & Timestamp Extractor:** Parses complex screenplay formats containing scene headers, character emotions, dialogue quotes, action notes, camera directions, and real timestamps (`MM:SS.cc`).
- **Semantic Promo Generation:** Synthesizes single-episode and multi-episode dramatic arcs with strong 3-second opening hooks, central conflicts, and unresolved cliffhanger endings.
- **Deterministic Explainable Ranking:** AI scores raw criteria (0–10), but Python strictly computes the weighted composite score and executes sorting. AI never manipulates the final rank.
- **Screenplay Source Verification:** Automatically scans the original screenplay text to verify that every quoted excerpt actually exists, flagging any unsupported claims or duration deviations.
- **Human Quality Review:** Content editors can review candidates, modify titles/hooks/cliffhangers, add comments for video editing teams, and approve or reject promos.
- **Standardized Multi-Format Export:** Downloads full structured JSON, CSV summary tables, or comprehensive Markdown pitch reports.
- **Graceful Offline / Demo Mode:** Seamlessly operates without an API key using realistic synthetic sample data and deterministic rule-based analysis.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.12 | Core programming language |
| **Frontend UI** | Streamlit (>= 1.40.0) | Interactive dashboard and review interface |
| **AI Integration** | `google-genai` SDK | Official Google SDK for Gemini LLM analysis |
| **Data Validation** | Pydantic v2 (>= 2.10) | Strict schema validation for screenplay models & promo candidates |
| **Data Processing** | Pandas (>= 2.0) | Tabular processing, manifests, and CSV export |
| **Environment** | python-dotenv | Secure `.env` configuration management |
| **Testing** | Pytest & pytest-mock | Automated testing with 44 unit & integration tests |

*No complex databases (e.g., MongoDB/PostgreSQL) or heavy full-stack frameworks (e.g., MERN) are introduced — maintaining a clean, easily-deployable modular monolith.*

---

## 📐 Architecture & Project Structure

PromoAI is built around a **separation of concerns** principle:
- **`src/`** contains pure Python business logic and data models.
- **`src/ai/`** isolates LLM interactions behind an abstract provider interface.
- **`app.py`** is a presentation layer that delegates all processing to `src/`.

```
PromoAI/
├── app.py                          # Streamlit web application & UI dashboard
├── requirements.txt                # Python package dependencies
├── README.md                       # Complete documentation & interview guide
├── .env.example                    # Environment variable template
├── .gitignore                      # Secure exclusion of .env, venv, and confidential scripts
│
├── src/                            # Modular application source code
│   ├── __init__.py
│   ├── config.py                   # Central settings, paths, scoring weights, env loading
│   ├── file_processor.py           # TXT/ZIP ingestion, safe extraction, validation
│   ├── screenplay_parser.py        # Pydantic models, timestamp parser, scene extraction
│   ├── scene_analyzer.py           # Deterministic scene intensity, keyword analysis
│   ├── promo_detector.py           # Promo models, AI response builder, ID generator
│   ├── ranking_engine.py           # Deterministic scoring formula & descending sort
│   ├── validator.py                # Source quote verification, duration checks, duplicates
│   ├── output_manager.py           # JSON, CSV, and Markdown export serialization
│   │
│   └── ai/
│       ├── __init__.py
│       ├── base_provider.py        # Abstract AI provider interface & ProviderStatus enum
│       └── gemini_provider.py      # Google Gemini SDK implementation & Demo fallback
│
├── input/
│   └── screenplay/                 # Sample screenplay text files (50 episodes)
│
├── outputs/                        # Saved exports & reports
│   └── .gitkeep
│
├── docs/                           # Project requirements & specifications
│   ├── PRD.md                      # Product Requirements Document
│   ├── TRD.md                      # Technical Requirements Document
│   ├── SRS.md                      # Software Requirements Specification
│   ├── HLD.md                      # High-Level Design
│   ├── LLD.md                      # Low-Level Design
│   ├── Database_Design.md          # Data modeling & schema documentation
│   ├── API_Documentation.md        # API reference documentation
│   └── Test_Plan.md                # Verification records & actual test results
│
└── tests/                          # Pytest automated test suite (44 tests)
    ├── __init__.py
    ├── conftest.py                 # Shared fixtures & mock data
    ├── test_file_processor.py      # Uploads, ZIP security, episode extraction
    ├── test_screenplay_parser.py   # Timestamps, scenes, dialogue, characters
    ├── test_promo_detector.py      # Schema validation, AI response parsing
    ├── test_ranking_engine.py      # Scoring formula math & descending order
    ├── test_validator.py           # Source quotes, duration flags, duplicate detection
    ├── test_output_manager.py      # JSON schema, CSV formatting, Markdown report
    └── test_ai_provider.py         # Missing key fallback, API failures, error codes
```

---

## 🧮 Deterministic Scoring Formula

To ensure full transparency and prevent AI score hallucination, PromoAI enforces a strict mathematical calculation in Python:

$$S = 0.25H + 0.20E + 0.25C + 0.15K + 0.15P$$

Where each criterion is scored on a scale of $0.0$ to $10.0$:
- **$H$ = Hook Strength (25%):** Visual or verbal punch in the first 3 seconds.
- **$E$ = Emotional Impact (20%):** Intensity of betrayal, heartbreak, anger, or love.
- **$C$ = Cliffhanger Strength (25%):** Suspense or unanswered question at the end.
- **$K$ = Story Coherence (15%):** Clarity of the promo narrative when viewed standalone.
- **$P$ = Promo Suitability (15%):** Pacing, dialogue punchiness, and visual appeal for short vertical video.

*Candidates are sorted in strictly descending order of $S$.*

---

## 💻 Installation & Setup (Windows)

### 1. Prerequisites
- **Python 3.12** installed on your system.
- Ensure **"Add Python to PATH"** was checked during Python installation.

### 2. Open PowerShell or Command Prompt
Navigate to the project root directory:
```powershell
cd d:\PromoAI
```

### 3. Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell)
.venv\Scripts\Activate.ps1

# (If running in Command Prompt instead)
# .venv\Scripts\activate.bat
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Configure API Key
Copy `.env.example` to create your local `.env` file:
```powershell
copy .env.example .env
```
Open `.env` in any text editor and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.1-flash-lite
APP_MODE=production
```
*(If you do not have an API key right now, PromoAI will automatically run in **Demo / Offline Mode** with synthetic data and deterministic validation.)*

---

## 🚀 Running the Application

Launch the Streamlit web dashboard:
```powershell
streamlit run app.py
```
Your browser will automatically open to `http://localhost:8501`.

---

## 🎥 Demonstration Workflow (Interview Ready)

When presenting this prototype to an evaluator:

1. **Section 1: 🏠 Home Dashboard**
   - Click **"⚡ Quick-Load First 5 Episodes"** in the sidebar (or drag-and-drop a ZIP of scripts).
   - Point out the file manifest, valid episode count, and encoding confirmation.
   - Explain that path traversal attacks (`../`) and non-text files are automatically blocked.

2. **Section 2: 📄 Screenplay Overview**
   - Select `Episode 1`.
   - Show how the parser extracted the logline, character list (`MATRIARCH`, `LADY JULIANA`, `GERALD`), and scenes.
   - Expand `Scene 01` to demonstrate exact dialogue lines and timestamps (`00:11.30` → `00:13.10`).

3. **Section 3: 🎯 Promo Generation**
   - Click **"✨ Generate Promo Candidates"**.
   - Show how the AI analyzes dramatic turning points and assembles continuous or multi-episode promos.

4. **Section 4: 📊 Promo Results**
   - Review candidate cards ranked by final score.
   - Expand the **"🔢 View Scoring Breakdown"** table to show the explainable weighted formula ($0.25H + 0.20E + \dots$).
   - Point out the **"📜 Selected Screenplay Source Moments"** with verbatim quotes and timestamp verification.

5. **Section 5: ✅ Quality Review**
   - Select a candidate. Demonstrate human editorial control: modify a hook, add editor notes, and click **"👍 Approve Promo"** or **"👎 Reject Promo"**.
   - Show the validation box verifying that quoted dialogue actually exists in the screenplay.

6. **Section 6: 📥 Export Results**
   - Click **"📄 Download JSON Output"** and **"📊 Download CSV Summary"**.
   - Show the JSON preview conforming to the assignment specification.

---

## 🧪 Automated Testing Suite

Automated tests are built with `pytest` and mock all external AI services, meaning **no API key and no paid network calls are required** to test.

Run the test suite:
```powershell
pytest tests/ -v
```

### Actual Execution Results:
```
tests/test_ai_provider.py::test_missing_api_key_returns_demo_mode PASSED
tests/test_ai_provider.py::test_missing_api_key_episode_analysis_demo PASSED
tests/test_ai_provider.py::test_health_check_no_key PASSED
tests/test_ai_provider.py::test_api_failure_handled_gracefully PASSED
tests/test_ai_provider.py::test_malformed_json_response_handled PASSED
tests/test_file_processor.py::test_valid_txt_file_accepted PASSED
tests/test_file_processor.py::test_invalid_extension_rejected PASSED
tests/test_file_processor.py::test_empty_file_rejected PASSED
tests/test_file_processor.py::test_missing_script_markers_rejected PASSED
tests/test_file_processor.py::test_zip_extraction_valid PASSED
tests/test_file_processor.py::test_zip_path_traversal_blocked PASSED
tests/test_file_processor.py::test_zip_executable_skipped PASSED
tests/test_file_processor.py::test_corrupted_zip_handled PASSED
tests/test_file_processor.py::test_multiple_txt_files PASSED
tests/test_file_processor.py::test_episode_label_extracted_from_header PASSED
tests/test_output_manager.py::test_json_export_structure PASSED
tests/test_output_manager.py::test_csv_export_headers_and_rows PASSED
tests/test_output_manager.py::test_markdown_report_generation PASSED
tests/test_promo_detector.py::test_promo_candidate_schema_valid PASSED
tests/test_promo_detector.py::test_promo_candidate_missing_hook_raises PASSED
tests/test_promo_detector.py::test_build_candidates_from_valid_ai_response PASSED
tests/test_promo_detector.py::test_build_candidates_handles_missing_fields PASSED
tests/test_promo_detector.py::test_build_candidates_empty_list PASSED
tests/test_promo_detector.py::test_generate_promo_id PASSED
tests/test_ranking_engine.py::test_score_formula_all_tens PASSED
tests/test_ranking_engine.py::test_score_formula_all_zeros PASSED
tests/test_ranking_engine.py::test_score_formula_weighted_calculation PASSED
tests/test_ranking_engine.py::test_ranking_sorts_descending PASSED
tests/test_ranking_engine.py::test_ranking_recalculates_ignoring_ai_score PASSED
tests/test_screenplay_parser.py::test_parse_timestamp_valid PASSED
tests/test_screenplay_parser.py::test_parse_timestamp_edge_cases PASSED
tests/test_screenplay_parser.py::test_extract_episode_header PASSED
tests/test_screenplay_parser.py::test_parse_full_episode PASSED
tests/test_screenplay_parser.py::test_characters_extracted PASSED
tests/test_screenplay_parser.py::test_dialogue_line_fields PASSED
tests/test_validator.py::test_source_text_found_in_episode PASSED
tests/test_validator.py::test_source_text_not_found_flagged PASSED
tests/test_validator.py::test_duration_within_range PASSED
tests/test_validator.py::test_duration_too_short_flagged PASSED
tests/test_validator.py::test_duration_too_long_flagged PASSED
tests/test_validator.py::test_duration_none_flagged PASSED
tests/test_validator.py::test_missing_hook_flagged PASSED
tests/test_validator.py::test_missing_cliffhanger_flagged PASSED
tests/test_validator.py::test_duplicate_candidates_detected PASSED

============================= 44 passed in 0.28s ==============================
```

---

## 🔒 Security & Verification Guidelines

1. **No Hardcoded Keys:** Secrets are strictly loaded via `os.getenv` and `.env`. The `.gitignore` file excludes `.env`, `venv/`, and Python cache artifacts.
2. **Confidential Screenplays:** Raw Kuku FM screenplays and generated commercial scripts are ignored by Git to prevent proprietary data leaks.
3. **No Hallucinated Accuracy:** The validator strictly checks whether extracted dialogue exists verbatim in the uploaded episode files.
4. **Timestamp Integrity:** If timestamps are missing in source scripts, PromoAI marks them as `unavailable` or `estimated` — never as verified timecodes.

---

## 🔭 Limitations & Future Improvements

- **Video Stream Synchronization:** The prototype operates directly on text screenplays. A logical future extension is integrating `ffmpeg` to directly cut and assemble corresponding MP4 video clips using the extracted timestamps.
- **Audio Energy Analysis:** Combining script dialogue with audio loudness / pitch analysis from audio tracks to further refine emotional intensity scores.
- **Automated A/B Promo Generation:** Generating multiple variations of the opening 3-second hook for the same core dramatic scene to facilitate marketing split tests.

---

**Developed for Kuku AI Generalist Campus Placement Assignment • PromoAI v1.0**
