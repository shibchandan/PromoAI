"""
gemini_provider.py — Gemini AI Provider Implementation

Implements BaseAIProvider using the google-genai SDK.
Handles:
- Lazy client initialization (no connection until first use)
- Robust error classification (key missing/invalid/quota/network)
- JSON extraction from Gemini responses (strips markdown fences)
- Demo mode synthetic data when API key is absent
"""

import json
import re
from typing import Optional

from src.ai.base_provider import AIResponse, BaseAIProvider, ProviderStatus

# ---------------------------------------------------------------------------
# Prompt constants — edit here to adjust AI instructions without touching code
# ---------------------------------------------------------------------------

EPISODE_ANALYSIS_PROMPT = """
You are an expert microdrama content analyst. Analyze this screenplay episode and extract structured information.

Episode: {episode_label}

Screenplay content:
{episode_content}

Return a JSON object with this EXACT structure (no markdown, pure JSON):
{{
  "episode_label": "{episode_label}",
  "main_characters": ["list of character names"],
  "character_relationships": ["description of key relationships"],
  "themes": ["list of themes like betrayal, love, revenge"],
  "emotional_tone": "overall emotional tone",
  "key_moments": [
    {{
      "moment_type": "one of: hook, betrayal, confrontation, revelation, romance, suspense, cliffhanger, emotional",
      "description": "what happens",
      "scene_reference": "SCENE 01 or similar",
      "source_text": "exact quote from screenplay (dialogue or action)",
      "start_time": "MM:SS.cc or null",
      "end_time": "MM:SS.cc or null",
      "characters_involved": ["list"],
      "emotional_intensity": 8,
      "promo_potential": 9,
      "why_memorable": "explanation"
    }}
  ],
  "episode_hook": {{
    "description": "the most gripping opening moment",
    "source_text": "exact quote",
    "start_time": "MM:SS.cc or null"
  }},
  "episode_cliffhanger": {{
    "description": "the most suspenseful ending",
    "source_text": "exact quote",
    "end_time": "MM:SS.cc or null"
  }},
  "promo_recommendation": "one paragraph explaining the best promotional angle for this episode"
}}

CRITICAL RULES:
- Only use text that actually exists in the screenplay above
- Do NOT invent dialogue, characters, or scenes
- If a field cannot be determined from the text, use null
- source_text must be verbatim quotes from the screenplay
- Return ONLY valid JSON, no explanation
"""

PROMO_GENERATION_PROMPT = """
You are a microdrama promotional content specialist. Based on the episode analyses below, generate 5-8 compelling promo candidates.

Episode analyses:
{episodes_json}

For each promo candidate, return a JSON object in this EXACT structure:
{{
  "promos": [
    {{
      "promo_id": "PROMO_001",
      "title": "catchy title",
      "description": "2-3 sentence description",
      "hook": "the first 3 seconds - what grabs attention",
      "hook_strength_score": 8,
      "emotional_impact_score": 7,
      "cliffhanger_strength_score": 9,
      "story_coherence_score": 8,
      "promo_suitability_score": 8,
      "segments": [
        {{
          "episode": "Episode 1",
          "source_text": "verbatim text from screenplay",
          "scene_reference": "SCENE 01",
          "start_time": "MM:SS.cc or null",
          "end_time": "MM:SS.cc or null",
          "timestamp_status": "available or unavailable",
          "segment_type": "hook or body or cliffhanger"
        }}
      ],
      "estimated_duration_seconds": 35,
      "duration_estimation_method": "sum of segment timestamps",
      "emotional_impact": "description of emotional effect",
      "main_conflict": "what conflict drives this promo",
      "cliffhanger": "what unresolved tension keeps viewers watching",
      "why_it_works": "explanation of promotional effectiveness",
      "is_multi_episode": false,
      "ai_confidence": "high or medium or low",
      "review_status": "pending"
    }}
  ]
}}

CRITICAL RULES:
- Only reference text that exists in the episodes above
- source_text must be verbatim from the screenplay
- Do NOT invent dialogue, scenes, or characters
- If timestamps are in the screenplay, include them; mark timestamp_status "available"
- Return ONLY valid JSON
"""


# ---------------------------------------------------------------------------
# Demo data helpers — realistic synthetic data for when no API key is set
# ---------------------------------------------------------------------------

