"""
scene_analyzer.py — Rule-Based Scene Analysis

This module uses deterministic Python code (no AI) to analyze screenplay content.
AI is used elsewhere for semantic understanding.
Here we extract facts: who is present, word counts, intensity markers, etc.
"""

from dataclasses import dataclass, field
from src.screenplay_parser import Episode, Scene, DialogueLine

EMOTION_KEYWORDS = {
    "high_intensity": ["betrayal", "fury", "rage", "shock", "devastated", "outrage", "crushed", "horror"],
    "romantic": ["love", "tender", "embrace", "kiss", "adore", "cherish"],
    "suspense": ["secret", "whisper", "shadow", "threat", "warning", "danger"],
    "confrontation": ["accuse", "challenge", "defy", "confront", "demand", "refuse"],
}

DRAMATIC_EMOTION_TAGS = [
    "Betrayed", "Outraged", "Devastated", "Shocked", "Furious",
    "Piercing", "Accusing", "Desperate", "Heartbroken",
]


@dataclass
class SceneFeatures:
    scene_number: str
    episode_label: str
    character_count: int
    dialogue_count: int
    total_words: int
    has_confrontation: bool
    has_emotional_dialogue: bool
    has_cliffhanger_indicator: bool
    dominant_emotion: str
    intensity_score: float  # 0-10, computed deterministically
    unique_characters: list[str]
    longest_speech_words: int
    has_sound_fx: bool


@dataclass
class EpisodeAnalysis:
    episode_label: str
    episode_number: int
    total_scenes: int
    total_duration_seconds: float
    all_characters: list[str]
    high_intensity_scenes: list[str]  # scene numbers
    scene_features: list[SceneFeatures]
    estimated_word_count: int
    has_clear_hook: bool  # first scene has confrontation or strong emotion
    has_cliffhanger: bool  # last scene has unresolved moment


def _count_keyword_hits(text: str, keywords: list[str]) -> int:
    """Count how many keywords appear in the text (case-insensitive)."""
    lower = text.lower()
    return sum(1 for kw in keywords if kw in lower)


def _all_dialogue_text(scene: Scene) -> str:
    """Concatenate all dialogue lines in a scene into one string."""
    parts = []
    for line in scene.dialogue_lines:
        if line.text:
            parts.append(line.text)
    return " ".join(parts)


def compute_scene_intensity(scene: Scene) -> float:
    """
    Compute a 0-10 intensity score deterministically.

    Components:
      - Dramatic emotion tags on character lines (up to 4 pts)
      - Confrontation/high-intensity keywords in dialogue (up to 3 pts)
      - Ratio of dramatic lines to total lines (up to 2 pts)
      - Presence of SOUND FX (1 pt)
    """
    score = 0.0
    total_lines = len(scene.dialogue_lines)
    if total_lines == 0:
        return 0.0

    # 1. Dramatic emotion tags
    dramatic_tag_count = sum(
        1 for line in scene.dialogue_lines
        if any(tag.lower() in (line.emotion or "").lower() for tag in DRAMATIC_EMOTION_TAGS)
    )
    tag_score = min(4.0, dramatic_tag_count * 1.0)
    score += tag_score

    # 2. High-intensity + confrontation keywords in dialogue
    all_text = _all_dialogue_text(scene)
    kw_hits = _count_keyword_hits(all_text, EMOTION_KEYWORDS["high_intensity"])
    kw_hits += _count_keyword_hits(all_text, EMOTION_KEYWORDS["confrontation"])
    kw_score = min(3.0, kw_hits * 0.5)
    score += kw_score

    # 3. Ratio of dramatic lines to total lines
    dramatic_lines = sum(
        1 for line in scene.dialogue_lines
        if any(tag.lower() in (line.emotion or "").lower() for tag in DRAMATIC_EMOTION_TAGS)
        or _count_keyword_hits(line.text or "", EMOTION_KEYWORDS["high_intensity"]) > 0
    )
    ratio = dramatic_lines / total_lines
    score += ratio * 2.0  # up to 2 pts

    # 4. Sound FX present (check both actions and dialogue)
    has_sfx = any(
        (getattr(line, "character", "") or "").upper() == "SOUND FX"
        for line in scene.dialogue_lines
    ) or any(
        (getattr(act, "action_type", "") or "").upper() == "SOUND FX"
        for act in getattr(scene, "actions", [])
    )
    if has_sfx:
        score += 1.0

    return round(min(10.0, score), 2)


