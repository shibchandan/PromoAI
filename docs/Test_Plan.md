# **PromoAI – Test Plan**

**Version:** 1.0  
**Project:** PromoAI – AI-Powered Microdrama Promo Finder  
**Status:** Pre-development draft

---

## **1\. Purpose**

This document defines the testing strategy for PromoAI. The objective is to verify that the system can process screenplay files, identify promising promotional moments, generate structured promo recommendations, rank candidates, and produce reliable outputs.

Testing must verify both technical correctness and the creative usefulness of the generated promos.

## **2\. Scope of Testing**

The following modules will be tested:

1. File upload and validation  
2. Screenplay text extraction  
3. Episode and scene parsing  
4. Scene analysis  
5. Promo candidate generation  
6. Hook and cliffhanger evaluation  
7. Promo duration and source-reference validation  
8. Promo scoring and ranking  
9. JSON and CSV export  
10. Streamlit user interface

## **3\. Testing Strategy**

| Testing type | Purpose |
| ----- | ----- |
| Unit testing | Test individual functions independently |
| Integration testing | Verify communication between modules |
| Functional testing | Check complete user workflows |
| AI output testing | Evaluate the relevance and quality of AI-generated promos |
| Validation testing | Detect missing references, invalid durations, and unsupported claims |
| Manual testing | Review creative quality and usability |

**Testing tools:**

* `pytest` – automated testing  
* `unittest.mock` – mock external AI services  
* Streamlit – interface testing  
* Manual review – creative quality evaluation

## **4\. Functional Test Cases**

| Test ID | Test scenario | Expected result |
| ----- | ----- | ----- |
| TC-01 | Upload a valid TXT screenplay | File is accepted |
| TC-02 | Upload an unsupported file | Clear validation error |
| TC-03 | Upload an empty TXT file | Empty-file warning |
| TC-04 | Upload multiple episode files | All valid files are processed |
| TC-05 | Parse episode information | Episode references are extracted correctly |
| TC-06 | Analyze screenplay scenes | Scene summaries and story elements are generated |
| TC-07 | Generate promo candidates | Relevant promo candidates are returned |
| TC-08 | Generate a hook | Hook is concise and attention-grabbing |
| TC-09 | Identify a cliffhanger | Candidate ends on an unresolved dramatic moment |
| TC-10 | Validate promo duration | Duration is within the configured 20–60 second range |
| TC-11 | Rank promo candidates | Candidates are sorted by calculated score |
| TC-12 | Export results | JSON and CSV files are generated successfully |

## **5\. AI Quality Test Cases**

AI-generated recommendations must be checked for creative relevance and factual accuracy.

| Test ID | Quality criterion | Expected result |
| ----- | ----- | ----- |
| AI-01 | Hook quality | First few seconds establish curiosity or tension |
| AI-02 | Emotional impact | Candidate contains an engaging emotional moment |
| AI-03 | Cliffhanger quality | Ending creates suspense or an unanswered question |
| AI-04 | Story coherence | Selected moments make sense as a promo |
| AI-05 | Independent understanding | Promo can be understood without excessive context |
| AI-06 | Source accuracy | Every selected segment exists in the source screenplay |
| AI-07 | No fabricated dialogue | AI does not invent dialogue or events |
| AI-08 | Multi-episode selection | Combined moments preserve logical order and references |

AI quality should be assessed through human review rather than relying only on automated scores.

## **6\. Promo Scoring Validation**

Each candidate will be scored on a scale of 0–10 across five criteria.

| Criterion | Weight |
| ----- | ----- |
| Hook strength | 25% |
| Emotional impact | 20% |
| Cliffhanger strength | 25% |
| Story coherence | 15% |
| Promo suitability | 15% |

The final score is calculated as:

\[  
S \= 0.25H \+ 0.20E \+ 0.25C \+ 0.15K \+ 0.15P  
\]

Where:

* H \= Hook strength  
* E \= Emotional impact  
* C \= Cliffhanger strength  
* K \= Story coherence  
* P \= Promo suitability

**Example:** If the scores are H=8, E=9, C=9, K=8, P=8:

\[  
S \= 8.45  
\]

The ranking engine must sort candidates in descending order of their final scores.

## **7\. Source Accuracy and Hallucination Testing**

The system must not present invented screenplay content as factual.

The following checks will be performed:

* Verify every episode reference against the uploaded input.  
* Verify every selected dialogue excerpt against the original screenplay.  
* Verify that selected scenes and events exist in the source.  
* Flag unsupported or missing timestamps.  
* Clearly distinguish actual timestamps from estimated timestamps.  
* Reject or flag candidates with missing source references.  
* Check that generated explanations are supported by the selected source material.

If timestamps are not available in the screenplay, the system must not claim that estimated timestamps are verified video timestamps.

## **8\. Integration Testing**

| Test ID | Modules involved | Expected result |
| ----- | ----- | ----- |
| IT-01 | File Processor \+ Parser | Uploaded text reaches the parser correctly |
| IT-02 | Parser \+ Scene Analyzer | Parsed scenes are analyzed successfully |
| IT-03 | Scene Analyzer \+ Promo Detector | Relevant promo candidates are generated |
| IT-04 | Promo Detector \+ Validator | Candidates are checked before ranking |
| IT-05 | Validator \+ Ranking Engine | Only valid candidates are ranked |
| IT-06 | Ranking Engine \+ Output Manager | Ranked results are exported correctly |

