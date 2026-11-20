# **API Documentation**

## **PromoAI – AI-Powered Microdrama Promo Finder**

**Version:** 1.0  
**Status:** Pre-Development Draft  
**Backend:** Python 3.12  
**Frontend:** Streamlit  
**AI Provider:** Gemini API  
**Data Format:** JSON

---

## **1\. Introduction**

### **1.1 Purpose**

This document describes the interfaces through which different PromoAI modules communicate, along with the external AI service integration.

It defines:

* Input parameters.  
* Output structures.  
* Function responsibilities.  
* Error responses.  
* Data validation rules.  
* AI request and response formats.

### **1.2 API Architecture**

PromoAI initially uses internal Python function interfaces rather than a standalone REST API.

The main communication flow is:

```
flowchart TD
    A[Streamlit UI] --> B[File Processing Interface]
    B --> C[Screenplay Parsing Interface]
    C --> D[Scene Analysis Interface]
    D --> E[Gemini Provider Interface]
    E --> F[Promo Detection Interface]
    F --> G[Validation Interface]
    G --> H[Ranking Interface]
    H --> I[Output Interface]
    I --> J[Streamlit Results Dashboard]
```

---

## **2\. Internal API Interfaces**

### **2.1 File Processing API**

**Module:** `src/file_processor.py`

#### **Function: `validate_file(file)`**

Purpose: Validate an uploaded screenplay file.

Input:

| Parameter | Type | Description |
| ----- | ----- | ----- |
| file | UploadedFile | Uploaded screenplay file |

Expected output:

```
{
  "valid": true,
  "filename": "episode_01.txt",
  "message": "File is valid"
}
```

Possible errors:

* Unsupported file format.  
* Empty file.  
* Invalid encoding.  
* File too large.

#### **Function: `process_uploaded_files(files)`**

Purpose: Process multiple uploaded screenplay files.

Input:

* `files`: List of uploaded screenplay files.

Expected output:

```
{
  "processed_files": [
    {
      "episode_id": "EP_01",
      "filename": "episode_01.txt",
      "content": "Screenplay content...",
      "status": "success"
    }
  ],
  "errors": []
}
```

---

### **2.2 Screenplay Parsing API**

**Module:** `src/screenplay_parser.py`

#### **Function: `parse_screenplay(filename, text)`**

Purpose: Convert screenplay text into structured episode and scene data.

Input:

| Parameter | Type |
| ----- | ----- |
| filename | String |
| text | String |

Expected output:

```
{
  "episode_id": "EP_01",
  "filename": "episode_01.txt",
  "scenes": [
    {
      "scene_id": "EP_01_SC_01",
      "scene_text": "Screenplay scene content...",
      "start_line": 1,
      "end_line": 30
    }
  ]
}
```

If scene boundaries cannot be reliably identified, the parser should use fallback text chunking and preserve source references.

---

### **2.3 Scene Analysis API**

**Module:** `src/scene_analyzer.py`

#### **Function: `analyze_scene(scene, ai_provider)`**

Purpose: Analyze a screenplay scene using the configured AI provider.

Input:

| Parameter | Type | Description |
| ----- | ----- | ----- |
| scene | Dictionary | Structured scene information |
| ai\_provider | BaseAIProvider | Configured AI provider |

Expected output:

```
{
  "scene_id": "EP_01_SC_01",
  "main_event": "A confrontation between two characters",
  "conflict": "A disagreement about a hidden truth",
  "emotional_intensity": 8,
  "suspense": 9,
  "potential_hook": "A surprising opening moment",
  "potential_cliffhanger": "An unanswered question",
  "evidence": [
    "Relevant original screenplay excerpt"
  ]
}
```

---

## **3\. AI Provider API**

### **3.1 Base Provider Interface**

**Module:** `src/ai/base_provider.py`

Function:

```
analyze(prompt: str) -> dict
```

Purpose:

