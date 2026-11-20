"""
ranking_engine.py — Deterministic Promo Ranking

The scoring formula from PRD:
S = 0.25H + 0.20E + 0.25C + 0.15K + 0.15P

Where:
- H = Hook strength (0-10)
- E = Emotional impact (0-10)
- C = Cliffhanger strength (0-10)
- K = Story coherence (0-10)
- P = Promo suitability (0-10)

IMPORTANT: The AI provides raw scores 0-10 for each criterion.
Python calculates the final weighted score. AI never decides ranking.
"""

from src.promo_detector import PromoCandidate, ScoreBreakdown
from src import config


def calculate_final_score(scores: ScoreBreakdown) -> float:
    """
    Apply the PRD scoring formula deterministically.
    This is ALWAYS computed in Python - never trusted from AI output.
    """
    score = (
        config.SCORING_WEIGHTS["hook_strength"] * scores.hook_strength
        + config.SCORING_WEIGHTS["emotional_impact"] * scores.emotional_impact
        + config.SCORING_WEIGHTS["cliffhanger_strength"] * scores.cliffhanger_strength
        + config.SCORING_WEIGHTS["story_coherence"] * scores.story_coherence
        + config.SCORING_WEIGHTS["promo_suitability"] * scores.promo_suitability
    )
    return round(score, 2)


def rank_candidates(candidates: list[PromoCandidate]) -> list[PromoCandidate]:
    """
    Score and sort all candidates by final_score descending.
    Re-calculates every score from scratch to prevent AI score manipulation.
    """
    for candidate in candidates:
        # Always recalculate — never trust AI-provided final score
        candidate.final_score = calculate_final_score(candidate.scores)

    return sorted(candidates, key=lambda c: c.final_score, reverse=True)


def add_rank_labels(candidates: list[PromoCandidate]) -> list[PromoCandidate]:
    """Add rank position to each candidate after sorting."""
    # Return with rank embedded in promo_id prefix if desired
    return candidates