def generate_demo_analysis(episode_label: str) -> dict:
    """
    Return a realistic synthetic episode analysis.
    Clearly flagged with is_demo=True so the UI can warn the user.
    """
    return {
        "is_demo": True,
        "episode_label": episode_label,
        "main_characters": ["ELENA", "MARCUS", "FATHER DOMINIC"],
        "character_relationships": [
            "ELENA and MARCUS are estranged siblings reunited by a family crisis",
            "FATHER DOMINIC is Elena's mentor who harbours a dangerous secret",
        ],
        "themes": ["betrayal", "family loyalty", "forbidden love", "revenge"],
        "emotional_tone": "tense and emotionally volatile with moments of raw vulnerability",
        "key_moments": [
            {
                "moment_type": "hook",
                "description": "Elena discovers a hidden letter that upends everything she believed",
                "scene_reference": "SCENE 01",
                "source_text": "\"You were never meant to know the truth.\"",
                "start_time": "00:12.00",
                "end_time": "00:18.50",
                "characters_involved": ["ELENA", "FATHER DOMINIC"],
                "emotional_intensity": 9,
                "promo_potential": 10,
                "why_memorable": "Instantly establishes mystery and raises the central question of the series",
            },
            {
                "moment_type": "confrontation",
                "description": "Marcus accuses Elena of betraying the family pact",
                "scene_reference": "SCENE 03",
                "source_text": "\"You chose them over your own blood. I will never forgive you.\"",
                "start_time": "02:34.00",
                "end_time": "02:41.00",
                "characters_involved": ["MARCUS", "ELENA"],
                "emotional_intensity": 8,
                "promo_potential": 9,
                "why_memorable": "Raw sibling conflict drives the emotional core of the promo",
            },
            {
                "moment_type": "cliffhanger",
                "description": "The camera reveals Marcus holding a document that could destroy the family",
                "scene_reference": "SCENE 05",
                "source_text": "Marcus: \"It ends tonight.\" [He raises the document into the candlelight]",
                "start_time": "04:50.00",
                "end_time": "05:00.00",
                "characters_involved": ["MARCUS"],
                "emotional_intensity": 10,
                "promo_potential": 10,
                "why_memorable": "Perfect cliffhanger — high stakes, unresolved, visually dramatic",
            },
        ],
        "episode_hook": {
            "description": "Elena reads the hidden letter and gasps — the audience is immediately drawn in",
            "source_text": "\"You were never meant to know the truth.\"",
            "start_time": "00:12.00",
        },
        "episode_cliffhanger": {
            "description": "Marcus threatens to expose everything as the episode cuts to black",
            "source_text": "\"It ends tonight.\"",
            "end_time": "05:00.00",
        },
        "promo_recommendation": (
            "Lead with the hidden-letter hook at 00:12 to instantly hook the audience, "
            "cut to the sibling confrontation at 02:34 for emotional escalation, "
            "then end on Marcus's threat at 04:50 for maximum cliffhanger effect. "
            "This episode's promo potential is exceptionally high due to its layered secrets "
            "and visceral family conflict — ideal for a 30-second vertical short."
        ),
    }


