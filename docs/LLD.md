# **Low-Level Design (LLD)**

## **PromoAI – AI-Powered Microdrama Promo Finder**

**Version:** 1.0  
**Status:** Pre-Development Draft  
**Language:** Python 3.12  
**Frontend:** Streamlit  
**AI Provider:** Gemini API  
**Architecture:** Modular Monolithic Architecture

---

## **1\. Introduction**

### **1.1 Purpose**

This document describes the internal implementation design of PromoAI. It defines the individual modules, functions, data structures, processing sequence, and interactions required to build the application.

### **1.2 Scope**

PromoAI will analyze microdrama screenplay files, identify potential promotional segments, evaluate their quality, and generate ranked recommendations.

The initial implementation will focus on text-based screenplay analysis rather than direct video editing.

---

## **2\. Project Directory Structure**

The proposed project structure is:

```
PromoAI/
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── input/
│   └── screenplay/
│
├── outputs/
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── file_processor.py
│   ├── screenplay_parser.py
│   ├── scene_analyzer.py
│   ├── promo_detector.py
│   ├── ranking_engine.py
│   ├── validator.py
│   ├── output_manager.py
│   │
│   └── ai/
│       ├── __init__.py
│       ├── base_provider.py
│       └── gemini_provider.py
│
├── docs/
│   ├── PRD.md
│   ├── TRD.md
│   ├── SRS.md
│   ├── HLD.md
│   └── LLD.md
│
└── tests/
    ├── test_file_processor.py
    ├── test_screenplay_parser.py
    ├── test_promo_detector.py
    ├── test_validator.py
    └── test_ranking_engine.py
```

The directory structure may be adjusted after inspecting the actual screenplay input format.

---

## **3\. Module-Level Design**

### **3.1 app.py – Main Application**

**Purpose:** Entry point of the Streamlit application.

Responsibilities:

* Configure the Streamlit page.  
* Display application title and description.  
* Accept screenplay file uploads.  
* Trigger analysis.  
* Display progress and processing errors.  
* Display ranked promo recommendations.  
* Allow JSON and CSV downloads.

Proposed functions:

**`main()`**

* Initialize the interface.  
* Display the upload section.  
* Call the screenplay processing workflow.  
* Display generated results.

**`display_results(promos)`**

* Display each promo candidate.  
* Show its score, hook, cliffhanger, source episode, and validation status.

**`display_promo_details(promo)`**

* Display the complete details of a selected candidate.

---

### **3.2 config.py – Configuration Management**

**Purpose:** Manage application configuration and environment variables.

Responsibilities:

* Load API credentials.  
* Define supported file formats.  
* Define target promo duration.  
* Define scoring weights.  
* Define output directories.

Proposed constants:

```
SUPPORTED_EXTENSIONS = [".txt"]

MIN_PROMO_DURATION = 20
MAX_PROMO_DURATION = 60

SCORING_WEIGHTS = {
    "hook": 0.25,
    "emotional_impact": 0.20,
    "cliffhanger": 0.25,
    "coherence": 0.15,
    "promo_suitability": 0.15
}
```

The weights must total 1.0.

---

### **3.3 file\_processor.py – File Processing**

**Purpose:** Read and validate uploaded screenplay files.

Proposed functions:

**`validate_file(file)`**

Checks:

* Supported extension.  
* Non-empty content.  
* Valid text encoding.

Returns a validation result and error message, if applicable.

**`read_screenplay(file)`**

* Reads the uploaded file.  
* Decodes its contents.  
* Returns screenplay text.

**`process_uploaded_files(files)`**

* Processes multiple uploaded files.  
* Associates each text with its original filename.  
* Collects valid files and processing errors.

Expected output:

```
{
    "filename": "episode_01.txt",
    "episode_id": "EP_01",
    "content": "Screenplay text...",
    "status": "success"
}
```

---

### **3.4 screenplay\_parser.py – Screenplay Parsing**

