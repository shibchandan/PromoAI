# **High-Level Design (HLD)**

## **PromoAI – AI-Powered Microdrama Promo Finder**

**Version:** 1.0  
**Status:** Pre-Development Draft  
**Architecture:** Modular Monolithic Architecture  
**Frontend:** Streamlit  
**Backend:** Python 3.12  
**AI Provider:** Gemini API  
**Storage:** JSON / SQLite

---

## **1\. Introduction**

### **1.1 Purpose**

This document describes the high-level architecture and major components of PromoAI. It explains how screenplay files move through the system, how AI analysis is performed, how promo candidates are evaluated, and how results are presented to users.

### **1.2 System Overview**

PromoAI is an AI-powered application that analyzes microdrama screenplay episodes and identifies potential promotional segments lasting approximately 20–60 seconds.

The system combines:

* Rule-based screenplay processing.  
* LLM-powered story and scene analysis.  
* Candidate generation.  
* Quality scoring and ranking.  
* Validation and human review.

The architecture is designed to be modular so individual components can be improved without rewriting the entire application.

---

## **2\. System Architecture**

### **2.1 Architectural Style**

PromoAI will initially use a **Modular Monolithic Architecture**.

All application components will run within one Python application but will be separated into independent modules.

This approach is appropriate for a small prototype because it:

* Reduces infrastructure complexity.  
* Makes development and debugging easier.  
* Supports clear separation of responsibilities.  
* Allows future migration to separate services if required.

### **2.2 High-Level Architecture Diagram**

```
flowchart TD
    A[User] --> B[Streamlit User Interface]
    B --> C[File Upload Manager]
    C --> D[Screenplay Processor]
    D --> E[Episode and Scene Parser]
    E --> F[Scene Analyzer]
    F --> G[AI Provider Layer]
    G --> H[Gemini API]
    H --> I[Candidate Promo Generator]
    I --> J[Quality Validator]
    J --> K[Scoring and Ranking Engine]
    K --> L[Results Dashboard]
    L --> M[JSON / CSV Export]
    L --> N[User Feedback]
    D --> O[Local Storage]
    J --> O
    K --> O
```

### **2.3 Architecture Workflow**

1. The user uploads screenplay files through the Streamlit interface.  
2. The file upload manager checks file types and basic validity.  
3. The screenplay processor extracts the text from each file.  
4. The episode and scene parser organizes the content into manageable sections.  
5. The scene analyzer identifies story elements such as conflict, emotion, hooks, and suspense.  
6. The AI provider layer sends structured screenplay content to the selected LLM.  
7. The candidate promo generator creates potential promo segments.  
8. The quality validator checks references, timestamps, required fields, and supporting evidence.  
9. The scoring and ranking engine evaluates and ranks the valid candidates.  
10. The results dashboard displays recommendations.  
11. Users can review, flag, and export the results.

---

## **3\. Major System Components**

### **3.1 User Interface Layer**

**Technology:** Streamlit

Responsibilities:

* Provide screenplay upload controls.  
* Display uploaded episode names.  
* Start screenplay analysis.  
* Show processing progress.  
* Display ranked promo candidates.  
* Show quality scores and validation warnings.  
* Provide export and feedback controls.

### **3.2 File Upload Manager**

Responsibilities:

* Accept multiple screenplay files.  
* Validate file extensions and file sizes.  
* Reject empty or unsupported files.  
* Pass valid files to the screenplay processor.

### **3.3 Screenplay Processor**

Responsibilities:

* Read screenplay text.  
* Normalize line breaks and whitespace without changing story meaning.  
* Preserve original text for evidence verification.  
* Identify episode information.  
* Prepare content for parsing.

### **3.4 Episode and Scene Parser**

Responsibilities:

* Divide screenplay content into episodes.  
* Detect scene headings and dialogue blocks when the format supports them.  
* Split large scripts into manageable sections.  
* Preserve the relationship between each section and its original file.  
* Maintain source references for candidate generation.

### **3.5 Scene Analyzer**

Responsibilities:

