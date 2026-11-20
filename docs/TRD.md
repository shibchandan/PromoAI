# **Technical Requirements Document (TRD)**

# **PromoAI – AI-Powered Microdrama Promo Finder**

| Document Information | Details |
| ----- | ----- |
| Project Name | PromoAI |
| Document Type | Technical Requirements Document |
| Version | 1.0 |
| Status | Draft – Pre-Development |
| Related Document | PRD.md |
| Assignment | Kuku AI Generalist – Problem 1 |
| Frontend | Streamlit |
| Backend | Python |
| AI Provider | Gemini API (initial implementation) |
| Data Storage | JSON / SQLite |
| Development Tool | Antigravity |

---

# **1\. Introduction**

## **1.1 Purpose**

This document defines the technical requirements and implementation approach for PromoAI, an AI-powered application that identifies and ranks promotional moments from microdrama screenplays.

It describes the proposed technology stack, system architecture, application modules, data processing pipeline, AI integration, validation mechanisms, security requirements, deployment approach, and technical constraints.

The purpose is to provide a technical blueprint for developing a working and reusable prototype.

## **1.2 Project Overview**

PromoAI will analyse screenplay text files containing episode information, scene descriptions, dialogue, character actions, and timestamps.

The application will combine:

* Rule-based screenplay parsing.  
* AI-powered scene understanding.  
* Hook and cliffhanger detection.  
* Promotional segment selection.  
* Ranking algorithms.  
* Deterministic output validation.

The system will produce structured promotional recommendations that can be reviewed by content editors.

## **1.3 Technical Goals**

1. Build a modular Python application.  
2. Process multiple screenplay files.  
3. Extract screenplay structure and timestamps.  
4. Integrate an external Large Language Model (LLM).  
5. Generate structured promotional recommendations.  
6. Apply deterministic ranking and validation.  
7. Export results in JSON format.  
8. Support future AI model replacement.  
9. Provide a simple and interactive web interface.  
10. Support reproducible execution on new screenplay inputs.

---

# **2\. Technology Stack**

## **2.1 Frontend**

**Technology: Streamlit**

Purpose:

* Provide an interactive web interface.  
* Allow screenplay file uploads.  
* Display processing progress.  
* Show ranked promotional recommendations.  
* Display hooks, cliffhangers, and explanations.  
* Allow JSON output downloads.

Why Streamlit:

* Python-based development.  
* Minimal frontend configuration.  
* Fast prototyping.  
* Easy integration with Python backend modules.

## **2.2 Backend**

**Technology: Python 3.12**

Purpose:

* Process screenplay files.  
* Extract episode and scene information.  
* Manage AI requests.  
* Execute ranking algorithms.  
* Validate promotional recommendations.  
* Generate structured output.

Python will serve as the primary programming language for the project.

## **2.3 AI Integration**

**Initial Provider: Google Gemini API**

Purpose:

* Understand scene context.  
* Identify emotionally engaging moments.  
* Detect potential opening hooks.  
* Identify unresolved cliffhangers.  
* Evaluate narrative clarity.  
* Generate recommendation explanations.

The AI integration must be modular so that another LLM provider can be introduced without rewriting the complete application.

## **2.4 Data Storage**

**Initial Storage: JSON**

Purpose:

* Store parsed screenplay information.  
* Store AI analysis results.  
* Store promotional recommendations.  
* Export raw outputs.  
* Maintain reproducible analysis results.

**Optional Storage: SQLite**

SQLite may be introduced if persistent querying, historical analysis, or larger datasets require it.

## **2.5 Version Control**

**Technology: Git and GitHub**

Purpose:

* Track source code changes.  
* Maintain project history.  
* Organize development.  
* Share the source code repository with evaluators.

Confidential screenplay input files must not be committed to a public repository.

---

# **3\. System Architecture**

## **3.1 Architectural Overview**

PromoAI will follow a modular, layered architecture.

The application will contain five major layers:

1. Presentation Layer  
2. Application Processing Layer  
3. AI Analysis Layer  
4. Business Logic and Validation Layer  
5. Data Management Layer

### **High-Level Architecture**

