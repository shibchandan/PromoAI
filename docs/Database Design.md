# **Database Design Document**

## **PromoAI – AI-Powered Microdrama Promo Finder**

**Version:** 1.0  
**Status:** Pre-Development Draft  
**Primary Storage:** JSON  
**Optional Database:** SQLite  
**Backend:** Python 3.12

---

## **1\. Introduction**

### **1.1 Purpose**

This document defines the data storage architecture, logical entities, data structures, relationships, and storage operations for PromoAI.

The application analyzes screenplay files, identifies potential promotional segments, evaluates their quality, and stores ranked recommendations.

### **1.2 Database Objectives**

The storage design should:

* Maintain screenplay episode information.  
* Store parsed scenes and source references.  
* Store generated promo candidates.  
* Maintain evaluation scores and rankings.  
* Store validation results and warnings.  
* Preserve user feedback.  
* Support JSON and CSV exports.  
* Protect confidential screenplay content.

---

## **2\. Storage Architecture**

### **2.1 Selected Storage Approach**

The initial prototype will use JSON files for structured outputs and temporary application data.

SQLite may be introduced when persistent storage and querying across multiple analysis sessions are required.

| Storage | Purpose |
| ----- | ----- |
| Uploaded TXT files | Original screenplay inputs |
| JSON | Structured analysis results |
| SQLite (optional) | Persistent metadata and feedback |
| CSV | Exported promo recommendations |

### **2.2 Storage Architecture Diagram**

```
flowchart TD
    A[Screenplay TXT Files] --> B[File Processor]
    B --> C[Screenplay Parser]
    C --> D[Scene Data]
    D --> E[AI Analysis]
    E --> F[Promo Candidates]
    F --> G[Validation and Ranking]
    G --> H[Structured JSON Results]
    H --> I[Streamlit Dashboard]
    H --> J[CSV Export]
    H --> K[Optional SQLite Database]
```

---

## **3\. Entity Identification**

The system will use the following logical entities.

| Entity | Purpose |
| ----- | ----- |
| AnalysisSession | Represents one screenplay analysis run |
| Episode | Stores episode metadata |
| Scene | Stores parsed screenplay sections |
| PromoCandidate | Stores generated promo recommendations |
| PromoScore | Stores individual evaluation scores |
| ValidationResult | Stores validation status and warnings |
| UserFeedback | Stores human review feedback |

---

## **4\. Entity Descriptions**

### **4.1 AnalysisSession**

Represents a single analysis operation.

| Attribute | Data Type | Description |
| ----- | ----- | ----- |
| session\_id | String | Unique analysis identifier |
| created\_at | DateTime | Analysis creation time |
| total\_episodes | Integer | Number of uploaded episodes |
| total\_candidates | Integer | Number of generated candidates |
| status | String | Processing status |
| model\_name | String | AI model used, if applicable |

### **4.2 Episode**

Stores information about each screenplay episode.

| Attribute | Data Type | Description |
| ----- | ----- | ----- |
| episode\_id | String | Unique episode identifier |
| session\_id | String | Associated analysis session |
| filename | String | Original filename |
| content | Text | Extracted screenplay text |
| processing\_status | String | Processing result |
| error\_message | Text | Error information, if any |

### **4.3 Scene**

Stores screenplay sections identified by the parser.

| Attribute | Data Type | Description |
| ----- | ----- | ----- |
| scene\_id | String | Unique scene identifier |
| episode\_id | String | Associated episode |
| scene\_order | Integer | Position in episode |
| scene\_text | Text | Original scene text |
| start\_line | Integer | Starting source line, if available |
| end\_line | Integer | Ending source line, if available |

### **4.4 PromoCandidate**

Stores the generated promotional segment.

| Attribute | Data Type | Description |
| ----- | ----- | ----- |
| promo\_id | String | Unique promo identifier |
| session\_id | String | Associated analysis session |
| hook | Text | Opening hook |
| selected\_content | Text | Selected screenplay excerpt |
| cliffhanger | Text | Unresolved ending |
| emotional\_impact | Text | Emotional appeal explanation |
| duration\_seconds | Integer/Float | Segment duration, if established |
| timestamp\_status | String | Verified, estimated, or unavailable |
| overall\_score | Float | Weighted score |
| ranking | Integer | Candidate position |
| status | String | Generated, validated, or flagged |

### **4.5 PromoSourceSegment**

A candidate may use one continuous segment or multiple moments from different episodes. This entity preserves the source information for each segment.

| Attribute | Data Type | Description |
| ----- | ----- | ----- |
| source\_segment\_id | String | Unique source segment identifier |
| promo\_id | String | Associated promo |
| episode\_id | String | Source episode |
| scene\_id | String | Source scene, if available |
| start\_time | String | Start timestamp, if available |
| end\_time | String | End timestamp, if available |
| source\_reference | String | Source line or text reference |
| sequence\_order | Integer | Segment order in promo |

