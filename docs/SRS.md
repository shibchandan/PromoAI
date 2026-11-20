# **Software Requirements Specification (SRS)**

## **PromoAI – AI-Powered Microdrama Promo Finder**

**Version:** 1.0  
**Status:** Pre-Development Draft  
**Project Type:** AI-Powered Web Application  
**Target Platform:** Web  
**Prepared For:** Kuku FM AI Generalist Assignment

---

## **1\. Introduction**

### **1.1 Purpose**

This document defines the functional and non-functional requirements of PromoAI, an AI-powered application designed to identify, evaluate, and rank promotional video opportunities from microdrama screenplay scripts.

The system will analyze screenplay episodes, identify emotionally engaging story moments, and recommend suitable promo segments lasting approximately 20–60 seconds.

### **1.2 Scope**

PromoAI will accept screenplay files as input, process their content, identify potential promotional moments, and generate structured recommendations.

Each recommended promo should include:

* Episode number and source identification.  
* Start and end timestamps, where supported by the input or a reliable timing-estimation method.  
* Opening hook.  
* Main story moment.  
* Unresolved cliffhanger or suspense element.  
* Explanation of why the segment could work as a promo.  
* Quality score and ranking.

The system will also provide a way to review and correct weak or inaccurate AI recommendations.

### **1.3 Intended Users**

* Content and creative teams.  
* Microdrama marketing teams.  
* Promo editors.  
* AI content analysts.

### **1.4 Definitions**

| Term | Meaning |
| ----- | ----- |
| Microdrama | Short-form episodic drama content |
| Promo | Short promotional clip used to attract viewers |
| Hook | Opening moment designed to capture attention |
| Cliffhanger | Unresolved event that creates curiosity |
| Episode | Individual screenplay installment |
| Segment | A selected portion of screenplay content |
| LLM | Large Language Model |

---

## **2\. Overall Description**

### **2.1 Product Perspective**

PromoAI will operate as a standalone web application. It will combine screenplay processing, AI-based scene analysis, rule-based validation, and ranking.

### **2.2 Product Functions**

The application is expected to:

1. Accept screenplay files in supported formats.  
2. Extract and organize screenplay text by episode.  
3. Identify emotionally engaging and suspenseful moments.  
4. Generate candidate promo segments.  
5. Evaluate opening hooks and cliffhangers.  
6. Check promo duration and content continuity.  
7. Score and rank candidate promos.  
8. Display recommendations with explanations.  
9. Allow users to review and flag unsuitable recommendations.  
10. Export results in a structured format.

### **2.3 User Characteristics**

Users are expected to have basic computer knowledge. No programming or AI expertise should be required to upload scripts and review recommendations.

### **2.4 Operating Environment**

* Operating System: Windows, macOS, or Linux.  
* Frontend: Streamlit web interface.  
* Backend: Python 3.12.  
* AI Integration: Gemini API through a provider abstraction.  
* Data Storage: JSON initially, with SQLite where persistent records are needed.  
* Version Control: Git and GitHub.

---

## **3\. Functional Requirements**

### **FR-01: Screenplay Upload**

The system shall allow users to upload screenplay files.

**Expected behaviour:**

* Accept supported text-based screenplay files, initially `.txt`.  
* Support multiple episode files in one submission.  
* Display uploaded filenames.  
* Reject unsupported or empty files with a clear error message.

### **FR-02: Screenplay Processing**

The system shall extract screenplay text and organize it episode-wise.

**Expected behaviour:**

* Read each uploaded file.  
* Identify episode information from filenames or available script metadata.  
* Preserve the original screenplay text.  
* Detect empty, unreadable, or malformed files.  
* Maintain a reference to the source episode for every extracted segment.

### **FR-03: Candidate Promo Detection**

The system shall identify potential promotional moments from screenplay content.

**Expected behaviour:**