```
                  USER
                    |
                    v
          +-------------------+
          |  Streamlit UI     |
          |  Presentation     |
          +-------------------+
                    |
                    v
          +-------------------+
          | Application       |
          | Controller        |
          +-------------------+
                    |
                    v
          +-------------------+
          | Screenplay Parser |
          +-------------------+
                    |
                    v
          +-------------------+
          | Scene Extraction  |
          +-------------------+
                    |
                    v
          +-------------------+
          | AI Analysis       |
          | Provider Layer    |
          +-------------------+
                    |
                    v
          +-------------------+
          | Promo Candidate   |
          | Generation        |
          +-------------------+
                    |
                    v
          +-------------------+
          | Ranking Engine    |
          +-------------------+
                    |
                    v
          +-------------------+
          | Validation Engine |
          +-------------------+
                    |
                    v
          +-------------------+
          | JSON / SQLite     |
          | Output Storage    |
          +-------------------+
                    |
                    v
          +-------------------+
          | Results Dashboard |
          +-------------------+
```

## **3.2 Architecture Principles**

* Separation of concerns.  
* Modular implementation.  
* Reusable processing components.  
* Independent AI provider integration.  
* Deterministic validation.  
* Configurable ranking weights.  
* Human-readable output.  
* Reproducible execution.

---

# **4\. Application Modules**

The application will be divided into independent modules.

## **4.1 User Interface Module**

Proposed file: `app.py`

Responsibilities:

* Display application dashboard.  
* Accept screenplay uploads.  
* Validate uploaded file types.  
* Allow selection of multiple episodes.  
* Start screenplay analysis.  
* Display progress and errors.  
* Display ranked recommendations.  
* Provide downloadable JSON outputs.

Technology: Streamlit.

## **4.2 File Processing Module**

Proposed file: `src/file_processor.py`

Responsibilities:

* Accept uploaded screenplay files.  
* Read text content.  
* Handle file encoding.  
* Validate file extensions.  
* Identify empty or invalid files.  
* Extract episode identifiers.  
* Prepare text for screenplay parsing.

Initial supported format: TXT.

## **4.3 Screenplay Parser Module**

Proposed file: `src/screenplay_parser.py`

Responsibilities:

* Extract episode information.  
* Identify scene boundaries.  
* Extract dialogue.  
* Identify character names where possible.  
* Extract scene descriptions and actions.  
* Extract available timestamps.  
* Preserve the original screenplay text.

The parser should use configurable patterns rather than assuming every episode has an identical structure.

## **4.4 Scene Analysis Module**

Proposed file: `src/scene_analyzer.py`

Responsibilities:

* Prepare scene content for AI analysis.  
* Identify dramatic events.  
* Detect emotional confrontations.  
* Identify shocking revelations.  
* Identify suspenseful situations.  
* Generate candidate promotional moments.

The module will combine extracted screenplay structure with contextual information.

## **4.5 AI Provider Module**

Proposed files:

* `src/ai/base_provider.py`  
* `src/ai/gemini_provider.py`

Responsibilities:

* Define a common AI provider interface.  
* Communicate with the configured AI model.  
* Construct analysis prompts.  
* Send screenplay content.  
* Parse structured AI responses.  
* Handle API errors and rate limits.  
* Support future model replacement.

The Gemini implementation should remain isolated from the main application logic.

## **4.6 Promo Detection Module**

Proposed file: `src/promo_detector.py`

Responsibilities:

* Collect candidate scenes.  
* Identify potential promo start and end points.  
* Evaluate hook strength.  
* Evaluate cliffhanger strength.  
* Support continuous and multi-segment recommendations.  
* Generate candidate promotional outputs.

Candidate timestamps must be grounded in the screenplay's available timestamps.

## **4.7 Ranking Engine**

Proposed file: `src/ranking_engine.py`

Responsibilities:

* Calculate recommendation scores.  
* Apply configurable weights.  
* Compare promotional candidates.  
* Sort recommendations.  
* Assign ranks.  
* Handle missing scoring values.

### **Proposed Scoring Formula**

```
Promo Score =

0.25 * Hook Strength
+
0.25 * Cliffhanger Strength
+
0.20 * Emotional Impact
+
0.15 * Narrative Clarity
+
0.15 * Self-Contained Understanding
```

Each factor will have a value between 0 and 100\.

The formula will be configurable so that ranking weights can be improved after testing.

