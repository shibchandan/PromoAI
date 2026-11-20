# **Product Requirements Document (PRD)**

# **PromoAI – AI-Powered Microdrama Promo Finder**

| Document Information | Details |
| ----- | ----- |
| Project Name | PromoAI |
| Document Type | Product Requirements Document (PRD) |
| Version | 1.0 |
| Status | Draft – Pre-Development |
| Project Category | AI-Powered Content Analysis |
| Target Organization | Kuku |
| Selected Assignment | Problem 1 – Find the Promos (Ads) |
| Proposed Frontend | Streamlit |
| Proposed Backend | Python |
| AI Integration | Gemini API / Replaceable LLM Provider |
| Primary Dataset | Kuku-provided 50-episode screenplay input pack |

---

# **1\. Product Overview**

## **1.1 Introduction**

PromoAI is an AI-powered application designed to automatically identify, evaluate, and rank promotional moments from microdrama screenplays.

Microdramas are short-form vertical storytelling series consisting of episodes typically lasting 1–2 minutes. Platforms such as Kuku publish AI-generated microdramas and require engaging promotional content to attract new viewers.

Currently, editors manually watch episodes and identify interesting scenes that can be converted into promotional clips. This process requires significant human effort and becomes increasingly difficult as the number of shows and episodes grows.

PromoAI aims to reduce this manual effort by analysing screenplay content and recommending suitable promotional segments using AI-based scene understanding and rule-based evaluation.

The system will identify moments containing:

* Strong opening hooks.  
* Emotional confrontations.  
* Unexpected revelations.  
* Suspenseful situations.  
* Dramatic dialogue.  
* Unresolved cliffhangers.

The application will generate structured recommendations containing episode information, timestamps, hooks, cliffhangers, explanations, and ranking scores.

## **1.2 Product Vision**

To build an intelligent and reusable promotional-content discovery system that helps content editors identify engaging microdrama moments efficiently and consistently.

The goal is not to replace human editors but to provide AI-assisted recommendations that make promotional content selection faster and more systematic.

---

# **2\. Problem Statement**

Microdrama production generates multiple episodes regularly. Identifying the best promotional moments manually requires editors to review scripts or watch episodes individually.

This creates several challenges:

1. **Time Consumption:** Reviewing multiple episodes manually requires significant effort.  
2. **Inconsistent Selection:** Different editors may select different promotional moments based on subjective judgment.  
3. **Missed Opportunities:** Interesting hooks, emotional scenes, and cliffhangers may be overlooked.  
4. **Scalability:** Manual promotional selection becomes difficult when the number of shows and episodes increases.  
5. **Lack of Structured Evaluation:** There may be no consistent scoring mechanism to compare different promotional opportunities.

PromoAI addresses these challenges by analysing screenplay content and generating ranked promotional recommendations.

---

# **3\. Product Objectives**

The primary objectives of PromoAI are:

1. Automatically analyse screenplay files containing scene descriptions, dialogue, actions, and timestamps.  
2. Identify potential promotional moments across multiple episodes.  
3. Detect strong opening hooks within the first three seconds of a proposed promo.  
4. Identify unresolved moments that can serve as cliffhangers.  
5. Recommend promotional segments lasting between 20 and 60 seconds.  
6. Support promos consisting of one continuous segment or multiple segments.  
7. Rank recommendations based on promotional potential.  
8. Provide explanations for every recommendation.  
9. Allow human editors to review and validate AI-generated results.  
10. Generate structured and reusable output files.

---

# **4\. Target Users**

## **4.1 Primary User – Content Editor**

Content editors are responsible for identifying interesting moments from microdrama episodes and preparing promotional clips.

Their requirements include:

* Quickly discovering interesting scenes.  
* Identifying suitable start and end timestamps.  
* Understanding why a particular scene works as a promo.  
* Comparing multiple recommendations.  
* Reviewing AI-generated suggestions before publishing.

## **4.2 Secondary User – Content Marketing Team**

The marketing team uses promotional clips to attract viewers through platforms such as:

* Instagram Reels.  
* YouTube Shorts.  
* TikTok.

Their requirements include engaging hooks, suspenseful endings, and self-contained promotional narratives.

## **4.3 Project Evaluator**

The evaluator reviews the application's functionality, technical implementation, output quality, and scalability.

Their requirements include:

* A working prototype.  
* Reproducible results.  
* Clear explanations.  
* Testing evidence.  
* Honest identification of system limitations.

---

# **5\. Project Scope**

## **5.1 In-Scope Features**

The initial version of PromoAI will include the following features.

### **A. Screenplay Upload and Processing**

* Upload screenplay text files.  
* Support multiple episode files.  
* Read and process episode content.  
* Extract episode identifiers.  
* Identify scene descriptions, dialogue, actions, and timestamps.  
* Handle missing or incorrectly formatted information gracefully.

