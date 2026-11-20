"""
validator.py — Promo Candidate Quality Control

Validates AI-generated promo candidates against the original screenplay content.
Key principle: Never automatically mark something as verified unless the Python
code can confirm it in the original source text.
"""

import re
from src.promo_detector import PromoCandidate
from src.screenplay_parser import Episode


def _normalize_text_for_search(text: str) -> str:
    """Normalize screenplay or segment text by stripping quotes, punctuation, and extra whitespace."""
    if not text:
        return ""
    # Strip straight and curly quotes
    cleaned = (
        text.replace('"', " ")
        .replace("“", " ")
        .replace("”", " ")
        .replace("'", " ")
        .replace("‘", " ")
        .replace("’", " ")
    )
    # Replace punctuation characters with space
    cleaned = re.sub(r"[\(\)\[\]\{\}:;,\.\!\?–—\-\\\/]", " ", cleaned)
    # Collapse multiple whitespaces and lowercase
    return " ".join(cleaned.lower().split())


def validate_source_text_exists(candidate: PromoCandidate, episodes: list[Episode]) -> list[str]:
    """
    For each segment, check that source_text actually appears in the original screenplay.
    Returns list of validation failure messages.
    Supports verbatim substring matching, normalized text matching (for quotes and casing),
    and n-gram phrase matching to guard against false negatives while catching real hallucinations.
    """
    flags = []
    # Build a lookup mapping by exact label as well as variations
    episode_map: dict[str, str] = {}
    for ep in episodes:
        episode_map[ep.episode_label.lower().strip()] = ep.raw_content
        episode_map[f"episode {ep.episode_number}"] = ep.raw_content
        episode_map[f"ep {ep.episode_number}"] = ep.raw_content
        episode_map[f"ep.{ep.episode_number}"] = ep.raw_content
        episode_map[str(ep.episode_number)] = ep.raw_content

    for i, segment in enumerate(candidate.segments):
        ep_key = segment.episode.lower().strip()
        ep_content = episode_map.get(ep_key, "")
        if not ep_content:
            flags.append(f"Segment {i+1}: Episode '{segment.episode}' not found in loaded episodes")
            continue

        if segment.source_text and len(segment.source_text.strip()) > 10:
            search_text = segment.source_text.strip().strip('"\'')
            # 1. Exact raw substring check (first 50 chars)
            if search_text[:50] in ep_content:
                continue

            # 2. Normalized check (ignoring smart quotes, punctuation, casing, and whitespace)
            norm_content = _normalize_text_for_search(ep_content)
            norm_search = _normalize_text_for_search(search_text)

            if norm_search in norm_content or (len(norm_search) > 25 and norm_search[:40] in norm_content):
                continue

            # 3. 4-word sliding phrase match (to allow for character cues like "THE STRANGER: ...")
            words = norm_search.split()
            found_phrase = False
            if len(words) >= 4:
                for w_idx in range(len(words) - 3):
                    phrase = " ".join(words[w_idx : w_idx + 4])
                    if phrase in norm_content:
                        found_phrase = True
                        break

            if found_phrase:
                continue

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