**Purpose:** Organize extracted screenplay text into episodes and scenes.

Proposed functions:

**`extract_episode_id(filename)`**

Attempts to identify the episode number from the filename. If unavailable, uses a stable fallback identifier.

**`normalize_text(text)`**

* Removes unnecessary whitespace.  
* Normalizes line endings.  
* Preserves meaningful screenplay content.

**`split_into_scenes(text)`**

* Identifies scene boundaries where screenplay headings are available.  
* Splits text into manageable sections.  
* Preserves source order.

**`parse_screenplay(filename, text)`**

Returns a structured episode object containing episode metadata and scene information.

Important: Scene splitting must be based on the actual screenplay format. The implementation should not assume that all scripts use standard screenplay headings.

---

### **3.5 scene\_analyzer.py – Scene Analysis**

**Purpose:** Analyze screenplay scenes to identify important story elements.

Proposed functions:

**`analyze_scene(scene, ai_provider)`**

Sends a scene or suitable chunk to the AI provider for structured analysis.

Expected analysis:

* Main event.  
* Characters involved.  
* Conflict.  
* Emotional intensity.  
* Suspense.  
* Potential hook.  
* Potential cliffhanger.

**`analyze_episode(episode, ai_provider)`**

Analyzes all relevant scenes of an episode and collects their analysis results.

The analyzer should preserve evidence excerpts and source references.

---

### **3.6 ai/base\_provider.py – AI Provider Interface**

**Purpose:** Define a common interface for AI providers.

Proposed interface:

```
from abc import ABC, abstractmethod

class BaseAIProvider(ABC):

    @abstractmethod
    def analyze(self, prompt: str) -> dict:
        pass
```

This allows the application to switch AI providers without changing the main analysis workflow.

---

### **3.7 ai/gemini\_provider.py – Gemini Integration**

**Purpose:** Communicate with the Gemini API.

Proposed functions:

**`__init__()`**

* Load the API key.  
* Initialize the Gemini client.

**`analyze(prompt)`**

* Send the prompt to the model.  
* Receive the response.  
* Parse the structured output.  
* Handle API and response errors.

**`generate_scene_analysis(scene)`**

* Construct the scene-analysis prompt.  
* Request structured JSON.  
* Return parsed results.

**`generate_promo_candidates(analysis)`**

* Construct a candidate-generation prompt.  
* Request promo recommendations.  
* Return structured candidate data.

The implementation should use the current supported Gemini SDK and response-format capabilities.

---

### **3.8 promo\_detector.py – Promo Candidate Generation**

**Purpose:** Generate promotional segments from analyzed screenplay content.

Proposed functions:

**`identify_candidate_scenes(scene_analysis)`**

Selects scenes with strong conflict, emotion, curiosity, or suspense.

**`generate_candidates(episode_analysis, ai_provider)`**

Generates candidate promo segments using screenplay evidence.

**`check_continuity(candidate)`**

Checks whether selected content represents a coherent continuous stretch or clearly identified multiple source segments.

**`extract_hook(candidate)`**

Identifies the opening hook.

**`extract_cliffhanger(candidate)`**

Identifies the unresolved ending.

**`detect_promos(episodes, ai_provider)`**

Coordinates candidate generation across all uploaded episodes.

The system should prioritize continuous 20–60 second promo opportunities. Candidates combining multiple moments must retain separate source references for every segment.

---

### **3.9 validator.py – Quality Validation**

**Purpose:** Validate AI-generated recommendations before ranking and display.

Proposed functions:

**`validate_required_fields(promo)`**

Checks that required fields are present.

**`validate_episode_reference(promo, episodes)`**

Checks that source episode identifiers exist.

**`validate_timestamps(promo)`**

Checks timestamp formatting and consistency.

**`validate_duration(promo)`**

Checks whether duration is within the target 20–60 second range.

If actual timestamps are unavailable, the validator should require an explicit unavailable or estimated status rather than treating missing timing as verified.