### **4.6 PromoScore**

Stores individual evaluation criteria.

| Attribute | Data Type | Description |
| ----- | ----- | ----- |
| score\_id | String | Unique score identifier |
| promo\_id | String | Associated promo |
| hook\_score | Float | Hook strength |
| emotional\_score | Float | Emotional impact |
| cliffhanger\_score | Float | Cliffhanger strength |
| coherence\_score | Float | Story coherence |
| suitability\_score | Float | Promo suitability |
| overall\_score | Float | Weighted score |

All individual scores should be between 0 and 10\.

### **4.7 ValidationResult**

Stores quality checks for each candidate.

| Attribute | Data Type | Description |
| ----- | ----- | ----- |
| validation\_id | String | Unique validation identifier |
| promo\_id | String | Associated promo |
| validation\_status | String | Passed, warning, or failed |
| source\_check | Boolean | Source reference check |
| timestamp\_check | Boolean | Timestamp consistency check |
| evidence\_check | Boolean | Evidence verification |
| warnings | JSON/Text | Validation warnings |
| validated\_at | DateTime | Validation time |

A timestamp check should distinguish between a valid timestamp format and a timestamp that is actually verified against video timing. These are not the same.

### **4.8 UserFeedback**

Stores user review information.

| Attribute | Data Type | Description |
| ----- | ----- | ----- |
| feedback\_id | String | Unique feedback identifier |
| promo\_id | String | Associated promo |
| feedback\_type | String | Suitable or unsuitable |
| comment | Text | Optional feedback |
| created\_at | DateTime | Feedback creation time |

---

## **5\. Entity Relationship Diagram**

```
erDiagram
    ANALYSIS_SESSION ||--o{ EPISODE : contains
    ANALYSIS_SESSION ||--o{ PROMO_CANDIDATE : generates
    EPISODE ||--o{ SCENE : contains
    PROMO_CANDIDATE ||--o{ PROMO_SOURCE_SEGMENT : references
    EPISODE ||--o{ PROMO_SOURCE_SEGMENT : provides
    SCENE ||--o{ PROMO_SOURCE_SEGMENT : supports
    PROMO_CANDIDATE ||--|| PROMO_SCORE : has
    PROMO_CANDIDATE ||--|| VALIDATION_RESULT : receives
    PROMO_CANDIDATE ||--o{ USER_FEEDBACK : receives
```

The relationship diagram describes the logical model. In the initial JSON implementation, these relationships will be represented using identifiers rather than relational database constraints.

---

## **6\. Database Schema (SQLite – Optional)**

If SQLite is introduced, the following tables can be created.

### **6.1 Analysis Session Table**

```
CREATE TABLE analysis_sessions (
    session_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    total_episodes INTEGER DEFAULT 0,
    total_candidates INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    model_name TEXT
);
```

### **6.2 Episode Table**

```
CREATE TABLE episodes (
    episode_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    content TEXT,
    processing_status TEXT NOT NULL,
    error_message TEXT,
    FOREIGN KEY (session_id)
        REFERENCES analysis_sessions(session_id)
);
```

### **6.3 Scene Table**

```
CREATE TABLE scenes (
    scene_id TEXT PRIMARY KEY,
    episode_id TEXT NOT NULL,
    scene_order INTEGER NOT NULL,
    scene_text TEXT NOT NULL,
    start_line INTEGER,
    end_line INTEGER,
    FOREIGN KEY (episode_id)
        REFERENCES episodes(episode_id)
);
```

### **6.4 Promo Candidate Table**

```
CREATE TABLE promo_candidates (
    promo_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    hook TEXT,
    selected_content TEXT,
    cliffhanger TEXT,
    emotional_impact TEXT,
    duration_seconds REAL,
    timestamp_status TEXT,
    overall_score REAL,
    ranking INTEGER,
    status TEXT NOT NULL,
    FOREIGN KEY (session_id)
        REFERENCES analysis_sessions(session_id)
);
```

### **6.5 Promo Source Segment Table**

```
CREATE TABLE promo_source_segments (
    source_segment_id TEXT PRIMARY KEY,
    promo_id TEXT NOT NULL,
    episode_id TEXT NOT NULL,
    scene_id TEXT,
    start_time TEXT,
    end_time TEXT,
    source_reference TEXT,
    sequence_order INTEGER NOT NULL,
    FOREIGN KEY (promo_id)
        REFERENCES promo_candidates(promo_id),
    FOREIGN KEY (episode_id)
        REFERENCES episodes(episode_id),
    FOREIGN KEY (scene_id)
        REFERENCES scenes(scene_id)
);
```

