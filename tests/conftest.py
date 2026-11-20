"""
conftest.py — Pytest Configuration and Shared Fixtures

Provides realistic mocked test data for unit tests without hitting the real Gemini API.
"""

import io
import pytest
from src.file_processor import EpisodeFile
from src.screenplay_parser import (
    Episode,
    Scene,
    DialogueLine,
    ActionLine,
    TimestampStatus,
)
from src.promo_detector import (
    PromoCandidate,
    PromoSegment,
    ScoreBreakdown,
    ReviewStatus,
)

SAMPLE_SCREENPLAY_CONTENT = """EPISODE NUMBER: Episode 1
EPISODE LOGLINE: Lady Juliana arrives at the cathedral in her late mother's bridal gown, only to suffer betrayal.
CONTINUITY NOTES: First episode of the series.

--- SCRIPT START ---

SCENE 01
Scene heading: INT. CATHEDRAL – DAY
Scene start: 00:00.00
Scene end: 01:30.00

Actions and dialogue:

**CAMERA:**
Start: (00:00.00) | End: (00:05.00)
Wide shot of Juliana walking down the aisle.

**ACTION:**
Start: (00:01.00) | End: (00:05.00)
Juliana pauses at the threshold, radiant in white silk.

**MATRIARCH (Cold, Commanding):**
Start: (00:11.30) | End: (00:13.10)
"You should turn around, Juliana."

**LADY JULIANA (Confused, Breathless):**
Start: (00:13.50) | End: (00:14.30)
"Why?"

**THE FORMER GROOM (Cold, Callous):**
Start: (01:00.10) | End: (01:01.80)
"I changed my mind."

**SOUND FX:**
Start: (01:25.00) | End: (01:28.00)
Ominous string swell rises to a crescendo.

SCENE 02
Scene heading: INT. CATHEDRAL VESTRY – DAY
Scene start: 01:30.00
Scene end: 02:18.00

Actions and dialogue:

**LADY JULIANA (Betrayed, Piercing):**
Start: (01:35.00) | End: (01:38.00)
"You swore you loved me!"

**LADY IN GOLD GOWN (Mocking):**
Start: (01:40.00) | End: (01:43.00)
"People change their minds, sister."

--- SCRIPT END ---
"""


@pytest.fixture
def sample_screenplay_text() -> str:
    """Raw sample screenplay text."""
    return SAMPLE_SCREENPLAY_CONTENT


@pytest.fixture
def sample_episode_file() -> EpisodeFile:
    """A valid EpisodeFile instance."""
    return EpisodeFile(
        filename="episode-001-Episode 1671703.txt",
        episode_label="Episode 1",
        content=SAMPLE_SCREENPLAY_CONTENT,
        file_size_bytes=len(SAMPLE_SCREENPLAY_CONTENT.encode("utf-8")),
        is_valid=True,
    )


@pytest.fixture
def sample_parsed_episode() -> Episode:
    """A parsed Episode instance."""
    d1 = DialogueLine(
        character="MATRIARCH",
        emotion="Cold, Commanding",
        text="You should turn around, Juliana.",
        start_time="00:11.30",
        end_time="00:13.10",
        start_seconds=11.3,
        end_seconds=13.1,
        timestamp_status=TimestampStatus.AVAILABLE,
        line_number=20,
    )
    d2 = DialogueLine(
        character="THE FORMER GROOM",
        emotion="Cold, Callous",
        text="I changed my mind.",
        start_time="01:00.10",
        end_time="01:01.80",
        start_seconds=60.1,
        end_seconds=61.8,
        timestamp_status=TimestampStatus.AVAILABLE,
        line_number=35,
    )
    act1 = ActionLine(
        action_type="CAMERA",
        description="Wide shot of Juliana walking down the aisle.",
        start_time="00:00.00",
        end_time="00:05.00",
        start_seconds=0.0,
        end_seconds=5.0,
        timestamp_status=TimestampStatus.AVAILABLE,
        line_number=15,
    )
    scene1 = Scene(
        scene_number="01",
        heading="INT. CATHEDRAL – DAY",
        start_time="00:00.00",
        end_time="01:30.00",
        start_seconds=0.0,
        end_seconds=90.0,
        duration_seconds=90.0,
        dialogues=[d1, d2],
        actions=[act1],
        characters_present=["MATRIARCH", "THE FORMER GROOM"],
        raw_text="Sample scene text",
    )
    return Episode(
        episode_label="Episode 1",
        episode_number=1,
        logline="Lady Juliana arrives at the cathedral only to suffer betrayal.",
        continuity_notes="First episode of the series.",
        filename="episode-001-Episode 1671703.txt",
        scenes=[scene1],
        all_characters=["MATRIARCH", "THE FORMER GROOM"],
        total_duration_seconds=90.0,
        total_scenes=1,
        raw_content=SAMPLE_SCREENPLAY_CONTENT,
    )


@pytest.fixture
def sample_promo_candidate() -> PromoCandidate:
    """A valid PromoCandidate instance."""
    return PromoCandidate(
        promo_id="PROMO_001",
        title="Altar Betrayal",
        description="Juliana arrives for her wedding only to find Gerald with her sister.",
        hook="Juliana pauses at the cathedral door, smiles, then sees her sister holding Gerald's hand.",
        segments=[
            PromoSegment(
                episode="Episode 1",
                source_text="You should turn around, Juliana.",
                scene_reference="SCENE 01",
                start_time="00:11.30",
                end_time="00:13.10",
                timestamp_status=TimestampStatus.AVAILABLE,
                segment_type="hook",
            ),
            PromoSegment(
                episode="Episode 1",
                source_text="I changed my mind.",
                scene_reference="SCENE 01",
                start_time="01:00.10",
                end_time="01:01.80",
                timestamp_status=TimestampStatus.AVAILABLE,
                segment_type="cliffhanger",
            ),
        ],
        estimated_duration_seconds=35,
        duration_estimation_method="sum of segment timestamps",
        emotional_impact="Shock and betrayal",
        main_conflict="Juliana abandoned at altar for her sister Clarissa",
        cliffhanger="Gerald states 'I changed my mind' as Juliana's expression hardens.",
        why_it_works="Immediate high stakes and universal theme of betrayal.",
        is_multi_episode=False,
        scores=ScoreBreakdown(
            hook_strength=9.0,
            emotional_impact=9.0,
            cliffhanger_strength=9.5,
            story_coherence=8.5,
            promo_suitability=9.0,
        ),
        final_score=0.0,
        ai_confidence="high",
        review_status=ReviewStatus.PENDING,
        reviewer_comment="",
        is_demo=False,
        validation_flags=[],
    )
