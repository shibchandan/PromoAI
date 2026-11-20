"""
validator.py — Promo Candidate Quality Control

Validates AI-generated promo candidates against the original screenplay content.
Key principle: Never automatically mark something as verified unless the Python
code can confirm it in the original source text.
"""

from src.promo_detector import PromoCandidate
from src.screenplay_parser import Episode


def validate_source_text_exists(candidate: PromoCandidate, episodes: list[Episode]) -> list[str]:
    """
    For each segment, check that source_text actually appears in the original screenplay.
    Returns list of validation failure messages.
    """
    flags = []
    episode_map = {ep.episode_label: ep.raw_content for ep in episodes}

    for i, segment in enumerate(candidate.segments):
        ep_content = episode_map.get(segment.episode, "")
        if not ep_content:
            flags.append(f"Segment {i+1}: Episode '{segment.episode}' not found in loaded episodes")
        elif segment.source_text and len(segment.source_text) > 10:
            # Check if at least a substantial substring appears in the content
            search_text = segment.source_text.strip().strip('"')
            if search_text[:50] not in ep_content:
                flags.append(f"Segment {i+1}: Source text not verified in '{segment.episode}'")
    return flags


def validate_duration(candidate: PromoCandidate) -> list[str]:
    """Check duration is within 20-60 second range."""
    flags = []
    duration = candidate.estimated_duration_seconds
    if duration is None:
        flags.append("Duration not estimated — cannot verify promo length")
    elif duration < 20:
        flags.append(f"Duration {duration}s is below minimum 20 seconds")
    elif duration > 60:
        flags.append(f"Duration {duration}s exceeds maximum 60 seconds")
    return flags


def validate_required_fields(candidate: PromoCandidate) -> list[str]:
    """Check all required fields are present and non-empty."""
    flags = []
    if not candidate.hook:
        flags.append("Missing: hook")
    if not candidate.cliffhanger:
        flags.append("Missing: cliffhanger")
    if not candidate.segments:
        flags.append("Missing: no segments defined")
    if not candidate.title:
        flags.append("Missing: title")
    return flags


def validate_candidate(candidate: PromoCandidate, episodes: list[Episode]) -> PromoCandidate:
    """Run all validations and attach flags to candidate."""
    flags = []
    flags.extend(validate_required_fields(candidate))
    flags.extend(validate_duration(candidate))
    flags.extend(validate_source_text_exists(candidate, episodes))
    candidate.validation_flags = flags
    return candidate


def validate_all_candidates(candidates: list[PromoCandidate], episodes: list[Episode]) -> list[PromoCandidate]:
    """Validate all candidates and return with flags populated."""
    return [validate_candidate(c, episodes) for c in candidates]


def find_duplicate_candidates(candidates: list[PromoCandidate]) -> list[tuple[int, int]]:
    """
    Find pairs of candidates with very similar hooks/cliffhangers.
    Returns list of (index_a, index_b) pairs.
    Simple similarity: check if hooks share > 50% of words.
    """
    duplicates = []
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            hook_i = set(candidates[i].hook.lower().split())
            hook_j = set(candidates[j].hook.lower().split())
            if len(hook_i) > 0 and len(hook_j) > 0:
                overlap = len(hook_i & hook_j) / min(len(hook_i), len(hook_j))
                if overlap > 0.6:
                    duplicates.append((i, j))
    return duplicates