* Analyze dialogue and action descriptions.  
* Identify important story events.  
* Detect emotional moments and conflicts.  
* Identify possible hooks and cliffhangers.  
* Produce structured scene-analysis information.

### **3.6 AI Provider Layer**

**Initial Provider:** Gemini API

Responsibilities:

* Provide a common interface for AI models.  
* Construct prompts for screenplay analysis.  
* Send screenplay sections for analysis.  
* Receive and parse structured responses.  
* Handle API errors and malformed responses.

The provider layer will be designed so another LLM provider can be integrated later without changing the main application workflow.

### **3.7 Candidate Promo Generator**

Responsibilities:

* Combine relevant story moments into candidate promo segments.  
* Prefer coherent, continuous story stretches.  
* Identify opening and ending moments.  
* Generate candidate explanations.  
* Preserve episode and source references.

The system should prioritize a continuous segment. If it combines moments from different episodes, it must clearly identify every source segment.

### **3.8 Quality Validator**

Responsibilities:

* Validate required output fields.  
* Verify episode references against uploaded files.  
* Check timestamp formats and duration.  
* Identify missing or unreliable timing information.  
* Check whether supporting excerpts exist in the source screenplay.  
* Flag unsupported or contradictory AI-generated claims.

### **3.9 Scoring and Ranking Engine**

The ranking engine will calculate a weighted quality score.

Initial scoring model:

| Criterion | Weight |
| ----- | ----- |
| Hook strength | 25% |
| Emotional impact | 20% |
| Cliffhanger strength | 25% |
| Story coherence | 15% |
| Promo suitability | 15% |
| **Total** | **100%** |

Scores will be generated using AI evaluation and rule-based checks. The final score is a heuristic ranking aid, not a prediction of actual audience engagement.

### **3.10 Results and Export Manager**

Responsibilities:

* Display candidate promo details.  
* Sort candidates by score.  
* Display validation warnings.  
* Export results as JSON or CSV.  
* Save generated outputs for later inspection.

---

## **4\. Data Flow Design**

### **4.1 Input Data Flow**

The system receives one or more `.txt` screenplay files.

Each file is associated with:

* Original filename.  
* Episode identifier, if available.  
* Extracted screenplay text.  
* Parsing status.

### **4.2 Processing Data Flow**

The extracted text is divided into manageable sections.

Each section should retain:

* Episode identifier.  
* Scene identifier, if available.  
* Original text.  
* Source location or line references where possible.

The AI analyzes these sections and produces structured candidate information.

### **4.3 Output Data Flow**

Each candidate promo is passed through validation and scoring.

The final result contains:

* Promo identifier.  
* Source episode.  
* Selected screenplay excerpt.  
* Start and end timestamps, if supported.  
* Timestamp confidence or estimation status.  
* Opening hook.  
* Cliffhanger.  
* Emotional impact.  
* Quality score.  
* Ranking.  
* Explanation.  
* Validation status and warnings.

---

## **5\. Logical Data Design**

The initial prototype can use JSON files for storing results. SQLite can be introduced when persistent querying and feedback history are needed.

### **5.1 Main Logical Entities**

**Episode**

* episode\_id  
* filename  
* screenplay\_text  
* processing\_status

**Scene**

* scene\_id  
* episode\_id  
* scene\_text  
* source\_reference

**PromoCandidate**

* promo\_id  
* episode\_id  
* selected\_content  
* start\_time  
* end\_time  
* duration  
* hook  
* cliffhanger  
* emotional\_impact  
* score  
* ranking  
* validation\_status

**UserFeedback**

* feedback\_id  
* promo\_id  
* feedback\_type  
* feedback\_comment

These are logical entities. Their final physical representation may differ depending on the implementation.

---

## **6\. AI Integration Design**

### **6.1 AI Responsibilities**

The LLM will be used for tasks that require story understanding, including:

* Detecting emotional moments.  
* Understanding character conflicts.  
* Identifying hooks.  
* Identifying unresolved cliffhangers.  
* Explaining promo suitability.  
* Evaluating candidate quality.

### **6.2 Rule-Based Responsibilities**

The application code will handle:

