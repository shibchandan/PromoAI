================================================================================
PROMOAI — AI-POWERED MICRODRAMA PROMO FINDER
Kuku AI Generalist Assignment (Problem 1: Find the Promos)
================================================================================

Candidate / Author: Shib Chandan Mistry
Project Repository: https://github.com/shibchandan/PromoAI
Live Deployed Demo: https://promoai11.streamlit.app/
Python Environment: Python 3.12 | Streamlit 1.67 | Google Gemini API
Test Status:       44/44 Unit Tests Passing (100% Pass Rate)

================================================================================
1. EXECUTIVE SUMMARY & LIVE DEPLOYMENT
================================================================================
PromoAI is an intelligent, neuro-symbolic promotional moment discovery and
editorial studio designed specifically for serialized vertical microdramas.
It automatically analyzes full-length screenplay episodes (TXT / ZIP), detects
high-stakes dramatic Turning Points (20–60s duration window), isolates opening
3-second attention hooks and unresolved cliffhanger cutoffs, and ranks them
using a mathematically explainable 5-factor scoring model:

    S = 0.25*Hook + 0.20*Emotion + 0.25*Cliffhanger + 0.15*Coherence + 0.15*Suitability

All moments are verified against exact screenplay source text and timestamps
(MM:SS.cc), preventing hallucinations and narrative drift.

Live Interactive Studio:
https://promoai11.streamlit.app/

GitHub Source Code:
https://github.com/shibchandan/PromoAI

================================================================================
2. SUBMISSION PACKAGE STRUCTURE
================================================================================
PromoAI_Submission/
│
├── 01_Solution_Document/
│   └── PromoAI_Solution.pdf       <- Complete architectural and mathematical solution
│
├── 02_Raw_Outputs/
│   ├── promo_results.json         <- Validated JSON output matching assignment spec
│   ├── promo_results.csv          <- Tabular spreadsheet of ranked promo cuts
│   └── analysis_report.pdf        <- Executive editorial analysis pitch report
│
├── 03_Demo/
│   ├── PromoAI_Walkthrough.mp4    <- Video walkthrough of the live studio application
│   └── WALKTHROUGH_SCRIPT.md      <- 2-minute step-by-step presentation script
│
└── 04_Project_Links/
    └── README.txt                 <- This reference document

================================================================================
3. CORE CAPABILITIES & INNOVATIONS
================================================================================
1. Hollywood Screenplay Ingestion Engine:
   Robust regex and lexer parsing of scene headings (INT./EXT.), character slugs,
   parenthetical emotions, dialogue text, and precise timing (MM:SS.cc).

2. Dynamic 9:16 Video Cutting Monitor:
   In-app simulator rendering the exact mobile vertical viewing experience with:
   - TikTok / Instagram Reels social safe-zone guides
   - Pacing timeline bars (0–3s hook -> confrontation body -> cliffhanger cutoff)
   - Real-time burned-in subtitles and stereo audio mastering specs

3. Dual Strategy Discovery:
   - Single-episode continuous high-tension confrontations
   - Multi-episode narrative arcs connecting setup in Ep A with payoff in Ep B

4. Human-In-The-Loop Editorial Quality Review:
   Interactive review station allowing marketing editors to approve/reject cuts,
   refine hook wording, and add editor directions for video production teams.

5. Enterprise Anti-Hallucination Guardrails:
   Verbatim substring verification ensuring every dialogue line and timestamp
   corresponds to actual screenplay lines in the source dataset.

================================================================================
4. LOCAL SETUP & TESTING INSTRUCTIONS
================================================================================
To run PromoAI locally on your workstation:

Step 1: Clone Repository
   git clone https://github.com/shibchandan/PromoAI.git
   cd PromoAI

Step 2: Create & Activate Virtual Environment
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS / Linux:
   source .venv/bin/activate

Step 3: Install Dependencies
   pip install -r requirements.txt

Step 4: Configure API Key (Optional)
   cp .env.example .env
   # Add your Google Gemini API key to .env:
   # GEMINI_API_KEY="AIzaSy..."
   # (App also runs in deterministic heuristic mode without an API key)

Step 5: Run Automated Test Suite
   pytest tests/ -v
   # Result: 44 passed in ~0.37s

Step 6: Launch Streamlit Studio
   streamlit run app.py
   # Opens in browser at http://localhost:8501

================================================================================
5. CONTACT & VERIFICATION
================================================================================
Author: Shib Chandan Mistry
Assignment: Kuku AI Generalist Campus Placement Assignment
Problem: Problem 1 — Find the Promos
Date: November 2026