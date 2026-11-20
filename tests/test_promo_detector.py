"""
test_promo_detector.py — Unit Tests for Promo Detection and Pydantic Models

Tests schema validation, building candidates from AI responses, and ID generation.
"""

import pytest
from pydantic import ValidationError
from src.promo_detector import (
    PromoCandidate,
    PromoSegment,
    ScoreBreakdown,
    TimestampStatus,
    ReviewStatus,
    build_candidates_from_ai_response,
    generate_promo_id,
)


def test_promo_candidate_schema_valid(sample_promo_candidate):
    """A valid candidate passes Pydantic validation."""
    assert sample_promo_candidate.promo_id == "PROMO_001"
    assert sample_promo_candidate.scores.hook_strength == 9.0
    assert sample_promo_candidate.review_status == ReviewStatus.PENDING


def test_promo_candidate_missing_hook_raises():
    """Missing required field 'hook' must raise a ValidationError."""
    with pytest.raises(ValidationError):
        PromoCandidate(
            promo_id="PROMO_999",
            title="Broken Promo",
            segments=[],
            scores=ScoreBreakdown(
                hook_strength=5.0,
                emotional_impact=5.0,
                cliffhanger_strength=5.0,
                story_coherence=5.0,
                promo_suitability=5.0,
            ),
            # hook omitted!
        )


def test_build_candidates_from_valid_ai_response():
    """Correctly parses a valid AI response dictionary into PromoCandidate models."""
    ai_data = {
        "promos": [
            {
                "promo_id": "PROMO_001",
                "title": "Shock at Altar",
                "description": "Juliana is betrayed on her wedding day.",
                "hook": "Gerald refuses to marry Juliana at the altar.",
                "hook_strength_score": 9.5,
                "emotional_impact_score": 9.0,
                "cliffhanger_strength_score": 9.0,
                "story_coherence_score": 8.0,
                "promo_suitability_score": 8.5,
                "segments": [
                    {
                        "episode": "Episode 1",
                        "source_text": "I changed my mind.",
                        "scene_reference": "SCENE 01",
                        "start_time": "01:00.10",
                        "end_time": "01:01.80",
                        "timestamp_status": "available",
                        "segment_type": "cliffhanger",
                    }
                ],
                "estimated_duration_seconds": 30,
                "duration_estimation_method": "timestamps",
                "emotional_impact": "Devastating betrayal",
                "main_conflict": "Altar abandonment",
                "cliffhanger": "Gerald leaves with Clarissa",
                "why_it_works": "Extreme drama and emotion",
                "is_multi_episode": False,
                "ai_confidence": "high",
                "review_status": "pending",
            }
        ]
    }
    candidates = build_candidates_from_ai_response(ai_data, is_demo=False)
    assert len(candidates) == 1
    c = candidates[0]
    assert c.title == "Shock at Altar"
    assert c.scores.hook_strength == 9.5
    assert not c.is_demo


def test_build_candidates_handles_missing_fields():
    """Handles an AI response that is missing optional fields gracefully."""
    minimal_ai_data = {
        "promos": [
            {
                "promo_id": "PROMO_002",
                "title": "Minimal Promo",
                "hook": "Something happens",
                "cliffhanger": "Unresolved ending",
                "segments": [],
            }
        ]
    }
    candidates = build_candidates_from_ai_response(minimal_ai_data, is_demo=True)
    assert len(candidates) == 1
    c = candidates[0]
    assert c.is_demo is True
    assert c.scores.hook_strength >= 0.0


def test_build_candidates_empty_list():
    """Empty promos list returns an empty candidates list."""
    candidates = build_candidates_from_ai_response({"promos": []})
    assert len(candidates) == 0


def test_generate_promo_id():
    """Promo IDs are formatted consistently with zero-padding."""
    assert generate_promo_id(1) == "PROMO_001"
    assert generate_promo_id(10) == "PROMO_010"
    assert generate_promo_id(100) == "PROMO_100"