### **6.6 Promo Score Table**

```
CREATE TABLE promo_scores (
    score_id TEXT PRIMARY KEY,
    promo_id TEXT UNIQUE NOT NULL,
    hook_score REAL,
    emotional_score REAL,
    cliffhanger_score REAL,
    coherence_score REAL,
    suitability_score REAL,
    overall_score REAL,
    FOREIGN KEY (promo_id)
        REFERENCES promo_candidates(promo_id)
);
```

### **6.7 Validation Result Table**

```
CREATE TABLE validation_results (
    validation_id TEXT PRIMARY KEY,
    promo_id TEXT UNIQUE NOT NULL,
    validation_status TEXT NOT NULL,
    source_check INTEGER,
    timestamp_check INTEGER,
    evidence_check INTEGER,
    warnings TEXT,
    validated_at TEXT,
    FOREIGN KEY (promo_id)
        REFERENCES promo_candidates(promo_id)
);
```

### **6.8 User Feedback Table**

```
CREATE TABLE user_feedback (
    feedback_id TEXT PRIMARY KEY,
    promo_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL,
    comment TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (promo_id)
        REFERENCES promo_candidates(promo_id)
);
```

---

## **7\. JSON Storage Design**

For the first prototype, the complete output of one analysis session can be stored as a JSON document.

Example:

```
{
  "session_id": "SESSION_001",
  "status": "completed",
  "episodes": [
    {
      "episode_id": "EP_01",
      "filename": "episode_01.txt",
      "processing_status": "success"
    }
  ],
  "promo_candidates": [
    {
      "promo_id": "PROMO_001",
      "source_segments": [
        {
          "episode_id": "EP_01",
          "scene_id": "EP_01_SC_01",
          "start_time": null,
          "end_time": null,
          "source_reference": "EP_01_SC_01",
          "sequence_order": 1
        }
      ],
      "hook": "Opening hook explanation",
      "cliffhanger": "Unresolved ending explanation",
      "duration_seconds": null,
      "timestamp_status": "unavailable",
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
  ]
}
```

This is an illustrative schema, not a real analysis result.

---

## **8\. Data Relationships and Constraints**

The following rules shall apply:

1. Every episode must belong to an analysis session.  
2. Every scene must belong to an episode.  
3. Every promo candidate must belong to an analysis session.  
4. Every promo source segment must reference an existing episode.  
5. A source segment should reference a scene when scene identification is available.  
6. Every promo candidate should have one evaluation result.  
7. Every promo candidate should have one validation result.  
8. A promo candidate may receive multiple feedback records.  
9. Scores must be within the range 0–10.  
10. Rankings should be generated after candidate scoring.  
11. Missing timestamps must be represented as null, not fabricated values.  
12. Each candidate must preserve enough source information to trace its content to the original screenplay.

---

## **9\. Indexing Strategy**

If SQLite is used, the following indexes may improve query performance:

```
CREATE INDEX idx_episode_session
ON episodes(session_id);

CREATE INDEX idx_scene_episode
ON scenes(episode_id);

CREATE INDEX idx_promo_session
ON promo_candidates(session_id);

CREATE INDEX idx_promo_score
ON promo_candidates(overall_score);

CREATE INDEX idx_feedback_promo
ON user_feedback(promo_id);
```

---

## **10\. Data Security and Privacy**

* API keys must not be stored in database records.  
* Uploaded screenplay files must not be included in a public repository.  
* Confidential screenplay content should not be exposed through public URLs.  
* Generated outputs should be stored locally unless secure deployment storage is configured.  
* Application logs should avoid storing API credentials or unnecessary screenplay content.  
* Temporary files should be cleaned up when no longer required.

---

## **11\. Backup and Recovery**

For the initial prototype:

* Preserve original input files separately.  
* Save completed analysis results as JSON.  
* Avoid overwriting previous session outputs.  
* Use unique session identifiers.  
* Handle incomplete analysis sessions separately from completed results.

For SQLite deployment, create backups before schema changes or destructive operations.

---

## **12\. Future Enhancements**

Possible future improvements include:

* PostgreSQL for multi-user deployment.  
* Database-backed analysis history.  
* Persistent user feedback.  
* Search and filtering across promo candidates.  
* Version tracking for AI prompts and model configurations.  
* Analytics on human-approved recommendations.

---

## **13\. Conclusion**

The proposed storage architecture provides a structured way to manage screenplay episodes, scenes, promo candidates, source references, evaluation scores, validation results, and user feedback.

JSON is recommended for the initial assignment prototype because it reduces implementation complexity. SQLite provides a migration path when persistent querying and feedback management become necessary.

**Document Status:** Version 1.0 – Pre-Development Draft