* Analyze dialogue, actions, conflicts, emotional changes, and suspense.  
* Identify moments suitable for independent promotion.  
* Prefer coherent, continuous story stretches.  
* Permit combining moments from different episodes only when the final recommendation clearly identifies each source segment.  
* Avoid generating unsupported story events.

### **FR-04: Hook Identification**

The system shall identify an attention-grabbing opening for each candidate promo.

**Expected behaviour:**

* Identify a strong opening line, action, conflict, or surprising moment.  
* Prefer hooks that create immediate curiosity.  
* Explain why the selected opening may attract viewers.

### **FR-05: Cliffhanger Identification**

The system shall identify the suspenseful or unresolved ending of each candidate promo.

**Expected behaviour:**

* Detect unanswered questions, revelations, threats, emotional confrontations, or unresolved conflicts.  
* Explain what makes the ending intriguing.  
* Flag candidates that do not have a convincing unresolved ending.

### **FR-06: Duration and Timestamp Handling**

The system shall evaluate whether candidate promos meet the target duration of approximately 20–60 seconds.

**Expected behaviour:**

* Provide start and end timestamps when reliable timing information is available.  
* If timestamps are not present in the screenplay, clearly label estimated timestamps and explain the estimation basis.  
* Never present invented timestamps as verified source timestamps.  
* Flag candidates whose duration cannot be reliably established.

### **FR-07: Promo Quality Evaluation**

The system shall evaluate candidate promos against defined quality criteria.

Proposed evaluation dimensions:

| Criterion | Proposed Weight |
| ----- | ----- |
| Opening hook strength | 25% |
| Emotional impact | 20% |
| Cliffhanger strength | 25% |
| Story coherence | 15% |
| Promo suitability and duration | 15% |

The weights are initial design assumptions and may be adjusted after testing.

### **FR-08: Ranking**

The system shall rank candidate promos based on their evaluation scores.

**Expected behaviour:**

* Display the highest-scoring candidates first.  
* Show individual criterion scores where available.  
* Provide a short explanation for each ranking.  
* Avoid treating the score as a guarantee of marketing performance.

### **FR-09: Quality Validation**

The system shall validate AI-generated recommendations before displaying them as final results.

Validation shall check:

* Required fields are present.  
* Episode references match uploaded files.  
* Timestamps follow a valid format.  
* Duration is within the target range or explicitly flagged.  
* The selected segment has a coherent explanation.  
* The hook and cliffhanger are supported by screenplay content.  
* Unsupported or uncertain claims are flagged.

### **FR-10: User Review and Feedback**

The system shall allow users to review generated recommendations.

Users should be able to:

* View the selected screenplay excerpts.  
* Inspect the hook and cliffhanger explanations.  
* Mark a recommendation as suitable or unsuitable.  
* Flag incorrect episode references, timestamps, or story interpretations.

### **FR-11: Results Export**

The system shall allow users to export generated results in a structured format, initially JSON and/or CSV.

The exported data shall preserve episode references, segment information, scores, explanations, and validation warnings.

---

## **4\. External Interface Requirements**

### **4.1 User Interface**

The application shall provide:

* A screenplay upload section.  
* An analysis progress indicator.  
* A results dashboard.  
* Ranked promo recommendations.  
* Detailed views of individual recommendations.  
* Validation warnings and user feedback controls.  
* An export option.

### **4.2 Software Interfaces**

| Component | Purpose |
| ----- | ----- |
| Streamlit | Web application interface |
| Python | Application logic and processing |
| Gemini API | AI-based screenplay analysis |
| JSON | Structured input/output data |
| SQLite | Optional persistent storage |
| Pydantic | Output structure validation |

### **4.3 File Interface**

Initial supported input: `.txt` screenplay files.

Initial output formats: `.json` and `.csv`.

---

## **5\. Non-Functional Requirements**

### **NFR-01: Accuracy**