## **4.8 Validation Module**

Proposed file: `src/validator.py`

Responsibilities:

* Validate episode identifiers.  
* Validate timestamp formats.  
* Check start and end timestamps.  
* Calculate total promotional duration.  
* Ensure duration is between 20 and 60 seconds.  
* Validate required output fields.  
* Check chronological ordering.  
* Identify duplicate recommendations.  
* Reject unsupported or invalid timestamps.

Invalid recommendations should not be silently exported as valid results.

## **4.9 Output Management Module**

Proposed file: `src/output_manager.py`

Responsibilities:

* Convert recommendations into JSON.  
* Save episode-wise outputs.  
* Save combined recommendations.  
* Export ranked promotional results.  
* Preserve raw model outputs where appropriate.  
* Generate processing summaries.

## **4.10 Configuration Module**

Proposed file: `src/config.py`

Responsibilities:

* Load environment variables.  
* Manage API configuration.  
* Define upload limits.  
* Define supported file extensions.  
* Configure AI model settings.  
* Configure ranking weights.  
* Manage application settings.

---

# **5\. Technical Data Processing Pipeline**

The system will follow the pipeline below.

### **Step 1: Input Acquisition**

The user uploads one or more screenplay text files.

### **Step 2: File Validation**

The application checks:

* File extension.  
* File readability.  
* File size.  
* Empty content.  
* Duplicate filenames.

### **Step 3: Text Extraction**

The system reads screenplay text and preserves the original content.

### **Step 4: Structural Parsing**

The parser extracts:

* Episode number.  
* Scene boundaries.  
* Scene descriptions.  
* Character dialogue.  
* Character actions.  
* Available timestamps.

### **Step 5: Content Chunking**

Long screenplay content will be divided into manageable analysis units.

Chunking must preserve sufficient surrounding context to avoid losing narrative meaning.

### **Step 6: AI Analysis**

The AI model analyses screenplay content and identifies:

* Potential hooks.  
* Emotional moments.  
* Dramatic conflicts.  
* Suspenseful moments.  
* Cliffhanger opportunities.  
* Narrative context.

### **Step 7: Candidate Generation**

The application generates possible promotional segments from AI analysis and available screenplay timestamps.

### **Step 8: Ranking**

The ranking engine calculates recommendation scores and sorts candidates.

### **Step 9: Validation**

The validation engine checks timestamps, durations, structure, and completeness.

### **Step 10: Output Generation**

The application saves:

* Episode-wise JSON.  
* Combined promo recommendations.  
* Ranked promotional results.  
* Validation summaries.  
* Processing metadata.

### **Step 11: User Presentation**

The Streamlit interface displays the recommendations and allows JSON downloads.

---

# **6\. AI Integration Requirements**

## **6.1 AI Provider Architecture**

The AI provider must be replaceable.

A common interface will be used:

```
class BaseAIProvider:

    def analyze_scene(self, scene_data):
        raise NotImplementedError

    def analyze_candidates(self, candidates):
        raise NotImplementedError
```

The Gemini provider will implement this interface.

Future providers can implement the same methods.

## **6.2 AI Analysis Input**

The AI model should receive structured information such as:

* Episode identifier.  
* Scene identifier.  
* Scene description.  
* Dialogue.  
* Character actions.  
* Available timestamps.  
* Relevant surrounding context.

## **6.3 AI Analysis Output**

The AI model should return structured information containing:

* Candidate scene identifiers.  
* Hook description.  
* Cliffhanger description.  
* Emotional impact.  
* Narrative clarity.  
* Self-contained understanding.  
* Explanation.  
* Referenced screenplay evidence.

The final timestamps must be checked against the original screenplay data.

## **6.4 Structured Response Validation**

AI responses should be validated before being passed to the ranking engine.

Pydantic models may be used to validate response structures and data types.

Malformed responses should be rejected or retried according to configured limits.

## **6.5 Prompt Management**

AI prompts should be maintained separately from application logic.

Proposed directory:

`prompts/`

Suggested files:

* `scene_analysis.txt`  
* `hook_detection.txt`  
* `cliffhanger_detection.txt`  
* `promo_evaluation.txt`

This will make prompt improvements easier without changing the entire application.

---

# **7\. Data Requirements**

## **7.1 Input Data**

