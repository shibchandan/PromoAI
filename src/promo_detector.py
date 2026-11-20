"""
promo_detector.py — Promo Candidate Models and Builder

Pydantic models representing promo candidates, plus helpers to construct
them from AI JSON responses with graceful error handling.
"""

from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import Any


class TimestampStatus(str, Enum):
    AVAILABLE = "available"
    ESTIMATED = "estimated"
    UNAVAILABLE = "unavailable"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class PromoSegment(BaseModel):
    episode: str
    source_text: str
    scene_reference: str = ""
    start_time: str | None = None
    end_time: str | None = None
    timestamp_status: TimestampStatus = TimestampStatus.UNAVAILABLE
    segment_type: str = "body"  # hook, body, cliffhanger


class ScoreBreakdown(BaseModel):
    hook_strength: float = Field(ge=0, le=10)
    emotional_impact: float = Field(ge=0, le=10)
    cliffhanger_strength: float = Field(ge=0, le=10)
    story_coherence: float = Field(ge=0, le=10)
    promo_suitability: float = Field(ge=0, le=10)


class PromoCandidate(BaseModel):
    promo_id: str
    title: str
    description: str = ""
    hook: str
    segments: list[PromoSegment]
    estimated_duration_seconds: int | None = None
    duration_estimation_method: str = ""
    emotional_impact: str = ""
    main_conflict: str = ""
    cliffhanger: str = ""
    why_it_works: str = ""
    is_multi_episode: bool = False
    scores: ScoreBreakdown
    final_score: float = 0.0  # computed by ranking engine, NOT by AI
    ai_confidence: str = "medium"
    review_status: ReviewStatus = ReviewStatus.PENDING
    reviewer_comment: str = ""
    is_demo: bool = False
    validation_flags: list[str] = Field(default_factory=list)


def generate_promo_id(index: int) -> str:
    """Generate a formatted promo ID like PROMO_001."""
    return f"PROMO_{index:03d}"


def _safe_float(value: Any, default: float = 5.0, min_val: float = 0.0, max_val: float = 10.0) -> float:
    """Coerce a value to float, clamped within [min_val, max_val]."""
    try:
        return max(min_val, min(max_val, float(value)))
    except (TypeError, ValueError):
        return default


def _safe_str(value: Any, default: str = "") -> str:
    """Coerce a value to str safely."""
    if value is None:
        return default
    return str(value)