* Define a common interface for LLM providers.  
* Return structured analysis.  
* Allow future provider replacement.

### **3.2 Gemini Provider**

**Module:** `src/ai/gemini_provider.py`

#### **Function: `generate_scene_analysis(scene)`**

Purpose: Generate structured scene analysis.

Input:

```
{
  "scene_id": "EP_01_SC_01",
  "scene_text": "Screenplay scene content..."
}
```

Output:

* Main event.  
* Conflict.  
* Emotional intensity.  
* Suspense.  
* Hook and cliffhanger possibilities.  
* Supporting evidence.

#### **Function: `generate_promo_candidates(analysis)`**

Purpose: Generate potential promotional segments.

Input:

* Structured scene-analysis results.

Expected output:

```
{
  "candidates": [
    {
      "promo_id": "PROMO_001",
      "source_segments": [
        {
          "episode_id": "EP_01",
          "scene_id": "EP_01_SC_01",
          "start_time": null,
          "end_time": null
        }
      ],
      "hook": "Opening hook explanation",
      "cliffhanger": "Unresolved ending explanation",
      "selected_content": "Relevant screenplay excerpt",
      "timestamp_status": "unavailable"
    }
  ]
}
```

The example illustrates the response structure and is not a result from the actual screenplay pack.

---

## **4\. Promo Detection API**

**Module:** `src/promo_detector.py`

#### **Function: `identify_candidate_scenes(scene_analysis)`**

Purpose: Identify scenes that may contain promotional moments.

Input:

* List of scene-analysis objects.

Output:

* List of potential scenes with supporting evidence.

#### **Function: `generate_candidates(episode_analysis, ai_provider)`**

Purpose: Generate candidate promotional segments.

Input:

* Episode analysis.  
* Configured AI provider.

Output:

* List of promo candidate objects.

#### **Function: `check_continuity(candidate)`**

Purpose: Check whether a promo candidate represents a coherent story segment.

Output:

```
{
  "continuous": true,
  "source_segment_count": 1,
  "warning": null
}
```

A candidate assembled from multiple moments must retain separate source segment references.

---

## **5\. Validation API**

**Module:** `src/validator.py`

#### **Function: `validate_promo(promo, episodes)`**

Purpose: Validate the generated recommendation.

Checks:

* Required fields.  
* Episode references.  
* Source evidence.  
* Timestamp format.  
* Duration.  
* Output structure.

Expected output:

```
{
  "promo_id": "PROMO_001",
  "validation_status": "warning",
  "checks": {
    "required_fields": true,
    "episode_reference": true,
    "evidence": true,
    "timestamp_format": true,
    "duration": false
  },
  "warnings": [
    "Actual video timestamps are unavailable."
  ]
}
```

The timestamp format check does not prove that a timestamp matches the actual video.

---

## **6\. Ranking API**

**Module:** `src/ranking_engine.py`

#### **Function: `calculate_score(scores)`**

Purpose: Calculate the weighted promo quality score.

Input:

```
{
  "hook": 8,
  "emotional_impact": 9,
  "cliffhanger": 9,
  "coherence": 8,
  "promo_suitability": 8
}
```

Output:

```
{
  "overall_score": 8.45
}
```

Formula:

\[  
S \= 0.25H \+ 0.20E \+ 0.25C \+ 0.15K \+ 0.15P  
\]

#### **Function: `rank_promos(promos)`**

Purpose:

* Calculate candidate scores.  
* Sort candidates by score.  
* Assign ranking positions.

Output:

```
{
  "ranked_promos": [
    {
      "promo_id": "PROMO_001",
      "overall_score": 8.45,
      "ranking": 1
    }
  ]
}
```

Candidates that fail mandatory validation should not be presented as fully validated recommendations.

---

## **7\. Output Management API**

**Module:** `src/output_manager.py`

#### **Function: `save_json(promos, output_path)`**

