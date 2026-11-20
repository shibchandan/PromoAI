"""
test_output_manager.py — Unit Tests for Export and Output Serialization

Tests JSON export schema conformity, CSV row creation, and Markdown generation.
"""

import json
import pytest
from src.output_manager import (
    build_json_output,
    export_json,
    export_csv,
    export_markdown_report,
)
from src.promo_detector import PromoCandidate


def test_json_export_structure(sample_promo_candidate):
    """JSON output conforms to the required specification schema."""
    episodes_info = [{"episode_label": "Episode 1", "filename": "ep1.txt"}]
    json_str = export_json([sample_promo_candidate], episodes_info, is_demo=False)
    
    # Must be valid parseable JSON
    data = json.loads(json_str)
    assert data["project"] == "PromoAI"
    assert data["version"] == "1.0"
    assert data["total_episodes"] == 1
    assert data["total_candidates"] == 1
    assert not data["is_demo_data"]
    assert "scoring_weights" in data

    promo = data["promos"][0]
    assert promo["promo_id"] == "PROMO_001"
    assert promo["title"] == "Altar Betrayal"
    assert len(promo["segments"]) == 2
    assert promo["segments"][0]["episode"] == "Episode 1"
    assert promo["segments"][0]["timestamp_status"] == "available"


def test_csv_export_headers_and_rows(sample_promo_candidate):
    """CSV output contains proper header and row values."""
    csv_str = export_csv([sample_promo_candidate])
    lines = csv_str.strip().split("\n")
    assert len(lines) >= 2  # Header + at least 1 data row
    header = lines[0]
    assert "rank" in header
    assert "promo_id" in header
    assert "final_score" in header
    assert "hook" in header
    assert "cliffhanger" in header

    first_row = lines[1]
    assert "PROMO_001" in first_row
    assert "Altar Betrayal" in first_row


def test_markdown_report_generation(sample_promo_candidate):
    """Markdown report includes title, scoring formula, excerpts, and breakdown."""
    episodes_info = [{"episode_label": "Episode 1", "filename": "ep1.txt"}]
    report = export_markdown_report([sample_promo_candidate], episodes_info, is_demo=False)
    assert "# PromoAI — Promo Analysis Report" in report
    assert "Altar Betrayal" in report
    assert "Hook Strength" in report
    assert "Source Segments" in report