### **B. Screenplay Analysis**

* Analyse dialogue and scene descriptions.  
* Understand dramatic context.  
* Identify emotional moments.  
* Detect confrontations and revelations.  
* Identify suspenseful situations.  
* Detect potential promotional opportunities.

### **C. Hook Detection**

Identify moments capable of attracting a viewer's attention.

Examples:

* Unexpected statements.  
* Shocking revelations.  
* Emotional confrontations.  
* Sudden actions.  
* Surprising discoveries.

The system should prioritize hooks that occur within the first three seconds of the proposed promotional clip.

### **D. Cliffhanger Detection**

Identify moments that end with unresolved tension.

Examples:

* A character discovers a secret.  
* A character is about to reveal important information.  
* An unexpected person appears.  
* A confrontation begins but remains unresolved.  
* An important question remains unanswered.

### **E. Promo Segment Identification**

* Recommend continuous screenplay segments.  
* Support multiple segments when necessary.  
* Identify start and end timestamps for every segment.  
* Ensure the total promotional duration is between 20 and 60 seconds.  
* Preserve chronological order within each segment sequence.

### **F. Promo Ranking**

Rank promotional recommendations based on:

* Hook strength.  
* Cliffhanger strength.  
* Emotional impact.  
* Narrative clarity.  
* Self-contained understanding.  
* Overall promotional potential.

### **G. Recommendation Explanation**

For every recommended promo, provide:

* Episode number.  
* Segment timestamps.  
* Total duration.  
* Hook explanation.  
* Cliffhanger explanation.  
* Reason for recommendation.  
* Ranking score.

### **H. Output Export**

Generate structured JSON outputs containing promotional recommendations.

### **I. Quality Evaluation**

* Validate timestamps.  
* Check duration constraints.  
* Check required output fields.  
* Identify missing or inconsistent information.  
* Review weak promotional recommendations.  
* Record limitations and failure cases.

## **5.2 Out-of-Scope Features**

The initial version will not include:

1. Actual video editing.  
2. Music generation or background audio.  
3. Text overlays or subtitles.  
4. Automatic video rendering.  
5. Direct publishing to social media.  
6. Video footage analysis.  
7. Audience behaviour prediction.  
8. Automatic collection of social media engagement metrics.  
9. Fully autonomous publishing decisions.

These features may be considered in future versions.

---

# **6\. Functional Requirements**

| ID | Requirement | Priority |
| ----- | ----- | ----- |
| FR-01 | The system shall accept screenplay text files. | High |
| FR-02 | The system shall process multiple episodes. | High |
| FR-03 | The system shall extract episode and scene information. | High |
| FR-04 | The system shall extract available timestamps. | High |
| FR-05 | The system shall analyse dialogue and scene descriptions. | High |
| FR-06 | The system shall identify potential promotional moments. | High |
| FR-07 | The system shall identify opening hooks. | High |
| FR-08 | The system shall identify potential cliffhangers. | High |
| FR-09 | The system shall recommend clips lasting 20–60 seconds. | High |
| FR-10 | The system shall support multiple segments per promo. | Medium |
| FR-11 | The system shall rank promotional recommendations. | High |
| FR-12 | The system shall explain each recommendation. | High |
| FR-13 | The system shall export results in JSON format. | High |
| FR-14 | The system shall validate generated timestamps and durations. | High |
| FR-15 | The system shall identify invalid or incomplete recommendations. | High |
| FR-16 | The system shall allow users to review recommendations. | Medium |
| FR-17 | The system shall provide a summary of processing results. | Medium |

---

# **7\. Non-Functional Requirements**

## **7.1 Performance**

* The application should process multiple screenplay files efficiently.  
* Long-running operations should provide progress information.  
* AI requests should be divided into manageable chunks when required.  
* Processing should avoid unnecessary repeated API calls.

## **7.2 Reliability**

* Invalid input files should not crash the entire application.  
* Failed AI requests should be handled gracefully.  
* Output validation should occur before recommendations are exported.  
* Original screenplay files must remain unchanged.

## **7.3 Scalability**

* The architecture should support processing additional episodes.  
* AI integration should be modular.  
* The system should support alternative AI model providers.  
* Processing should be designed to support future batch execution.

## **7.4 Maintainability**

* Code should be organized into separate modules.  
* Business logic should be separated from the user interface.  
* Configuration should be managed through environment variables.  
* Reusable functions should be preferred over duplicated code.

## **7.5 Usability**

* The interface should be simple and understandable.  
* Users should be able to upload files easily.  
* Recommendations should be displayed in a readable format.  
* Errors should be explained clearly.

## **7.6 Security and Confidentiality**

* API keys must not be hardcoded.  
* Secrets must be stored in environment variables.  
* Kuku's screenplay dataset must be treated as confidential.  
* Original screenplay files must not be published publicly.  
* Only authorized users should access the original input data.