**`validate_evidence(promo, source_text)`**

Checks whether quoted or referenced content can be located in the original screenplay.

**`validate_promo(promo, episodes)`**

Runs all validation checks and returns:

* Validation status.  
* Error messages.  
* Warnings.

---

### **3.10 ranking\_engine.py – Scoring and Ranking**

**Purpose:** Calculate quality scores and rank candidate promos.

Initial weights:

| Criterion | Weight |
| ----- | ----- |
| Hook | 25% |
| Emotional impact | 20% |
| Cliffhanger | 25% |
| Coherence | 15% |
| Promo suitability | 15% |

Proposed functions:

**`calculate_score(scores)`**

Calculates the weighted score.

Formula:

\[  
S \= 0.25H \+ 0.20E \+ 0.25C \+ 0.15K \+ 0.15P  
\]

Where:

* (H) \= Hook score  
* (E) \= Emotional impact score  
* (C) \= Cliffhanger score  
* (K) \= Coherence score  
* (P) \= Promo suitability score

Each criterion is rated from 0 to 10\.

**`rank_promos(promos)`**

* Calculates scores.  
* Sorts candidates in descending order.  
* Assigns ranking positions.

Only candidates passing mandatory validation should be presented as validated recommendations. Candidates with warnings may remain visible with clear labels.

---

### **3.11 output\_manager.py – Output Management**

**Purpose:** Save and export generated recommendations.

Proposed functions:

**`save_json(promos, output_path)`**

Saves candidate recommendations in JSON format.

**`export_csv(promos)`**

Converts candidate recommendations into CSV format.

**`generate_output_filename()`**

Creates a unique output filename.

The export must retain source references, timestamp status, scores, explanations, and validation warnings.

---

## **4\. Data Models**

The application should use Pydantic models or equivalent structured validation.

### **4.1 Episode Model**

```
{
    "episode_id": "EP_01",
    "filename": "episode_01.txt",
    "content": "Full screenplay content",
    "scenes": [],
    "processing_status": "success"
}
```

### **4.2 Scene Model**

```
{
    "scene_id": "EP_01_SC_01",
    "episode_id": "EP_01",
    "scene_text": "Scene content",
    "source_start_line": 1,
    "source_end_line": 30
}
```

Line references are optional when reliable line boundaries can be preserved.

### **4.3 Promo Model**

```
{
    "promo_id": "PROMO_001",
    "source_segments": [
        {
            "episode_id": "EP_01",
            "start_time": None,
            "end_time": None,
            "source_reference": "EP_01_SC_01"
        }
    ],
    "hook": "Opening hook explanation",
    "cliffhanger": "Unresolved ending explanation",
    "selected_content": "Relevant screenplay excerpt",
    "timestamp_status": "unavailable",
    "duration_seconds": None,
    "scores": {
        "hook": 8,
        "emotional_impact": 9,
        "cliffhanger": 9,
        "coherence": 8,
        "promo_suitability": 8
    },
    "overall_score": 8.5,
    "ranking": 1,
    "validation_status": "passed",
    "warnings": []
}
```

The sample scores and text are illustrative only.

---

## **5\. Detailed Processing Algorithm**

### **Step 1: Upload**

Receive multiple screenplay files through Streamlit.

### **Step 2: Validate**

Check file type, encoding, and content.

### **Step 3: Extract**

Read screenplay text and associate it with its source filename.

### **Step 4: Parse**

Identify episodes and divide the text into scenes or manageable chunks.

### **Step 5: Analyze**

Use the AI provider to identify:

* Conflicts.  
* Emotional moments.  
* Character interactions.  
* Hooks.  
* Cliffhangers.

### **Step 6: Generate Candidates**

Generate possible promo segments using the analyzed screenplay content.

### **Step 7: Validate**

Check source references, evidence, timestamps, duration, and required fields.

### **Step 8: Score**

Calculate weighted quality scores.

### **Step 9: Rank**