The system should ground its recommendations in the uploaded screenplay and avoid unsupported dialogue, events, episode references, or timestamps.

### **NFR-02: Reliability**

The system should handle invalid files, API errors, incomplete AI responses, and processing failures gracefully.

### **NFR-03: Usability**

The interface should be simple and understandable for users without technical knowledge.

### **NFR-04: Performance**

The application should process screenplay files in manageable chunks and provide progress feedback during longer analysis tasks.

### **NFR-05: Scalability**

The architecture should support processing multiple episodes and allow future improvements to the AI provider or processing pipeline.

### **NFR-06: Maintainability**

The application should use modular components so that file processing, AI analysis, ranking, and validation can be modified independently.

### **NFR-07: Security and Privacy**

* API keys shall be stored in environment variables or Streamlit secrets.  
* API keys shall not be committed to GitHub.  
* Uploaded screenplay content shall not be exposed publicly.  
* Temporary and generated files shall be handled carefully.

---

## **6\. Data Requirements**

### **6.1 Input Data**

Each screenplay input should contain:

* Filename.  
* Episode identifier, if available.  
* Screenplay text.  
* Optional scene headings or timing information.

### **6.2 Output Data**

Each candidate promo should contain:

| Field | Description |
| ----- | ----- |
| promo\_id | Unique recommendation identifier |
| episode\_id | Source episode identifier |
| start\_time | Segment starting timestamp or estimate |
| end\_time | Segment ending timestamp or estimate |
| duration | Segment duration |
| selected\_content | Relevant screenplay excerpt |
| hook | Opening hook |
| cliffhanger | Unresolved ending |
| emotional\_impact | Explanation of emotional appeal |
| score | Overall evaluation score |
| ranking | Position among candidates |
| explanation | Reason for recommendation |
| validation\_status | Validation result and warnings |

---

## **7\. Error Handling Requirements**

The application shall provide understandable error messages for:

* Unsupported file formats.  
* Empty screenplay files.  
* Invalid screenplay content.  
* Missing episode identification.  
* AI API failures or rate limits.  
* Invalid or incomplete AI responses.  
* Missing timestamps or unreliable duration estimates.  
* Export failures.

The application should not silently discard failed episodes or display incomplete results as fully validated recommendations.

---

## **8\. Testing Requirements**

The system shall be tested using:

1. A valid single-episode screenplay.  
2. Multiple screenplay files.  
3. An empty screenplay file.  
4. A file with missing episode information.  
5. A screenplay with strong opening hooks.  
6. A screenplay with unresolved cliffhangers.  
7. A screenplay with no obvious promotional moment.  
8. An AI response containing invalid JSON.  
9. An AI response with unsupported episode references.  
10. A candidate with missing or estimated timestamps.

Testing shall include both normal operation and failure scenarios.

---

## **9\. Acceptance Criteria**

The initial version will be considered ready for demonstration when:

* Users can upload supported screenplay files.  
* The system can process multiple episodes.  
* Candidate promos can be generated with source references.  
* Each candidate includes a hook and cliffhanger explanation.  
* Recommendations are scored and ranked.  
* Validation checks identify missing or unsupported information.  
* Users can inspect recommendations and export results.  
* The application handles common input and API errors without crashing.  
* The prototype can be run using documented setup instructions.

---

## **10\. Assumptions and Limitations**

* Screenplay text may not contain actual video timestamps.  
* Timestamp estimation from dialogue or word count is approximate and must be labelled accordingly.  
* Screenplay analysis cannot fully determine visual performance, acting quality, music, or editing suitability.  
* AI-generated recommendations require human review.  
* Promo scores are heuristic indicators, not measured audience engagement.  
* The initial prototype focuses on text-based screenplay analysis rather than direct video editing.

---

**Document Status:** Version 1.0 – Pre-Development Draft  
**Next Step:** Implement the requirements incrementally and update this document when actual prototype behaviour has been tested.