The primary dataset consists of the 50 English-language screenplay episodes provided by Kuku.

The screenplay input pack includes timestamps for scenes, dialogue, and key actions, according to the assignment brief.

Supported initial file format: TXT.

## **7.2 Internal Data Structure**

### **Episode Object**

```
{
  "episode_id": "EP001",
  "episode_number": 1,
  "scenes": []
}
```

### **Scene Object**

```
{
  "scene_id": "EP001_SC001",
  "episode_id": "EP001",
  "description": "Scene description",
  "dialogue": [],
  "actions": [],
  "timestamps": []
}
```

### **Promo Object**

```
{
  "promo_id": "PROMO_001",
  "episode_id": "EP001",
  "segments": [],
  "hook": "Hook description",
  "cliffhanger": "Cliffhanger description",
  "explanation": "Recommendation explanation",
  "scores": {},
  "overall_score": 0,
  "rank": 1
}
```

These are proposed internal schemas and may be refined after examining the actual screenplay format.

---

# **8\. Validation and Quality Control**

## **8.1 Structural Validation**

The application must verify:

* Required fields are present.  
* Episode identifiers are valid.  
* Scene references exist.  
* Timestamps are parseable.  
* Segment start precedes segment end.  
* Total duration is between 20 and 60 seconds.  
* Multiple segments are chronologically ordered.

## **8.2 AI Output Validation**

The system should verify:

* AI-generated scene references exist.  
* Recommendations are supported by screenplay content.  
* Hook descriptions match the referenced content.  
* Cliffhanger explanations are grounded in the screenplay.  
* Missing scoring values are handled explicitly.

## **8.3 Quality Evaluation**

The application should support human review of:

* Hook quality.  
* Cliffhanger quality.  
* Narrative clarity.  
* Promotional suitability.  
* Timestamp accuracy.

Quality reports should include incorrect recommendations and known system limitations.

---

# **9\. Error Handling Requirements**

The application should handle the following scenarios:

| Error Scenario | Expected Handling |
| ----- | ----- |
| Unsupported file type | Display validation error |
| Empty screenplay | Reject file |
| Invalid encoding | Attempt supported decoding or report error |
| Missing timestamps | Mark affected content as incomplete |
| AI API failure | Retry within configured limits |
| API rate limit | Apply backoff or pause processing |
| Invalid AI response | Validate and retry or reject |
| Invalid duration | Reject recommendation |
| Duplicate recommendation | Flag or remove duplicate |
| Missing output fields | Reject incomplete output |

Errors should be logged without exposing API keys or confidential screenplay content unnecessarily.

---

# **10\. Security Requirements**

1. API keys must be stored in environment variables.  
2. `.env` files must be included in `.gitignore`.  
3. Uploaded files must be validated before processing.  
4. File paths must be handled safely.  
5. Confidential screenplay files must not be committed to a public GitHub repository.  
6. Raw screenplay content must not be exposed through public application logs.  
7. Only necessary content should be sent to external AI providers.  
8. Temporary files should be cleaned up when no longer needed.  
9. API credentials must never appear in frontend code or downloadable outputs.

---

# **11\. Performance and Scalability**

## **11.1 Performance**

* Process episodes independently where possible.  
* Avoid sending unnecessary repeated AI requests.  
* Cache analysis results when appropriate.  
* Divide large scripts into manageable chunks.  
* Display progress during lengthy processing.  
* Avoid blocking the user interface unnecessarily.

## **11.2 Scalability**

The initial application should support the provided 50-episode dataset.

Future scalability improvements may include:

* Parallel episode processing.  
* Background task queues.  
* Persistent database storage.  
* Distributed processing.  
* Cloud deployment.  
* Multiple AI provider support.

These improvements are not required for the initial prototype unless actual testing demonstrates a need.

---

# **12\. Proposed Project Structure**