def _safe_int(value: Any, default: int | None = None) -> int | None:
    """Coerce a value to int safely, returning default on failure."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_segment(raw: Any, episode_fallback: str = "") -> PromoSegment | None:
    """Parse a single segment dict into a PromoSegment, returning None on hard failure."""
    if not isinstance(raw, dict):
        return None

    episode = _safe_str(raw.get("episode") or raw.get("episode_label"), episode_fallback)
    source_text = _safe_str(raw.get("source_text") or raw.get("text"), "")
    scene_ref = _safe_str(raw.get("scene_reference") or raw.get("scene_ref"), "")
    start_time = raw.get("start_time") or raw.get("start")
    end_time = raw.get("end_time") or raw.get("end")
    segment_type = _safe_str(raw.get("segment_type") or raw.get("type"), "body")

    # Determine timestamp status
    if start_time and end_time:
        ts_status = TimestampStatus.AVAILABLE
    elif start_time or end_time:
        ts_status = TimestampStatus.ESTIMATED
    else:
        ts_status = TimestampStatus.UNAVAILABLE

    return PromoSegment(
        episode=episode,
        source_text=source_text,
        scene_reference=scene_ref,
        start_time=_safe_str(start_time) if start_time else None,
        end_time=_safe_str(end_time) if end_time else None,
        timestamp_status=ts_status,
        segment_type=segment_type,
    )


def _parse_scores(raw: Any) -> ScoreBreakdown:
    """Parse a scores dict into ScoreBreakdown, using defaults for missing/bad values."""
    if not isinstance(raw, dict):
        raw = {}

    return ScoreBreakdown(
        hook_strength=_safe_float(raw.get("hook_strength", 5.0)),
        emotional_impact=_safe_float(raw.get("emotional_impact", 5.0)),
        cliffhanger_strength=_safe_float(raw.get("cliffhanger_strength", 5.0)),
        story_coherence=_safe_float(raw.get("story_coherence", 5.0)),
        promo_suitability=_safe_float(raw.get("promo_suitability", 5.0)),
    )


def _parse_single_candidate(
    raw: dict,
    index: int,
    is_demo: bool = False,
) -> PromoCandidate | None:
    """
    Parse one candidate dict from AI output.
    Returns None if the dict is so malformed that no PromoCandidate can be built.
    """
    if not isinstance(raw, dict):
        return None

    promo_id = _safe_str(raw.get("promo_id"), generate_promo_id(index))
    if not promo_id:
        promo_id = generate_promo_id(index)

    title = _safe_str(raw.get("title"), f"Untitled Promo {index}")
    hook = _safe_str(raw.get("hook"), "")
    cliffhanger = _safe_str(raw.get("cliffhanger"), "")

    # Parse segments — accept list of dicts or a single dict
    raw_segments = raw.get("segments") or raw.get("segment_list") or []
    if isinstance(raw_segments, dict):
        raw_segments = [raw_segments]
    if not isinstance(raw_segments, list):
        raw_segments = []

    # Try to get a fallback episode label from top-level key
    ep_fallback = _safe_str(raw.get("episode") or raw.get("episode_label"), "")

    segments: list[PromoSegment] = []
    for seg_raw in raw_segments:
        seg = _parse_segment(seg_raw, ep_fallback)
        if seg:
            segments.append(seg)

    # Scores
    scores_raw = raw.get("scores") or raw.get("score_breakdown") or {}
    if not isinstance(scores_raw, dict):
        scores_raw = {}
    
    # Also accept flat score keys at the top level (including _score suffixes from AI prompts)
    scores_dict = {
        "hook_strength": scores_raw.get("hook_strength") or raw.get("hook_strength_score") or raw.get("hook_strength"),
        "emotional_impact": scores_raw.get("emotional_impact") or raw.get("emotional_impact_score") or raw.get("emotional_impact"),
        "cliffhanger_strength": scores_raw.get("cliffhanger_strength") or raw.get("cliffhanger_strength_score") or raw.get("cliffhanger_strength"),
        "story_coherence": scores_raw.get("story_coherence") or raw.get("story_coherence_score") or raw.get("story_coherence"),
        "promo_suitability": scores_raw.get("promo_suitability") or raw.get("promo_suitability_score") or raw.get("promo_suitability"),
    }
    scores = _parse_scores(scores_dict)

    # Duration
    duration = _safe_int(
        raw.get("estimated_duration_seconds")
        or raw.get("duration_seconds")
        or raw.get("duration")
    )

    # Multi-episode flag
    is_multi = bool(raw.get("is_multi_episode", False))
    if not is_multi and len({seg.episode for seg in segments}) > 1:
        is_multi = True

    # AI confidence
    confidence = _safe_str(raw.get("ai_confidence"), "medium").lower()
    if confidence not in {"low", "medium", "high"}:
        confidence = "medium"

    return PromoCandidate(
        promo_id=promo_id,
        title=title,
        description=_safe_str(raw.get("description"), ""),
        hook=hook,
        segments=segments,
        estimated_duration_seconds=duration,
        duration_estimation_method=_safe_str(raw.get("duration_estimation_method"), ""),
        emotional_impact=_safe_str(raw.get("emotional_impact_text") or raw.get("emotional_impact_summary"), ""),
        main_conflict=_safe_str(raw.get("main_conflict"), ""),
        cliffhanger=cliffhanger,
        why_it_works=_safe_str(raw.get("why_it_works"), ""),
        is_multi_episode=is_multi,
        scores=scores,
        final_score=0.0,  # Always recalculated by ranking engine
        ai_confidence=confidence,
        review_status=ReviewStatus.PENDING,
        reviewer_comment="",
        is_demo=is_demo,
        validation_flags=[],
    )


def build_candidates_from_ai_response(
    ai_data: dict,
    is_demo: bool = False,
) -> list[PromoCandidate]:
    """
    Parse the AI JSON response into a list of PromoCandidate objects.

    Expected top-level structure:
      { "promo_candidates": [ {...}, {...}, ... ] }

    Also handles:
      - Response wrapped in another key (e.g. "candidates", "promos")
      - A bare list at the top level
      - Partial / malformed entries (skipped with a warning, not crashing)

    is_demo: propagated to every candidate's is_demo field.
    """
    if not isinstance(ai_data, dict):
        return []

    # Locate the list of candidates under various possible keys
    raw_list: list = []
    for key in ("promo_candidates", "candidates", "promos", "results"):
        if key in ai_data and isinstance(ai_data[key], list):
            raw_list = ai_data[key]
            break

    # Fallback: if the dict itself looks like a single candidate
    if not raw_list and "hook" in ai_data:
        raw_list = [ai_data]

    candidates: list[PromoCandidate] = []
    for idx, raw_item in enumerate(raw_list, start=1):
        try:
            candidate = _parse_single_candidate(raw_item, idx, is_demo=is_demo)
            if candidate is not None:
                candidates.append(candidate)
        except Exception as exc:
            # Log but do not crash — keep whatever we could build
            import logging
            logging.getLogger(__name__).warning(
                "Skipping malformed candidate #%d: %s", idx, exc
            )

    return candidates