def analyze_scene(scene: Scene, episode_label: str) -> SceneFeatures:
    """Extract deterministic features from a single scene."""
    unique_chars: list[str] = []
    seen_chars: set[str] = set()
    total_words = 0
    longest_speech = 0
    has_sound_fx = False

    for line in scene.dialogue_lines:
        char = (line.character or "").strip()
        if char and char not in {"ACTION", "CAMERA", "SOUND FX", ""}:
            if char not in seen_chars:
                seen_chars.add(char)
                unique_chars.append(char)
        if char.upper() == "SOUND FX":
            has_sound_fx = True

        words = len((line.text or "").split())
        total_words += words
        if words > longest_speech:
            longest_speech = words

    all_text = _all_dialogue_text(scene)

    has_confrontation = _count_keyword_hits(all_text, EMOTION_KEYWORDS["confrontation"]) > 0
    has_emotional = any(
        any(tag.lower() in (line.emotion or "").lower() for tag in DRAMATIC_EMOTION_TAGS)
        for line in scene.dialogue_lines
    )

    # Cliffhanger indicators: suspense keywords in the last 20% of lines
    tail_start = max(0, int(len(scene.dialogue_lines) * 0.8))
    tail_text = " ".join(
        line.text or "" for line in scene.dialogue_lines[tail_start:]
    )
    has_cliffhanger = _count_keyword_hits(tail_text, EMOTION_KEYWORDS["suspense"]) > 0

    # Dominant emotion: whichever category has the most keyword hits
    category_scores = {
        cat: _count_keyword_hits(all_text, kws)
        for cat, kws in EMOTION_KEYWORDS.items()
    }
    dominant = max(category_scores, key=lambda k: category_scores[k])
    if category_scores[dominant] == 0:
        dominant = "neutral"

    intensity = compute_scene_intensity(scene)

    return SceneFeatures(
        scene_number=scene.scene_number,
        episode_label=episode_label,
        character_count=len(unique_chars),
        dialogue_count=len(scene.dialogue_lines),
        total_words=total_words,
        has_confrontation=has_confrontation,
        has_emotional_dialogue=has_emotional,
        has_cliffhanger_indicator=has_cliffhanger,
        dominant_emotion=dominant,
        intensity_score=intensity,
        unique_characters=unique_chars,
        longest_speech_words=longest_speech,
        has_sound_fx=has_sound_fx,
    )


def analyze_episode(episode: Episode) -> EpisodeAnalysis:
    """Analyze all scenes in an episode and produce a summary."""
    scene_features: list[SceneFeatures] = []
    all_chars_set: set[str] = set()
    total_words = 0
    total_duration = 0.0

    for scene in episode.scenes:
        sf = analyze_scene(scene, episode.episode_label)
        scene_features.append(sf)
        all_chars_set.update(sf.unique_characters)
        total_words += sf.total_words

        # Duration from scene timestamps if available
        try:
            if scene.start_time and scene.end_time:
                def _ts_to_secs(ts: str) -> float:
                    parts = ts.replace(".", ":").split(":")
                    if len(parts) == 3:
                        return int(parts[0]) * 60 + int(parts[1]) + int(parts[2]) / 100
                    elif len(parts) == 2:
                        return int(parts[0]) * 60 + float(parts[1])
                    return 0.0
                total_duration += _ts_to_secs(scene.end_time) - _ts_to_secs(scene.start_time)
        except Exception:
            pass

    high_intensity = [sf.scene_number for sf in scene_features if sf.intensity_score >= 6.0]

    has_hook = bool(
        scene_features and (
            scene_features[0].has_confrontation or scene_features[0].has_emotional_dialogue
        )
    )
    has_cliffhanger = bool(
        scene_features and scene_features[-1].has_cliffhanger_indicator
    )

    return EpisodeAnalysis(
        episode_label=episode.episode_label,
        episode_number=episode.episode_number,
        total_scenes=len(episode.scenes),
        total_duration_seconds=round(total_duration, 2),
        all_characters=sorted(all_chars_set),
        high_intensity_scenes=high_intensity,
        scene_features=scene_features,
        estimated_word_count=total_words,
        has_clear_hook=has_hook,
        has_cliffhanger=has_cliffhanger,
    )


def analyze_all_episodes(episodes: list[Episode]) -> list[EpisodeAnalysis]:
    """Analyze every episode and return the full list of EpisodeAnalysis objects."""
    return [analyze_episode(ep) for ep in episodes]