```
PromoAI/
│
├── app.py
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
├── prompts/
│   ├── scene_analysis.txt
│   ├── hook_detection.txt
│   ├── cliffhanger_detection.txt
│   └── promo_evaluation.txt
│
├── input/
│   └── screenplay/
│
├── outputs/
│
├── tests/
│   ├── test_parser.py
│   ├── test_detector.py
│   ├── test_ranking.py
│   └── test_validator.py
│
├── docs/
│   ├── PRD.md
│   └── TRD.md
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

The actual confidential screenplay files will remain local and will not be included in the public source repository.

---

# **13\. Development Environment**

## **13.1 Software Requirements**

| Software | Purpose |
| ----- | ----- |
| Python 3.12 | Application runtime |
| Antigravity | AI-assisted development |
| Git | Version control |
| Streamlit | Web interface |
| Gemini API | AI analysis |
| VS Code-compatible terminal | Development commands |

## **13.2 Python Dependencies**

Initial proposed dependencies:

```
streamlit
google-genai
python-dotenv
pydantic
pandas
```

Additional dependencies may be added when required by the implementation.

Dependency versions must be tested and pinned in the final requirements file.

## **13.3 Environment Configuration**

Example `.env.example`:

```
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=your_selected_model
APP_ENV=development
```

The actual `.env` file must remain private.

---

# **14\. Testing Requirements**

## **14.1 Unit Testing**

Test individual application modules:

* File processing.  
* Screenplay parsing.  
* Timestamp extraction.  
* Promo candidate generation.  
* Ranking calculations.  
* Output validation.

## **14.2 Integration Testing**

Verify the complete pipeline:

* Upload screenplay.  
* Parse content.  
* Analyse scenes.  
* Generate candidates.  
* Rank recommendations.  
* Validate results.  
* Export JSON.

## **14.3 Edge Case Testing**

Test:

* Missing timestamps.  
* Empty episodes.  
* Very long scenes.  
* Invalid timestamp formats.  
* Repeated dialogue.  
* Multiple potential hooks.  
* Missing cliffhangers.  
* Overlapping segments.  
* Invalid AI responses.

## **14.4 Evaluation Testing**

Run the application on the complete provided input pack and evaluate recommendation quality through human review.

Record both successful outputs and failure cases.

---

# **15\. Deployment Requirements**

## **15.1 Local Deployment**

The application should be runnable locally through:

```
pip install -r requirements.txt

streamlit run app.py
```

## **15.2 Public Demonstration**

A public demonstration may be deployed using a suitable hosting platform with free-tier support.

The deployed application must:

* Keep API credentials secure.  
* Avoid exposing Kuku's confidential screenplay dataset.  
* Allow testing with authorized or public sample inputs.  
* Include clear instructions for running the application.

## **15.3 GitHub Repository**

The repository should include:

* Source code.  
* Documentation.  
* Requirements file.  
* Environment example.  
* README.  
* Tests.  
* Non-confidential sample outputs.

The original Kuku screenplay input pack must not be uploaded publicly.

---

# **16\. Technical Constraints**

1. The project must be developed within the assignment's 48-hour submission window.  
2. Free-tier services should be preferred.  
3. AI provider usage may be subject to rate limits.  
4. LLM responses may be inconsistent.  
5. Screenplay timestamps may require normalization.  
6. The application analyses screenplay text and cannot independently verify actual video footage.  
7. The initial prototype does not perform video editing.  
8. Human review remains necessary for final promotional decisions.

---

# **17\. Technical Acceptance Criteria**

The technical implementation will be considered ready for demonstration when:

* The application launches successfully.  
* Multiple screenplay files can be uploaded.  
* Valid screenplay content can be parsed.  
* Episode and scene information can be extracted.  
* The AI provider can analyse screenplay content.  
* Candidate promotional moments can be generated.  
* Hook and cliffhanger descriptions are produced.  
* The ranking engine calculates scores.  
* Timestamp and duration validation works.  
* Invalid recommendations are identified.  
* JSON outputs can be downloaded.  
* The application can be rerun on new inputs.  
* Automated tests are available.  
* Known technical limitations are documented.

---

# **18\. Conclusion**

PromoAI will use a modular Python-based architecture to automate the discovery and evaluation of promotional moments from microdrama screenplays.

By combining Streamlit, Python, an interchangeable LLM provider, structured data validation, and deterministic ranking logic, the system will provide an explainable and reusable promotional discovery workflow.

The architecture prioritizes simplicity, reliability, maintainability, and rapid development while leaving room for future improvements.

The initial implementation will focus on successfully analysing the 50-episode screenplay dataset provided by Kuku and generating validated promotional recommendations.

**End of Document**