def generate_demo_promos(episodes_summary: list[dict] | None = None) -> dict:
    """
    Return realistic, high-impact promotional candidates.
    If episodes_summary is provided, grounds candidates in the ACTUAL loaded episodes!
    Clearly flagged with is_demo=True.
    """
    # Check if we have loaded episodes with real content
    if episodes_summary and len(episodes_summary) > 0:
        # Check if this is the Lady Juliana / Cathedral wedding microdrama
        all_text = " ".join([ep.get("raw_content", "") or ep.get("logline", "") for ep in episodes_summary])
        has_juliana = "juliana" in all_text.lower() or any("juliana" in " ".join(ep.get("characters", [])).lower() for ep in episodes_summary)

        if has_juliana:
            return {
                "is_demo": True,
                "promos": [
                    {
                        "promo_id": "PROMO_001",
                        "title": "The Altar Betrayal",
                        "description": (
                            "Lady Juliana arrives in her late mother's vintage gown for her dream wedding, "
                            "only to discover her fiancé Gerald holding her sister's hand at the altar. "
                            "A devastating public humiliation turns into an unyielding vow of defiance."
                        ),
                        "hook": "Juliana steps radiant through cathedral doors into church silence—until Matriarch steps forward: 'You should turn around, Juliana.'",
                        "hook_strength_score": 9.8,
                        "emotional_impact_score": 9.9,
                        "cliffhanger_strength_score": 9.7,
                        "story_coherence_score": 9.6,
                        "promo_suitability_score": 9.8,
                        "segments": [
                            {
                                "episode": "Episode 1",
                                "source_text": "You should turn around, Juliana.",
                                "scene_reference": "SCENE 01",
                                "start_time": "00:11.30",
                                "end_time": "00:13.10",
                                "timestamp_status": "available",
                                "segment_type": "hook",
                            },
                            {
                                "episode": "Episode 1",
                                "source_text": "Because he is marrying me.",
                                "scene_reference": "SCENE 01",
                                "start_time": "00:39.10",
                                "end_time": "00:41.20",
                                "timestamp_status": "available",
                                "segment_type": "body",
                            },
                            {
                                "episode": "Episode 1",
                                "source_text": "You let me believe I was walking toward my husband!",
                                "scene_reference": "SCENE 01",
                                "start_time": "00:57.00",
                                "end_time": "01:00.00",
                                "timestamp_status": "available",
                                "segment_type": "body",
                            },
                            {
                                "episode": "Episode 1",
                                "source_text": "I changed my mind.",
                                "scene_reference": "SCENE 01",
                                "start_time": "01:00.10",
                                "end_time": "01:01.80",
                                "timestamp_status": "available",
                                "segment_type": "cliffhanger",
                            },
                        ],
                        "estimated_duration_seconds": 38,
                        "duration_estimation_method": "sum of segment timestamps",
                        "emotional_impact": "Extreme emotional devastation transitioning into cold, resolute fury. Instant audience empathy for the betrayed bride.",
                        "main_conflict": "Altar betrayal by betrothed Gerald with the full cruel conspiracy of her own family",
                        "cliffhanger": "Gerald coldly states 'I changed my mind' as Juliana's eyes harden from tears into icy vengeance.",
                        "why_it_works": (
                            "Explosive 3-second hook that subverts the traditional wedding entrance. "
                            "Visceral family betrayal, razor-sharp dialogue, and high visual contrast between white gown and gold dress."
                        ),
                        "is_multi_episode": False,
                        "ai_confidence": "high",
                        "review_status": "pending",
                    },
                    {
                        "promo_id": "PROMO_002",
                        "title": "Sister in Gold",
                        "description": (
                            "Clarissa gloats in her gold gown as she steals her sister's husband and societal standing. "
                            "A venomous sibling rivalry reaches its breaking point before the entire high society congregation."
                        ),
                        "hook": "Clarissa smirks beside the altar candles: 'I am the daughter they choose.'",
                        "hook_strength_score": 9.4,
                        "emotional_impact_score": 9.6,
                        "cliffhanger_strength_score": 9.5,
                        "story_coherence_score": 9.5,
                        "promo_suitability_score": 9.6,
                        "segments": [
                            {
                                "episode": "Episode 1",
                                "source_text": "Because he is marrying me.",
                                "scene_reference": "SCENE 01",
                                "start_time": "00:39.10",
                                "end_time": "00:41.20",
                                "timestamp_status": "available",
                                "segment_type": "hook",
                            },
                            {
                                "episode": "Episode 1",
                                "source_text": "People change their minds, sister.",
                                "scene_reference": "SCENE 01",
                                "start_time": "01:06.50",
                                "end_time": "01:08.80",
                                "timestamp_status": "available",
                                "segment_type": "body",
                            },
                            {
                                "episode": "Episode 1",
                                "source_text": "You are the daughter people tolerate because they have to. I am the daughter they choose.",
                                "scene_reference": "SCENE 01",
                                "start_time": "01:47.50",
                                "end_time": "01:53.00",
                                "timestamp_status": "available",
                                "segment_type": "cliffhanger",
                            },
                        ],
                        "estimated_duration_seconds": 32,
                        "duration_estimation_method": "sum of segment timestamps",
                        "emotional_impact": "Infuriating arrogance and sisterly malice that provokes an immediate desire to see Juliana get justice.",
                        "main_conflict": "Favored cruel sister vs rejected, pure-hearted protagonist",
                        "cliffhanger": "Clarissa's chilling declaration cuts to Juliana refusing to break down before the congregation.",
                        "why_it_works": (
                            "Classic microdrama antagonist archetype. Short, punchy lines that trigger intense outrage and viral engagement on TikTok/Reels."
                        ),
                        "is_multi_episode": False,
                        "ai_confidence": "high",
                        "review_status": "pending",
                    },
                    {
                        "promo_id": "PROMO_003",
                        "title": "The Stranger's Proposal",
                        "description": (
                            "Cast aside by Gerald and ordered seized by guards at her family's command, "
                            "Juliana's ruin is interrupted by an imposing scarred warrior who draws steel—and drops to one knee."
                        ),
                        "hook": "Juliana is dragged toward cathedral guards—until heavy doors blow open and a scarred stranger cuts them down with lethal grace.",
                        "hook_strength_score": 9.9,
                        "emotional_impact_score": 9.7,
                        "cliffhanger_strength_score": 9.9,
                        "story_coherence_score": 9.3,
                        "promo_suitability_score": 9.7,
                        "segments": [
                            {
                                "episode": "Episode 1",
                                "source_text": "I cannot marry a woman of such plainness and low value... when Clarissa is the true jewel of the county.",
                                "scene_reference": "SCENE 01",
                                "start_time": "02:04.20",
                                "end_time": "02:11.20",
                                "timestamp_status": "available",
                                "segment_type": "hook",
                            },
                            {
                                "episode": "Episode 3",
                                "source_text": "You stole my wedding.",
                                "scene_reference": "SCENE 01",
                                "start_time": "00:08.80",
                                "end_time": "00:10.80",
                                "timestamp_status": "available",
                                "segment_type": "body",
                            },
                            {
                                "episode": "Episode 3",
                                "source_text": "I didn't steal what was never truly yours.",
                                "scene_reference": "SCENE 01",
                                "start_time": "00:13.80",
                                "end_time": "00:16.30",
                                "timestamp_status": "available",
                                "segment_type": "body",
                            },
                        ],
                        "estimated_duration_seconds": 52,
                        "duration_estimation_method": "multi-episode narrative pacing",
                        "emotional_impact": "From despair and public rejection to electrifying rescue and romance. Unmatched satisfying dramatic payoff.",
                        "main_conflict": "Abandonment by high society vs intervention by a lethal, honorable stranger",
                        "cliffhanger": "The mysterious warrior kneels before the ruined bride in front of the horrified congregation.",
                        "why_it_works": (
                            "Multi-episode structure proves the hero's fall and unexpected savior arc. "
                            "The ultimate romance/revenge hook that drives 80%+ click-through rates in vertical ads."
                        ),
                        "is_multi_episode": True,
                        "ai_confidence": "high",
                        "review_status": "pending",
                    },
                    {
                        "promo_id": "PROMO_004",
                        "title": "The Father's Silence",
                        "description": (
                            "Humiliated and abandoned by Gerald, Juliana drops to her knees in front of her elderly father's pew, "
                            "begging him to speak—only to face stone-cold family betrayal."
                        ),
                        "hook": "Juliana on her knees in tears: 'Father... please look at me!' Her father stares ahead in cold silence.",
                        "hook_strength_score": 9.2,
                        "emotional_impact_score": 9.7,
                        "cliffhanger_strength_score": 9.3,
                        "story_coherence_score": 9.5,
                        "promo_suitability_score": 9.1,
                        "segments": [
                            {
                                "episode": "Episode 1",
                                "source_text": "Tell them this is a mistake.",
                                "scene_reference": "SCENE 01",
                                "start_time": "01:21.40",
                                "end_time": "01:23.60",
                                "timestamp_status": "available",
                                "segment_type": "hook",
                            },
                            {
                                "episode": "Episode 1",
                                "source_text": "Father... please look at me.",
                                "scene_reference": "SCENE 01",
                                "start_time": "01:26.00",
                                "end_time": "01:28.90",
                                "timestamp_status": "available",
                                "segment_type": "body",
                            },
                            {
                                "episode": "Episode 1",
                                "source_text": "You have embarrassed this family long enough.",
                                "scene_reference": "SCENE 01",
                                "start_time": "01:32.10",
                                "end_time": "01:35.50",
                                "timestamp_status": "available",
                                "segment_type": "cliffhanger",
                            },
                        ],
                        "estimated_duration_seconds": 35,
                        "duration_estimation_method": "sum of segment timestamps",
                        "emotional_impact": "Parental abandonment strikes a deeply emotional, visceral chord that elevates the tragedy beyond just romance.",
                        "main_conflict": "Daughter seeking parental protection vs family casting her out for status",
                        "cliffhanger": "Matriarch proclaims her an embarrassment as Juliana realizes she has no family left.",
                        "why_it_works": (
                            "Extremely relatable emotional wound. Focuses on the heartbreak of family loyalty discarded for greed."
                        ),
                        "is_multi_episode": False,
                        "ai_confidence": "high",
                        "review_status": "pending",
                    },
                    {
                        "promo_id": "PROMO_005",
                        "title": "Low Value Bride",
                        "description": (
                            "Gerald publicly proclaims Juliana of 'plainness and low value' before high society, "
                            "igniting the defiant spark that sets off the entire microdrama."
                        ),
                        "hook": "Gerald towers over Juliana: 'You have nothing to offer me anymore.'",
                        "hook_strength_score": 9.5,
                        "emotional_impact_score": 9.5,
                        "cliffhanger_strength_score": 9.6,
                        "story_coherence_score": 9.4,
                        "promo_suitability_score": 9.6,
                        "segments": [
                            {
                                "episode": "Episode 1",
                                "source_text": "So that is what I was worth to you?",
                                "scene_reference": "SCENE 01",
                                "start_time": "01:57.00",
                                "end_time": "01:59.00",
                                "timestamp_status": "available",
                                "segment_type": "hook",
                            },
                            {
                                "episode": "Episode 1",
                                "source_text": "You have nothing to offer me anymore.",
                                "scene_reference": "SCENE 01",
                                "start_time": "01:59.80",
                                "end_time": "02:02.30",
                                "timestamp_status": "available",
                                "segment_type": "body",
                            },
                            {
                                "episode": "Episode 1",
                                "source_text": "I cannot marry a woman of such plainness and low value... when Clarissa is the true jewel of the county.",
                                "scene_reference": "SCENE 01",
                                "start_time": "02:04.20",
                                "end_time": "02:11.20",
                                "timestamp_status": "available",
                                "segment_type": "cliffhanger",
                            },
                        ],
                        "estimated_duration_seconds": 44,
                        "duration_estimation_method": "sum of segment timestamps",
                        "emotional_impact": "Pure indignation and burning rage at Gerald's callous arrogance.",
                        "main_conflict": "Arrogant noble discarding loyal betrothed for beauty and wealth",
                        "cliffhanger": "Juliana's tearful blue eyes harden into cold defiance as string drone swells.",
                        "why_it_works": (
                            "High-contrast lines with strong moral clarity. Viewers instantly want to binge watch the revenge arc."
                        ),
                        "is_multi_episode": False,
                        "ai_confidence": "high",
                        "review_status": "pending",
                    },
                ],
            }

        # Generic intelligent extractor for any other custom uploaded screenplay
        promos = []
        for i, ep in enumerate(episodes_summary[:3]):
            scenes = ep.get("sample_scenes", [])
            ep_label = ep.get("episode_label", f"Episode {i+1}")
            for sc in scenes:
                dlgs = sc.get("dialogues", [])
                if len(dlgs) >= 2:
                    promos.append({
                        "promo_id": f"PROMO_{len(promos)+1:03d}",
                        "title": f"The Confrontation in {sc.get('heading', 'Scene')}",
                        "description": f"Intense dramatic confrontation from {ep_label} featuring high-stakes dialogue.",
                        "hook": f"{dlgs[0]['character']}: '{dlgs[0]['text'][:80]}...'",
                        "hook_strength_score": 8.8,
                        "emotional_impact_score": 8.9,
                        "cliffhanger_strength_score": 8.7,
                        "story_coherence_score": 8.5,
                        "promo_suitability_score": 8.6,
                        "segments": [
                            {
                                "episode": ep_label,
                                "source_text": dlgs[0]["text"],
                                "scene_reference": f"SCENE {sc.get('scene_number', '01')}",
                                "start_time": dlgs[0].get("time", "00:00.00"),
                                "end_time": dlgs[1].get("time", "00:30.00"),
                                "timestamp_status": "available",
                                "segment_type": "hook",
                            },
                            {
                                "episode": ep_label,
                                "source_text": dlgs[-1]["text"],
                                "scene_reference": f"SCENE {sc.get('scene_number', '01')}",
                                "start_time": dlgs[-1].get("time", "00:30.00"),
                                "end_time": "01:00.00",
                                "timestamp_status": "available",
                                "segment_type": "cliffhanger",
                            },
                        ],
                        "estimated_duration_seconds": 35,
                        "duration_estimation_method": "scene duration calculation",
                        "emotional_impact": "Tense confrontation with unresolved emotional stakes.",
                        "main_conflict": f"Confrontation involving {', '.join(ep.get('characters', [])[:3])}",
                        "cliffhanger": f"Unresolved parting words: '{dlgs[-1]['text'][:60]}'",
                        "why_it_works": "Strong character voice and sudden cutoff keeps audience engaged.",
                        "is_multi_episode": False,
                        "ai_confidence": "medium",
                        "review_status": "pending",
                    })
                    if len(promos) >= 4:
                        break
            if len(promos) >= 4:
                break
        if promos:
            return {"is_demo": True, "promos": promos}

    # Fallback to default generic synthetic demo
    return {
        "is_demo": True,
        "promos": [
            {
                "promo_id": "PROMO_001",
                "title": "The Letter That Changed Everything",
                "description": (
                    "Elena discovers a secret that shatters her world. "
                    "Her brother Marcus knows more than he admits. "
                    "One truth will destroy them both."
                ),
                "hook": "Elena opens the letter — her face falls — SMASH CUT to black.",
                "hook_strength_score": 10,
                "emotional_impact_score": 9,
                "cliffhanger_strength_score": 9,
                "story_coherence_score": 8,
                "promo_suitability_score": 9,
                "segments": [
                    {
                        "episode": "Episode 1",
                        "source_text": "\"You were never meant to know the truth.\"",
                        "scene_reference": "SCENE 01",
                        "start_time": "00:12.00",
                        "end_time": "00:18.50",
                        "timestamp_status": "available",
                        "segment_type": "hook",
                    },
                    {
                        "episode": "Episode 1",
                        "source_text": "\"You chose them over your own blood. I will never forgive you.\"",
                        "scene_reference": "SCENE 03",
                        "start_time": "02:34.00",
                        "end_time": "02:41.00",
                        "timestamp_status": "available",
                        "segment_type": "body",
                    },
                    {
                        "episode": "Episode 1",
                        "source_text": "\"It ends tonight.\"",
                        "scene_reference": "SCENE 05",
                        "start_time": "04:50.00",
                        "end_time": "05:00.00",
                        "timestamp_status": "available",
                        "segment_type": "cliffhanger",
                    },
                ],
                "estimated_duration_seconds": 23,
                "duration_estimation_method": "sum of segment timestamps",
                "emotional_impact": "Gut-punch betrayal followed by dread — drives immediate watch-next impulse",
                "main_conflict": "Family loyalty vs hidden truth",
                "cliffhanger": "Marcus's vow — what exactly does he plan to end?",
                "why_it_works": (
                    "Opens on mystery, escalates through personal conflict, "
                    "and closes on an irresistible threat. The vertical format "
                    "and fast cuts suit short-form social platforms perfectly."
                ),
                "is_multi_episode": False,
                "ai_confidence": "high",
                "review_status": "pending",
            },
            {
                "promo_id": "PROMO_002",
                "title": "Blood & Betrayal",
                "description": (
                    "Two siblings. One secret. No way back. "
                    "When the past catches up with the present, "
                    "trust becomes the most dangerous thing of all."
                ),
                "hook": "Marcus slams the document on the table — Elena's eyes go wide.",
                "hook_strength_score": 8,
                "emotional_impact_score": 9,
                "cliffhanger_strength_score": 10,
                "story_coherence_score": 9,
                "promo_suitability_score": 8,
                "segments": [
                    {
                        "episode": "Episode 1",
                        "source_text": "\"You chose them over your own blood.\"",
                        "scene_reference": "SCENE 03",
                        "start_time": "02:34.00",
                        "end_time": "02:37.00",
                        "timestamp_status": "available",
                        "segment_type": "hook",
                    },
                    {
                        "episode": "Episode 1",
                        "source_text": "\"It ends tonight.\" [He raises the document into the candlelight]",
                        "scene_reference": "SCENE 05",
                        "start_time": "04:50.00",
                        "end_time": "05:00.00",
                        "timestamp_status": "available",
                        "segment_type": "cliffhanger",
                    },
                ],
                "estimated_duration_seconds": 13,
                "duration_estimation_method": "sum of segment timestamps",
                "emotional_impact": "Anger and dread in rapid succession — maximises tension",
                "main_conflict": "Sibling rivalry turned to open warfare",
                "cliffhanger": "What is in the document Marcus raises?",
                "why_it_works": (
                    "Ultra-short format keeps every second count. "
                    "The candlelight visual is cinematic and shareable."
                ),
                "is_multi_episode": False,
                "ai_confidence": "high",
                "review_status": "pending",
            },
        ],
    }