---

# **8\. User Workflow**

The expected application workflow is:

1. User opens PromoAI.  
2. User uploads one or more screenplay files.  
3. The application validates the uploaded files.  
4. The screenplay parser extracts scenes, dialogue, actions, and timestamps.  
5. The processed content is passed to the AI analysis module.  
6. The AI identifies potential promotional moments.  
7. The ranking engine evaluates recommendations.  
8. The validation module checks timestamps, duration, and required fields.  
9. The application displays ranked promotional recommendations.  
10. The user reviews the recommendations.  
11. The user exports the results as JSON.

---

# **9\. AI-Based Recommendation Strategy**

PromoAI will use a combination of AI-based semantic analysis and deterministic program logic.

## **9.1 AI Responsibilities**

The AI model will be responsible for:

* Understanding scene context.  
* Identifying dramatic moments.  
* Detecting emotional intensity.  
* Evaluating hook potential.  
* Evaluating cliffhanger potential.  
* Explaining promotional suitability.

## **9.2 Rule-Based Responsibilities**

The application code will handle:

* Timestamp extraction.  
* Duration calculation.  
* Segment ordering.  
* Duration validation.  
* Required-field validation.  
* Duplicate detection.  
* Ranking calculations.  
* Output formatting.

The AI model should not be solely responsible for calculating or validating timestamps.

## **9.3 Proposed Ranking Model**

Each candidate promo will receive a score out of 100\.

| Evaluation Factor | Proposed Weight |
| ----- | ----- |
| Hook Strength | 25% |
| Cliffhanger Strength | 25% |
| Emotional Impact | 20% |
| Narrative Clarity | 15% |
| Self-Contained Understanding | 15% |
| Total | 100% |

Proposed scoring formula:

Promo Score \=

(0.25 × Hook Score) \+

(0.25 × Cliffhanger Score) \+

(0.20 × Emotional Impact Score) \+

(0.15 × Narrative Clarity Score) \+

(0.15 × Self-Contained Score)

Each individual factor will be evaluated on a scale of 0–100.

These weights are initial design assumptions and may be adjusted after evaluating real screenplay outputs.

---

# **10\. Input and Output Requirements**

## **10.1 Input Requirements**

The application will primarily process the screenplay text files provided in the Kuku assignment input pack.

Expected screenplay information includes:

* Episode identifiers.  
* Scene descriptions.  
* Dialogue.  
* Character names.  
* Actions.  
* Scene timestamps.

The system should preserve the original timestamp information and identify missing or invalid timestamps.

## **10.2 Output Requirements**

Each promotional recommendation should contain:

| Field | Description |
| ----- | ----- |
| Promo ID | Unique recommendation identifier |
| Episode | Episode number |
| Segments | Ordered start and end timestamps |
| Total Duration | Combined promotional duration |
| Hook | Opening attention-grabbing moment |
| Cliffhanger | Unresolved ending |
| Explanation | Why the promo works |
| Score | Overall promotional score |
| Rank | Relative recommendation position |

### **Example JSON Output**

```
{
  "promo_id": "PROMO_001",
  "episode": 1,
  "segments": [
    {
      "start": "00:09",
      "end": "00:45"
    }
  ],
  "total_duration_seconds": 36,
  "hook": "An unexpected confrontation",
  "cliffhanger": "A revelation remains unresolved",
  "explanation": "The scene creates immediate curiosity and ends with unresolved tension.",
  "scores": {
    "hook": 90,
    "cliffhanger": 92,
    "emotional_impact": 85,
    "narrative_clarity": 88,
    "self_contained": 84
  },
  "overall_score": 88.5,
  "rank": 1
}
```

This is an illustrative output schema, not an actual analysis result.

---

# **11\. Quality Assurance and Evaluation**

Quality evaluation is a major part of the product.

PromoAI must not assume that every AI-generated recommendation is correct.

The application will use the following validation methods:

## **11.1 Structural Validation**

* Verify that episode identifiers exist.  
* Verify that timestamps are valid.  
* Verify that segment start times precede end times.  
* Verify that total duration is between 20 and 60 seconds.  
* Verify that required output fields are present.  
* Verify that segments are chronologically ordered.

## **11.2 Recommendation Quality Evaluation**

Review whether:

* The opening hook attracts attention.  
* The ending creates curiosity.  
* The clip can be understood independently.  
* The scene contains sufficient dramatic value.  
* The recommended timestamps capture the intended moment.

## **11.3 Failure Analysis**

The system should record examples of:

* Weak or misleading hooks.  
* Cliffhangers that resolve too early.  
* Recommendations that lack context.  
* Incorrect timestamps.  
* Repeated promotional suggestions.  
* AI-generated explanations unsupported by the screenplay.

## **11.4 Human Review**

