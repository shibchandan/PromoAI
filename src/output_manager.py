"""
output_manager.py — Export and Output Management

Handles saving and exporting promo analysis results.
Supported formats: JSON, CSV, Markdown report
"""

import json
import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from src.promo_detector import PromoCandidate
from src import config


def candidates_to_dict(candidates: list[PromoCandidate]) -> list[dict]:
    """Convert PromoCandidate Pydantic objects to plain dicts for JSON export."""
    result = []
    for c in candidates:
        d = c.model_dump()
        # Convert enum values to strings
        d["review_status"] = c.review_status.value
        for seg in d.get("segments", []):
            seg["timestamp_status"] = seg.get("timestamp_status", "unavailable")
        result.append(d)
    return result


def build_json_output(
    candidates: list[PromoCandidate],
    episodes_info: list[dict],
    is_demo: bool = False
) -> dict:
    """
    Build the complete JSON output structure.
    
    The structure includes project metadata plus all promo candidates
    with their scores, segments, source references, and review status.
    """
    return {
        "project": "PromoAI",
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "is_demo_data": is_demo,
        "total_episodes": len(episodes_info),
        "total_candidates": len(candidates),
        "scoring_weights": config.SCORING_WEIGHTS,
        "episodes_summary": episodes_info,
        "promos": candidates_to_dict(candidates),
    }


def export_json(
    candidates: list[PromoCandidate],
    episodes_info: list[dict],
    is_demo: bool = False
) -> str:
    """Return JSON string of full output. Raises ValueError if serialization fails."""
    data = build_json_output(candidates, episodes_info, is_demo)
    return json.dumps(data, indent=2, ensure_ascii=False)


def export_csv(candidates: list[PromoCandidate]) -> str:
    """
    Return CSV string with one row per candidate.
    Multi-segment promos are summarized (not exploded into multiple rows).
    """
    output = io.StringIO()
    
    fieldnames = [
        "rank", "promo_id", "title", "final_score",
        "hook_strength", "emotional_impact", "cliffhanger_strength",
        "story_coherence", "promo_suitability",
        "hook", "cliffhanger", "main_conflict",
        "emotional_impact_description", "why_it_works",
        "estimated_duration_seconds", "is_multi_episode",
        "episodes_used", "segment_count",
        "ai_confidence", "review_status", "validation_flag_count",
        "is_demo"
    ]
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    
    for rank, c in enumerate(candidates, 1):
        episodes_used = list({seg.episode for seg in c.segments})
        writer.writerow({
            "rank": rank,
            "promo_id": c.promo_id,
            "title": c.title,
            "final_score": c.final_score,
            "hook_strength": c.scores.hook_strength,
            "emotional_impact": c.scores.emotional_impact,
            "cliffhanger_strength": c.scores.cliffhanger_strength,
            "story_coherence": c.scores.story_coherence,
            "promo_suitability": c.scores.promo_suitability,
            "hook": c.hook,
            "cliffhanger": c.cliffhanger,
            "main_conflict": c.main_conflict,
            "emotional_impact_description": c.emotional_impact,
            "why_it_works": c.why_it_works,
            "estimated_duration_seconds": c.estimated_duration_seconds or "",
            "is_multi_episode": c.is_multi_episode,
            "episodes_used": "; ".join(episodes_used),
            "segment_count": len(c.segments),
            "ai_confidence": c.ai_confidence,
            "review_status": c.review_status.value if hasattr(c.review_status, "value") else c.review_status,
            "validation_flag_count": len(c.validation_flags),
            "is_demo": c.is_demo,
        })
    
    return output.getvalue()


def export_markdown_report(
    candidates: list[PromoCandidate],
    episodes_info: list[dict],
    is_demo: bool = False
) -> str:
    """
    Generate a full Markdown report suitable for sharing.
    Includes all candidates with scores, excerpts, and explanations.
    """
    lines = []
    lines.append("# PromoAI — Promo Analysis Report")
    lines.append(f"\n**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    if is_demo:
        lines.append("\n> ⚠️ **DEMO MODE** — Results below are synthetic sample data, NOT real AI analysis.")
    lines.append(f"\n**Total Episodes Analyzed:** {len(episodes_info)}")
    lines.append(f"**Total Promo Candidates:** {len(candidates)}")
    lines.append("\n---\n")
    
    lines.append("## Scoring Formula\n")
    lines.append("S = 0.25×Hook + 0.20×Emotion + 0.25×Cliffhanger + 0.15×Coherence + 0.15×Suitability\n")
    
    lines.append("## Ranked Promo Candidates\n")
    
    for rank, c in enumerate(candidates, 1):
        lines.append(f"### #{rank} — {c.title}")
        lines.append(f"**Promo ID:** {c.promo_id} | **Final Score:** {c.final_score}/10")
        if c.is_demo:
            lines.append("*[DEMO DATA — not real AI analysis]*")
        lines.append(f"\n**Description:** {c.description}")
        lines.append(f"\n**🎣 Hook:** {c.hook}")
        lines.append(f"\n**💥 Cliffhanger:** {c.cliffhanger}")
        lines.append(f"\n**❤️ Emotional Impact:** {c.emotional_impact}")
        lines.append(f"\n**⚔️ Main Conflict:** {c.main_conflict}")
        lines.append(f"\n**⏱️ Estimated Duration:** {c.estimated_duration_seconds or 'Unknown'} seconds")
        lines.append(f"\n**✅ Why It Works:** {c.why_it_works}")
        
        lines.append("\n**Score Breakdown:**")
        lines.append(f"- Hook Strength: {c.scores.hook_strength}/10")
        lines.append(f"- Emotional Impact: {c.scores.emotional_impact}/10")
        lines.append(f"- Cliffhanger Strength: {c.scores.cliffhanger_strength}/10")
        lines.append(f"- Story Coherence: {c.scores.story_coherence}/10")
        lines.append(f"- Promo Suitability: {c.scores.promo_suitability}/10")
        
        lines.append("\n**Source Segments:**")
        for i, seg in enumerate(c.segments, 1):
            lines.append(f"\n*Segment {i} — {seg.episode} ({seg.scene_reference or 'N/A'}):*")
            lines.append(f"> {seg.source_text}")
            ts = f"{seg.start_time} → {seg.end_time}" if seg.start_time else "N/A"
            lines.append(f"Timestamp: {ts} [Status: {seg.timestamp_status}]")
        
        if c.validation_flags:
            lines.append("\n**⚠️ Validation Flags:**")
            for flag in c.validation_flags:
                lines.append(f"- {flag}")
        
        lines.append(f"\n**Review Status:** {c.review_status}")
        if c.reviewer_comment:
            lines.append(f"**Reviewer Comment:** {c.reviewer_comment}")
        
        lines.append("\n---\n")
    
    return "\n".join(lines)


def save_output_to_file(content: str, filename: str, output_dir: Path = None) -> Path:
    """Save content string to file in output directory."""
    if output_dir is None:
        output_dir = config.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath
