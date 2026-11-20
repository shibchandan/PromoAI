"""
test_validator.py — Unit Tests for Promo Candidate Validation and Quality Control

Tests source text verification, duration constraints, required fields, and duplicate detection.
"""

import pytest
from src.promo_detector import PromoCandidate, PromoSegment, ScoreBreakdown
from src.validator import (
    validate_source_text_exists,
    validate_duration,
    validate_required_fields,
    validate_candidate,
    validate_all_candidates,
    find_duplicate_candidates,
)


def test_source_text_found_in_episode(sample_promo_candidate, sample_parsed_episode):
    """Source text that actually appears in the episode produces zero validation flags."""
    flags = validate_source_text_exists(sample_promo_candidate, [sample_parsed_episode])
    assert len(flags) == 0


def test_source_text_not_found_flagged(sample_promo_candidate, sample_parsed_episode):
    """Invented text that does NOT exist in the screenplay must be flagged."""
    c = sample_promo_candidate.model_copy(deep=True)
    c.segments[0].source_text = "This dialogue never existed in the screenplay anywhere!"
    flags = validate_source_text_exists(c, [sample_parsed_episode])
    assert len(flags) > 0
    assert "not verified" in flags[0].lower() or "not found" in flags[0].lower()


def test_duration_within_range(sample_promo_candidate):
    """Duration between 20-60s has no flags."""
    c = sample_promo_candidate.model_copy()
    c.estimated_duration_seconds = 45
    flags = validate_duration(c)
    assert len(flags) == 0


def test_duration_too_short_flagged(sample_promo_candidate):
    """Duration below 20s must be flagged."""
    c = sample_promo_candidate.model_copy()
    c.estimated_duration_seconds = 15
    flags = validate_duration(c)
    assert len(flags) > 0
    assert "below minimum" in flags[0].lower() or "too short" in flags[0].lower()


def test_duration_too_long_flagged(sample_promo_candidate):
    """Duration above 60s must be flagged."""
    c = sample_promo_candidate.model_copy()
    c.estimated_duration_seconds = 75
    flags = validate_duration(c)
    assert len(flags) > 0
    assert "exceeds maximum" in flags[0].lower() or "too long" in flags[0].lower()


def test_duration_none_flagged(sample_promo_candidate):
    """None duration must be flagged."""
    c = sample_promo_candidate.model_copy()
    c.estimated_duration_seconds = None
    flags = validate_duration(c)
    assert len(flags) > 0


def test_missing_hook_flagged(sample_promo_candidate):
    """Empty hook must be flagged."""
    c = sample_promo_candidate.model_copy()
    c.hook = ""
    flags = validate_required_fields(c)
    assert any("hook" in f.lower() for f in flags)


def test_missing_cliffhanger_flagged(sample_promo_candidate):
    """Empty cliffhanger must be flagged."""
    c = sample_promo_candidate.model_copy()
    c.cliffhanger = ""
    flags = validate_required_fields(c)
    assert any("cliffhanger" in f.lower() for f in flags)


def test_duplicate_candidates_detected(sample_promo_candidate):
    """Two candidates with highly similar hooks should be flagged as duplicates."""
    c1 = sample_promo_candidate.model_copy()
    c1.hook = "Juliana pauses at cathedral door, smiles, then sees her sister holding Gerald's hand."
    c2 = sample_promo_candidate.model_copy()
    c2.hook = "Juliana pauses at cathedral door and smiles, then sees her sister holding Gerald's hand."
    duplicates = find_duplicate_candidates([c1, c2])
    assert len(duplicates) == 1
    assert duplicates[0] == (0, 1)