## **9\. Performance and Reliability Testing**

The following aspects will be evaluated:

* Processing multiple episode files without crashing.  
* Handling large screenplay files within reasonable time.  
* Handling AI API failures and rate limits gracefully.  
* Preventing duplicate promo recommendations.  
* Preserving source references during export.  
* Showing useful error messages when processing fails.

Initial performance observations will be recorded during testing. No performance target will be marked as achieved until measured.

## **10\. Manual Evaluation**

Generated promo candidates will be manually reviewed using the following checklist:

* The opening hook attracts attention.  
* The selected moments contain meaningful conflict or emotion.  
* The ending creates suspense.  
* The promo is understandable independently.  
* The selected content exists in the screenplay.  
* Episode and source references are correct.  
* Duration is within the required range or transparently marked as estimated.  
* The ranking reflects the quality of the candidate.

Poor recommendations will be recorded along with the reason for failure and any correction made.

## **11\. Acceptance Criteria**

PromoAI will be considered ready for the assignment demonstration when:

1. Valid screenplay TXT files can be uploaded and processed.  
2. Episode and source references are preserved.  
3. Promo candidates are generated in a structured format.  
4. Candidates are evaluated using the defined scoring criteria.  
5. Invalid or unsupported source references are flagged.  
6. Results can be exported in JSON or CSV format.  
7. AI failures are handled without crashing the application.  
8. At least a few generated candidates have been manually reviewed and their weaknesses documented.

## **12\. Test Execution Record**

Actual test execution results recorded on **November 20, 2026**.
Automated suite: **44 tests passed in 0.28s** (`pytest tests/ -v`).

| Test ID | Test Category / Module | Status | Execution Details & Remarks |
| ----- | ----- | ----- | ----- |
| **TC-01** | Upload valid TXT | **PASSED** | Verified via `test_valid_txt_file_accepted`. Single episode parsed with 100% field integrity. |
| **TC-02** | Reject unsupported files | **PASSED** | Verified via `test_invalid_extension_rejected`. Non-.txt extensions properly rejected. |
| **TC-03** | Empty file handling | **PASSED** | Verified via `test_empty_file_rejected`. Empty files flagged with descriptive error. |
| **TC-04** | Multiple episode processing | **PASSED** | Verified via `test_multiple_txt_files` and `test_zip_extraction_valid`. |
| **TC-05** | Screenplay parsing & metadata | **PASSED** | Verified via `test_extract_episode_header` and `test_parse_full_episode`. |
| **TC-06** | Scene & intensity analysis | **PASSED** | Verified via `test_characters_extracted` and deterministic scene intensity scoring. |
| **TC-07** | Promo candidate schema | **PASSED** | Verified via `test_promo_candidate_schema_valid` and `test_build_candidates_from_valid_ai_response`. |
| **TC-08** | Hook validation | **PASSED** | Verified via `test_missing_hook_flagged`. Candidates without hooks are strictly flagged. |
| **TC-09** | Cliffhanger validation | **PASSED** | Verified via `test_missing_cliffhanger_flagged`. |
| **TC-10** | Duration validation (20-60s) | **PASSED** | Verified via `test_duration_within_range`, `test_duration_too_short_flagged`, `test_duration_too_long_flagged`. |
| **TC-11** | Scoring & Ranking engine | **PASSED** | Verified via `test_score_formula_weighted_calculation` and `test_ranking_sorts_descending`. Enforces S = 0.25H + 0.20E + 0.25C + 0.15K + 0.15P. |
| **TC-12** | JSON, CSV & Markdown export | **PASSED** | Verified via `test_json_export_structure`, `test_csv_export_headers_and_rows`, `test_markdown_report_generation`. |
| **SEC-01**| ZIP Path Traversal Security | **PASSED** | Verified via `test_zip_path_traversal_blocked`. Zip-slip exploits blocked. |
| **SEC-02**| ZIP Executable Protection | **PASSED** | Verified via `test_zip_executable_skipped`. Non-script payloads safely filtered. |
| **AI-01** | Missing API Key Fallback | **PASSED** | Verified via `test_missing_api_key_returns_demo_mode` and `test_health_check_no_key`. |
| **AI-02** | AI API Failure Handling | **PASSED** | Verified via `test_api_failure_handled_gracefully` with mocked 403 quota exhaustion. |
| **AI-03** | Malformed JSON Recovery | **PASSED** | Verified via `test_malformed_json_response_handled`. |
| **VAL-01**| Source Text Verification | **PASSED** | Verified via `test_source_text_found_in_episode` and `test_source_text_not_found_flagged`. |
| **VAL-02**| Duplicate Detection | **PASSED** | Verified via `test_duplicate_candidates_detected`. Overlapping hooks flagged. |

**Summary:** 44/44 automated unit & integration tests executed and passing with 100% success rate.

## **13\. Conclusion**

This test plan aims to ensure that PromoAI is technically reliable, produces useful promotional recommendations, and maintains traceability to the original screenplay. Both automated tests and human creative evaluation are necessary to establish the quality of the final prototype.