* File validation.  
* Text extraction.  
* Episode identification.  
* Required-field validation.  
* Timestamp format checks.  
* Duration calculations when timestamps are available.  
* Source-reference checks.  
* Score aggregation.  
* Candidate sorting.  
* Export generation.

### **6.3 AI Response Format**

The AI should return structured JSON rather than unstructured paragraphs.

Example:

```
{
  "promo_id": "PROMO_001",
  "episode_id": "EP_01",
  "hook": "A surprising confrontation creates immediate curiosity.",
  "selected_content": "Relevant screenplay excerpt",
  "start_time": null,
  "end_time": null,
  "duration_seconds": null,
  "timestamp_status": "unavailable",
  "cliffhanger": "The confrontation ends with an unanswered question.",
  "emotional_impact": "Creates tension and curiosity.",
  "score": {
    "hook": 8,
    "emotional_impact": 9,
    "cliffhanger": 9,
    "coherence": 8,
    "promo_suitability": 8
  },
  "explanation": "The segment introduces conflict and ends on an unresolved moment."
}
```

The example is illustrative, not an actual result from the supplied screenplay pack.

### **6.4 AI Reliability**

The system shall:

* Use structured prompts.  
* Request evidence from screenplay text.  
* Validate model responses.  
* Retry recoverable formatting failures where appropriate.  
* Flag unsupported claims.  
* Avoid presenting estimated timestamps as verified timestamps.

---

## **7\. Error Handling Architecture**

| Error | Handling |
| ----- | ----- |
| Unsupported file | Display validation error |
| Empty file | Reject file |
| Parsing failure | Record episode-level error |
| AI API unavailable | Display error and allow retry |
| Invalid AI response | Attempt structured parsing and validation |
| Missing timestamp | Mark as unavailable or estimated |
| Invalid episode reference | Reject or flag candidate |
| Export failure | Display error without losing current results |

The application should continue processing other valid episodes when one episode fails, wherever practical.

---

## **8\. Security and Privacy Design**

* API keys shall be stored in environment variables or Streamlit secrets.  
* Secrets shall be excluded from version control.  
* Uploaded screenplay files shall not be placed in a public directory.  
* Temporary data shall be handled carefully.  
* The confidential assignment input pack shall not be published in the public GitHub repository.  
* Logs should avoid unnecessarily recording full screenplay content or API credentials.

---

## **9\. Deployment Architecture**

### **9.1 Development Environment**

The application will initially run locally.

Required components:

* Python 3.12.  
* Virtual environment.  
* Required Python packages.  
* Gemini API key.  
* Git repository.

### **9.2 Deployment Option**

The prototype may be deployed using Streamlit Community Cloud or demonstrated locally.

If deployed:

* Store API credentials securely using deployment secrets.  
* Do not include confidential screenplay files in the public repository.  
* Provide sample or synthetic input for public demonstrations.

---

## **10\. Scalability and Future Enhancements**

Potential improvements include:

* Support for PDF and DOCX screenplay files.  
* Video and subtitle analysis.  
* Automatic alignment between screenplay text and actual video timestamps.  
* Character relationship analysis.  
* Multi-language screenplay support.  
* Additional LLM providers.  
* Human feedback-based ranking improvements.  
* Integration with video editing workflows.

---

## **11\. Design Decisions**

| Decision | Reason |
| ----- | ----- |
| Python | Suitable for text processing and AI integration |
| Streamlit | Fast development of an interactive prototype |
| Gemini API | Provides LLM-based screenplay understanding |
| Modular monolith | Simple deployment and maintenance |
| JSON output | Easy to inspect and validate |
| Rule-based validation | Reduces dependence on AI-generated claims |
| Human review | Helps identify weak or misleading recommendations |

---

## **12\. Conclusion**

PromoAI uses a modular architecture combining screenplay processing, LLM-based story analysis, candidate generation, rule-based validation, and quality ranking.

The design prioritizes grounded recommendations, traceability to original screenplay content, and transparent handling of timestamp uncertainty.

The architecture is intentionally lightweight for the initial assignment prototype while allowing future expansion into video-based promo generation.

**Document Status:** Version 1.0 – Pre-Development Draft