Human evaluation will be used to assess the quality of AI-generated recommendations.

The application will provide explanations so that editors can accept, reject, or manually review suggestions.

---

# **12\. Success Metrics**

The following metrics will be used to evaluate the prototype.

| Metric | Success Criteria |
| ----- | ----- |
| File Processing | Successfully process valid screenplay files |
| Timestamp Validation | All exported segments pass structural validation |
| Duration Compliance | All accepted recommendations meet 20–60 seconds |
| Output Completeness | All required output fields are populated |
| Recommendation Quality | Recommendations receive human review |
| Ranking Quality | Higher-ranked recommendations demonstrate stronger promotional potential |
| Reproducibility | The application can run again on new screenplay inputs |
| Failure Transparency | Known limitations and failures are documented |

No numerical accuracy target is claimed before actual testing.

---

# **13\. Assumptions and Constraints**

## **13.1 Assumptions**

1. Screenplay files contain usable scene and dialogue information.  
2. Timestamps are available for scenes, dialogue, and key actions, as described in the assignment.  
3. The screenplay dataset represents the first 50 episodes of one English-language microdrama show.  
4. Promotional duration must be between 20 and 60 seconds.  
5. A promo may contain one continuous segment or multiple segments.  
6. The AI model can analyse screenplay text and return structured recommendations.  
7. Human review is necessary before final promotional selection.

## **13.2 Constraints**

1. Development time is limited by the assignment's 48-hour submission window.  
2. The initial implementation should use free-tier tools wherever possible.  
3. AI API usage may be subject to rate limits.  
4. AI-generated recommendations may contain incorrect interpretations.  
5. Screenplay analysis cannot guarantee the actual visual quality of a video scene.  
6. The prototype is expected to operate on text-based screenplay information rather than original video footage.

---

# **14\. Risks and Mitigation**

| Risk | Mitigation |
| ----- | ----- |
| AI hallucination | Validate AI outputs against screenplay content |
| Incorrect timestamps | Use extracted screenplay timestamps and deterministic validation |
| Poor promo selection | Use ranking criteria and human review |
| API failure | Implement retries and clear error handling |
| Large input size | Process episodes and scenes in manageable chunks |
| Duplicate recommendations | Implement overlap and similarity checks |
| Missing context | Include relevant surrounding scenes during analysis |
| API cost limitations | Use caching, batching, and free-tier models where feasible |

---

# **15\. Proposed Technology Stack**

| Layer | Technology | Responsibility |
| ----- | ----- | ----- |
| Frontend | Streamlit | User interface and dashboard |
| Backend | Python | Core application logic |
| AI Integration | Gemini API / Replaceable LLM | Scene understanding and recommendation |
| Text Processing | Python libraries | Parsing screenplay files |
| Data Validation | Pydantic | Structured output validation |
| Data Storage | JSON / SQLite | Store analysis and recommendations |
| Configuration | Python dotenv | Manage environment variables |
| Version Control | Git and GitHub | Source code management |
| Development Environment | Antigravity | AI-assisted development |

The AI provider should be isolated behind a common interface to allow future model replacement.

---

# **16\. Future Enhancements**

Potential future improvements include:

1. Video-based scene verification.  
2. Automatic identification of visual hooks.  
3. Multi-language screenplay support.  
4. Advanced promotional performance prediction.  
5. Editor feedback integration.  
6. Batch processing across multiple shows.  
7. Analytics dashboard for promotional recommendations.  
8. Integration with video editing workflows.

These enhancements are outside the initial assignment scope.

---

# **17\. Acceptance Criteria**

The initial version of PromoAI will be considered ready for assignment demonstration when:

* Users can upload screenplay text files.  
* The system can process multiple episodes.  
* The parser extracts available episode, scene, and timestamp information.  
* The AI module identifies potential promotional moments.  
* Recommendations include hooks and cliffhangers.  
* Each recommendation contains episode and segment timestamps.  
* Recommended total duration is between 20 and 60 seconds.  
* Recommendations are ranked using documented criteria.  
* Results include explanations.  
* JSON output can be downloaded.  
* Structural validation is performed.  
* The prototype has been tested on the provided input pack.  
* Raw outputs and known failure cases are available for review.  
* The application can be run again on new screenplay inputs.

---

# **18\. Final Product Summary**

PromoAI aims to transform the manual discovery of microdrama promotional moments into a structured, AI-assisted workflow.

By combining screenplay parsing, AI-based scene understanding, deterministic validation, and recommendation ranking, the application will help content editors discover potentially engaging promotional moments across multiple episodes.

The system will focus on three important promotional characteristics:

1. A strong opening hook.  
2. An unresolved cliffhanger.  
3. A self-contained narrative that attracts new viewers.

The final product will be a working prototype that produces explainable and testable promotional recommendations while keeping human editors involved in the final selection process.

**End of Document**

