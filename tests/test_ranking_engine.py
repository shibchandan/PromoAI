"""
test_ranking_engine.py — Unit Tests for Deterministic Promo Ranking

Tests exact scoring formula: S = 0.25H + 0.20E + 0.25C + 0.15K + 0.15P
and verifies that rankings are strictly descending and not manipulated by AI.
"""

import pytest
from src.promo_detector import PromoCandidate, PromoSegment, ScoreBreakdown
from src.ranking_engine import calculate_final_score, rank_candidates


def test_score_formula_all_tens():
    """All 10s should result in a perfect 10.0 final score."""
    scores = ScoreBreakdown(
        hook_strength=10.0,
        emotional_impact=10.0,
        cliffhanger_strength=10.0,
        story_coherence=10.0,
        promo_suitability=10.0,
    )
    assert calculate_final_score(scores) == 10.0


def test_score_formula_all_zeros():
    """All 0s should result in 0.0."""
    scores = ScoreBreakdown(
        hook_strength=0.0,
        emotional_impact=0.0,
        cliffhanger_strength=0.0,
        story_coherence=0.0,
        promo_suitability=0.0,
    )
    assert calculate_final_score(scores) == 0.0


def test_score_formula_weighted_calculation():
    """
    S = 0.25*8 + 0.20*6 + 0.25*9 + 0.15*7 + 0.15*8
    S = 2.00 + 1.20 + 2.25 + 1.05 + 1.20 = 7.70
    """
    scores = ScoreBreakdown(
        hook_strength=8.0,
        emotional_impact=6.0,
        cliffhanger_strength=9.0,
        story_coherence=7.0,
        promo_suitability=8.0,
    )
    assert calculate_final_score(scores) == 7.70


def test_ranking_sorts_descending(sample_promo_candidate):
    """Rank candidates must sort in strictly descending order of final_score."""
    c1 = sample_promo_candidate.model_copy()
    c1.promo_id = "PROMO_001"
    c1.scores = ScoreBreakdown(
        hook_strength=5.0, emotional_impact=5.0,
        cliffhanger_strength=5.0, story_coherence=5.0, promo_suitability=5.0
    )  # final_score = 5.0

    c2 = sample_promo_candidate.model_copy()
    c2.promo_id = "PROMO_002"
    c2.scores = ScoreBreakdown(
        hook_strength=9.0, emotional_impact=9.0,
        cliffhanger_strength=9.0, story_coherence=9.0, promo_suitability=9.0
    )  # final_score = 9.0

    c3 = sample_promo_candidate.model_copy()
    c3.promo_id = "PROMO_003"
    c3.scores = ScoreBreakdown(
        hook_strength=7.0, emotional_impact=7.0,
        cliffhanger_strength=7.0, story_coherence=7.0, promo_suitability=7.0
    )  # final_score = 7.0

    ranked = rank_candidates([c1, c2, c3])
    assert ranked[0].promo_id == "PROMO_002"
    assert ranked[1].promo_id == "PROMO_003"
    assert ranked[2].promo_id == "PROMO_001"
    assert ranked[0].final_score >= ranked[1].final_score >= ranked[2].final_score


def test_ranking_recalculates_ignoring_ai_score(sample_promo_candidate):
    """If AI provides an exaggerated final_score (e.g. 99.9), Python recalculates it."""
    c = sample_promo_candidate.model_copy()
    c.final_score = 99.9  # Fake high score from AI
    c.scores = ScoreBreakdown(
        hook_strength=5.0, emotional_impact=5.0,
        cliffhanger_strength=5.0, story_coherence=5.0, promo_suitability=5.0
    )
    ranked = rank_candidates([c])
    assert ranked[0].final_score == 5.0  # Must be overwritten by Python calculation