Purpose: Save structured recommendations to JSON.

Input:

* List of promo objects.  
* Output file path.

Output:

* Saved JSON file.

#### **Function: `export_csv(promos)`**

Purpose: Convert promo recommendations into CSV format.

Expected columns:

* promo\_id  
* episode\_id  
* hook  
* cliffhanger  
* duration\_seconds  
* timestamp\_status  
* overall\_score  
* ranking  
* validation\_status

For multi-episode or multi-segment candidates, source references should be represented without losing segment information.

---

## **8\. External Gemini API Integration**

### **8.1 Purpose**

The Gemini API provides language-model capabilities for understanding screenplay content and generating candidate promotional segments.

### **8.2 Authentication**

The API key must be stored securely in an environment variable or Streamlit secrets.

Example `.env` entry:

```
GEMINI_API_KEY=your_api_key_here
```

Never commit the real API key to GitHub.

### **8.3 Request Structure**

The application will send:

* A structured prompt.  
* Relevant screenplay content.  
* Output-format instructions.  
* Constraints against inventing unsupported story events.

### **8.4 Expected Response**

The model should return structured JSON containing:

* Scene analysis.  
* Hook.  
* Cliffhanger.  
* Selected screenplay content.  
* Source references.  
* Quality evaluation.

The application must validate the response before using it.

### **8.5 API Error Handling**

| Error | Handling |
| ----- | ----- |
| Authentication failure | Report invalid API configuration |
| Rate limit | Retry with controlled backoff or report limit |
| Network failure | Allow retry |
| Invalid response | Parse and validate; flag if unsuccessful |
| Empty response | Report generation failure |
| Token limit | Reduce chunk size and retry when appropriate |

The application should use the currently supported Gemini SDK and model configuration rather than hardcoding an outdated model identifier.

---

## **9\. Common Data Format**

All internal modules should exchange structured dictionaries or validated Pydantic objects.

A promo candidate should contain:

```
{
  "promo_id": "PROMO_001",
  "source_segments": [],
  "selected_content": "Screenplay excerpt",
  "hook": "Hook explanation",
  "cliffhanger": "Cliffhanger explanation",
  "duration_seconds": null,
  "timestamp_status": "unavailable",
  "scores": {},
  "overall_score": null,
  "ranking": null,
  "validation_status": "pending",
  "warnings": []
}
```

All modules should follow consistent field names and data types.

---

## **10\. API Security**

* API keys must be stored in environment variables or deployment secrets.  
* Never expose credentials in UI output or logs.  
* Validate uploaded files before processing.  
* Avoid sending unnecessary screenplay content to external services.  
* Do not publish confidential assignment scripts or raw outputs.  
* Validate external AI responses before storing or displaying them.

---

## **11\. Future REST API Design**

A separate REST API is not required for the initial prototype.

If PromoAI is later expanded into a multi-user application, FastAPI can provide endpoints such as:

| Method | Endpoint | Purpose |
| ----- | ----- | ----- |
| POST | `/api/v1/episodes/upload` | Upload screenplay files |
| POST | `/api/v1/analysis` | Start screenplay analysis |
| GET | `/api/v1/analysis/{session_id}` | Retrieve analysis status |
| GET | `/api/v1/promos/{session_id}` | Retrieve promo recommendations |
| GET | `/api/v1/promos/{promo_id}` | Retrieve one promo |
| POST | `/api/v1/promos/{promo_id}/feedback` | Submit user feedback |
| GET | `/api/v1/exports/{session_id}` | Export results |

These endpoints are future design proposals and are not part of the initial Streamlit implementation.

---

## **12\. Conclusion**

This API documentation defines the communication interfaces between PromoAI modules and the external Gemini AI service.

The design keeps the initial implementation simple through internal Python interfaces while allowing future migration to a REST-based architecture if required.

**Document Status:** Version 1.0 – Pre-Development Draft

