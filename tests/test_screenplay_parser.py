"""
test_screenplay_parser.py — Unit Tests for Screenplay Parsing Module

Tests timestamp parsing, scene extraction, dialogue recognition, and character mapping.
"""

import pytest
from src.screenplay_parser import (
    parse_timestamp,
    extract_episode_header,
    parse_scene_block,
    parse_episode,
    Episode,
    Scene,
    DialogueLine,
    ActionLine,
    TimestampStatus,
)
from src.file_processor import EpisodeFile


def test_parse_timestamp_valid():
    """Valid MM:SS.cc timestamps are converted to total seconds."""
    assert parse_timestamp("00:00.00") == 0.0
    assert parse_timestamp("01:30.00") == 90.0
    assert parse_timestamp("02:18.50") == 138.5
    assert parse_timestamp("00:11.30") == 11.3


def test_parse_timestamp_edge_cases():
    """Invalid or empty timestamps should return 0.0 without crashing."""
    assert parse_timestamp("") == 0.0
    assert parse_timestamp(None) == 0.0
    assert parse_timestamp("invalid") == 0.0


def test_extract_episode_header(sample_screenplay_text):
    """Header fields (number, logline, continuity) are extracted correctly."""
    label, logline, continuity = extract_episode_header(sample_screenplay_text)
    assert label == "Episode 1"
    assert "Juliana" in logline
    assert "continuity" in continuity.lower() or "first" in continuity.lower()


def test_parse_full_episode(sample_screenplay_text):
    """A complete screenplay is parsed into an Episode model with scenes."""
    ep_file = EpisodeFile(
        filename="test.txt",
        episode_label="Episode 1",
        content=sample_screenplay_text,
        file_size_bytes=len(sample_screenplay_text),
        is_valid=True,
    )
    episode = parse_episode(ep_file)
    assert isinstance(episode, Episode)
    assert episode.episode_label == "Episode 1"
    assert len(episode.scenes) == 2
    assert episode.total_duration_seconds > 0

    scene1 = episode.scenes[0]
    assert scene1.scene_number == "01"
    assert "CATHEDRAL" in scene1.heading
    assert len(scene1.dialogues) > 0
    assert len(scene1.actions) > 0


def test_characters_extracted(sample_screenplay_text):
    """Character names are extracted and normalized."""
    ep_file = EpisodeFile(
        filename="test.txt",
        episode_label="Episode 1",
        content=sample_screenplay_text,
        file_size_bytes=len(sample_screenplay_text),
        is_valid=True,
    )
    episode = parse_episode(ep_file)
    characters = episode.all_characters
    assert any("MATRIARCH" in c for c in characters)
    assert any("JULIANA" in c for c in characters)
    # CAMERA and ACTION should NOT be characters
    assert "CAMERA" not in characters
    assert "ACTION" not in characters
    assert "SOUND FX" not in characters


def test_dialogue_line_fields(sample_screenplay_text):
    """Dialogue lines retain character, emotion, text, and timestamps."""
    ep_file = EpisodeFile(
        filename="test.txt",
        episode_label="Episode 1",
        content=sample_screenplay_text,
        file_size_bytes=len(sample_screenplay_text),
        is_valid=True,
    )
    episode = parse_episode(ep_file)
    first_dlg = episode.scenes[0].dialogues[0]
    assert "MATRIARCH" in first_dlg.character
    assert "Cold" in first_dlg.emotion or "Commanding" in first_dlg.emotion
    assert "turn around" in first_dlg.text
    assert first_dlg.start_seconds > 0
    assert first_dlg.end_seconds > first_dlg.start_seconds