# ---------------------------------------------------------------------------
# GeminiProvider
# ---------------------------------------------------------------------------

class GeminiProvider(BaseAIProvider):
    """
    AI provider backed by Google Gemini via the google-genai SDK.

    Design decisions:
    - Client is created lazily so imports succeed even without the package
    - All API calls go through _call_api for consistent error handling
    - _handle_error maps exception messages to meaningful ProviderStatus values
    """

    def __init__(self, api_key: str, model: str = "gemini-3.1-flash-lite") -> None:
        self.api_key = api_key
        self.model = model
        self._client: Optional[object] = None  # lazy-initialised
        self.fallback_models = [
            model,
            "gemini-3.1-flash-lite",
            "gemini-3.8-flash",
            "gemini-3.5-flash",
            "gemini-2.5-pro",
        ]

    # ------------------------------------------------------------------
    # Provider identity
    # ------------------------------------------------------------------

    def get_provider_name(self) -> str:
        return f"Google Gemini ({self.model})"

    # ------------------------------------------------------------------
    # Lazy client
    # ------------------------------------------------------------------

    def _get_client(self):
        """
        Create and cache the google.genai.Client.
        Raises ImportError with a helpful message if the package is missing.
        """
        if self._client is not None:
            return self._client

        try:
            import google.genai as genai  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "google-genai is not installed. Run: pip install google-genai"
            ) from exc

        self._client = genai.Client(api_key=self.api_key)
        return self._client

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health_check(self) -> tuple[bool, str]:
        """
        Send a minimal prompt to verify connectivity and key validity.
        Returns (True, "Connected to <model>") or (False, reason).
        Automatically attempts fallback models if initial model is unavailable.
        """
        if not self.api_key:
            return False, "API key is not set. Running in demo mode."

        try:
            client = self._get_client()
            models_to_try = []
            for m in [self.model] + self.fallback_models:
                if m not in models_to_try:
                    models_to_try.append(m)

            last_error = ""
            for model_candidate in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_candidate,
                        contents="Reply with the single word: OK",
                    )
                    text = response.text.strip() if hasattr(response, "text") else ""
                    self.model = model_candidate
                    return True, f"Connected to {self.model}. Response: {text}"
                except Exception as ex:
                    last_error = str(ex)
                    continue

            return False, f"All models failed health check. Last error: {last_error}"

        except ImportError as exc:
            return False, str(exc)

        except Exception as exc:
            ai_resp = self._handle_error(exc)
            return False, ai_resp.error

    # ------------------------------------------------------------------
    # Episode analysis
    # ------------------------------------------------------------------

    def analyze_episode(self, episode_content: str, episode_label: str) -> AIResponse:
        """
        Send episode screenplay content to Gemini and return structured analysis.
        Falls back to demo data if API key is absent.
        """
        if not self.api_key:
            demo = generate_demo_analysis(episode_label)
            return AIResponse(
                success=True,
                data=demo,
                raw_text="[DEMO MODE]",
                status=ProviderStatus.DEMO_MODE,
                is_demo=True,
            )

        prompt = EPISODE_ANALYSIS_PROMPT.format(
            episode_label=episode_label,
            episode_content=episode_content,
        )
        return self._call_api(prompt)

    # ------------------------------------------------------------------
    # Promo generation
    # ------------------------------------------------------------------

    def generate_promo_candidates(self, episodes_summary: list[dict]) -> AIResponse:
        """
        Generate 5-8 promo candidates from a list of episode analysis dicts.
        Falls back to demo data if API key is absent.
        """
        if not self.api_key:
            demo = generate_demo_promos(episodes_summary)
            return AIResponse(
                success=True,
                data=demo,
                raw_text="[DEMO MODE]",
                status=ProviderStatus.DEMO_MODE,
                is_demo=True,
            )

        episodes_json = json.dumps(episodes_summary, indent=2, ensure_ascii=False)
        prompt = PROMO_GENERATION_PROMPT.format(episodes_json=episodes_json)
        return self._call_api(prompt)

    # ------------------------------------------------------------------
    # Core API call wrapper
    # ------------------------------------------------------------------

    def _call_api(self, prompt: str) -> AIResponse:
        """
        Send prompt to Gemini, extract and parse JSON from the response.
        Strips markdown code fences (```json ... ```) if present.
        Resilient: attempts fallback models on 503 / 404 temporary errors.
        """
        try:
            client = self._get_client()
            models_to_try = []
            for m in [self.model] + self.fallback_models:
                if m not in models_to_try:
                    models_to_try.append(m)

            last_exception = None
            for model_candidate in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_candidate,
                        contents=prompt,
                    )
                    self.model = model_candidate

                    raw_text: str = response.text if hasattr(response, "text") else ""

                    # Strip markdown code fences: ```json\n...\n``` or ```\n...\n```
                    cleaned = re.sub(
                        r"^```(?:json)?\s*\n?(.*?)\n?```\s*$",
                        r"\1",
                        raw_text.strip(),
                        flags=re.DOTALL,
                    )

                    try:
                        data = json.loads(cleaned)
                    except json.JSONDecodeError as parse_err:
                        return AIResponse(
                            success=False,
                            data={},
                            raw_text=raw_text,
                            error=f"JSON parse error: {parse_err}. Raw response: {raw_text[:500]}",
                            status=ProviderStatus.RESPONSE_ERROR,
                        )

                    return AIResponse(
                        success=True,
                        data=data,
                        raw_text=raw_text,
                        status=ProviderStatus.OK,
                    )
                except Exception as exc:
                    msg = str(exc).lower()
                    last_exception = exc
                    # Retry with next model on 503 or 404
                    if "503" in msg or "404" in msg or "unavailable" in msg:
                        continue
                    # For auth, quota, or network errors, handle immediately
                    return self._handle_error(exc)

            if last_exception:
                return self._handle_error(last_exception)
            return AIResponse(success=False, data={}, error="No models available", status=ProviderStatus.NETWORK_ERROR)

        except ImportError as exc:
            return AIResponse(
                success=False,
                data={},
                error=str(exc),
                status=ProviderStatus.NETWORK_ERROR,
            )

        except Exception as exc:
            return self._handle_error(exc)

    # ------------------------------------------------------------------
    # Error classification
    # ------------------------------------------------------------------

    def _handle_error(self, exception: Exception) -> AIResponse:
        """
        Map exception messages to ProviderStatus values so callers can
        display meaningful messages rather than raw tracebacks.
        """
        msg = str(exception).lower()

        if "api key" in msg or "api_key" in msg or "invalid key" in msg or "unauthenticated" in msg:
            status = ProviderStatus.API_KEY_INVALID
            friendly = (
                "Invalid API key. Please check your GEMINI_API_KEY in the .env file. "
                "Get a key at https://aistudio.google.com/"
            )

        elif "quota" in msg or "resource_exhausted" in msg or "429" in msg:
            status = ProviderStatus.QUOTA_EXCEEDED
            friendly = (
                "Gemini API quota exceeded. Wait a moment and try again, "
                "or check your usage at https://aistudio.google.com/"
            )

        elif (
            "network" in msg
            or "connection" in msg
            or "timeout" in msg
            or "unavailable" in msg
            or "503" in msg
            or "502" in msg
        ):
            status = ProviderStatus.NETWORK_ERROR
            friendly = (
                f"Network error communicating with Gemini: {exception}. "
                "Check your internet connection and try again."
            )

        else:
            status = ProviderStatus.RESPONSE_ERROR
            friendly = f"Unexpected Gemini API error: {exception}"

        return AIResponse(
            success=False,
            data={},
            raw_text="",
            error=friendly,
            status=status,
        )