Sort valid candidates from highest to lowest score.

### **Step 10: Display and Export**

Display results in Streamlit and allow JSON or CSV export.

---

## **6\. Prompt Design**

### **6.1 Scene Analysis Prompt**

The model should be instructed to:

* Analyze only the supplied screenplay.  
* Identify major story events.  
* Detect emotional conflict and suspense.  
* Identify possible hooks and cliffhangers.  
* Include supporting evidence.  
* Avoid inventing dialogue, characters, or events.  
* Return structured JSON.

### **6.2 Promo Generation Prompt**

The model should be instructed to:

* Generate candidates lasting approximately 20–60 seconds.  
* Prefer continuous screenplay moments.  
* Start with a strong hook.  
* End with an unresolved cliffhanger.  
* Make each promo understandable independently.  
* Identify all source episodes and segments.  
* Explain why the candidate is promotional.  
* Mark missing timestamps as unavailable.  
* Return structured JSON.

### **6.3 Evaluation Prompt**

The model should evaluate:

* Hook strength.  
* Emotional impact.  
* Cliffhanger strength.  
* Story coherence.  
* Promo suitability.

Each criterion should receive a score from 0 to 10 with a brief explanation.

---

## **7\. Exception Handling**

| Exception | Handling |
| ----- | ----- |
| Invalid file | Reject and show error |
| Empty screenplay | Skip and report |
| Unknown episode ID | Assign fallback ID |
| Scene parsing failure | Use safe chunking fallback |
| AI API failure | Report failure and allow retry |
| Invalid JSON | Attempt controlled recovery or retry |
| Missing evidence | Flag candidate |
| Invalid timestamps | Mark candidate as requiring review |
| Export failure | Display an error |

An episode failure should not unnecessarily stop the processing of other valid episodes.

---

## **8\. Testing Design**

The following unit tests should be implemented:

| Test File | Test Cases |
| ----- | ----- |
| `test_file_processor.py` | Valid, empty, and unsupported files |
| `test_screenplay_parser.py` | Episode extraction and scene splitting |
| `test_promo_detector.py` | Candidate structure and continuity |
| `test_validator.py` | Missing fields, invalid references, and timestamps |
| `test_ranking_engine.py` | Weighted score and sorting |

Integration testing should cover the complete workflow from file upload to export.

AI-dependent tests should use controlled sample responses where possible, so unit tests do not require a live API call.

---

## **9\. Performance Considerations**

* Process scripts in manageable chunks.  
* Avoid sending an entire large screenplay in one API request.  
* Reuse parsed data when possible.  
* Handle API rate limits and transient errors.  
* Provide progress indicators.  
* Avoid repeatedly analyzing unchanged screenplay sections.

---

## **10\. Implementation Priorities**

### **Phase 1: Basic Application**

* Set up Python environment.  
* Create project structure.  
* Build Streamlit upload interface.  
* Implement file validation and text extraction.

### **Phase 2: Screenplay Analysis**

* Inspect actual screenplay format.  
* Implement episode and scene parsing.  
* Integrate Gemini API.  
* Generate structured scene analysis.

### **Phase 3: Promo Generation**

* Implement candidate detection.  
* Generate hooks and cliffhangers.  
* Preserve source references.

### **Phase 4: Validation and Ranking**

* Implement validation rules.  
* Implement scoring and ranking.  
* Flag unreliable timestamp information.

### **Phase 5: Final Interface and Testing**

* Build the results dashboard.  
* Add JSON and CSV export.  
* Run tests on the full input pack.  
* Save raw outputs.  
* Prepare the final solution document.

---

## **11\. Conclusion**

This LLD defines the proposed internal structure of PromoAI, including individual Python modules, function responsibilities, data models, AI prompt requirements, validation logic, and implementation phases.

The modular design separates AI-based story understanding from deterministic application logic, allowing the prototype to generate explainable and traceable promo recommendations.

**Document Status:** Version 1.0 – Pre-Development Draft

