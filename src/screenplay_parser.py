"""
screenplay_parser.py — Screenplay File Parser for PromoAI

This module parses structured screenplay text files into Pydantic models that
the rest of the PromoAI pipeline can consume.

Screenplay format expected:
    EPISODE NUMBER: Episode 1
    EPISODE LOGLINE: ...
    CONTINUITY NOTES: ...

    --- SCRIPT START ---

    SCENE 01
    Scene heading: INT. CATHEDRAL – DAY
    Scene start: 00:00.00
    Scene end: 02:18.00

    Actions and dialogue:

    **CAMERA:**
    Start: (00:00.00) | End: (00:04.80)
    Camera description text...

    **CHARACTER_NAME (Emotion):**
    Start: (00:11.30) | End: (00:13.10)
    "Dialogue text goes here."

    **ACTION:**
    Start: (00:01.00) | End: (00:04.80)
    Action description...

    **SOUND FX:**
    Start: (02:15.00) | End: (02:17.50)
    Sound description...

    --- SCRIPT END ---

Timestamps use MM:SS.cc (minutes:seconds.centiseconds) format.
Centiseconds (cc) represent hundredths of a second, so 04.80 means 4.80 seconds.
"""

import logging
import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Action-type block tag names (not character dialogue)
ACTION_TAGS = {"ACTION", "CAMERA", "SOUND FX", "SOUND", "FX", "SFX", "VFX", "MUSIC"}

# Regex to match a **TAG:** bold block header line.
# The screenplay format uses **TAG_TEXT:** where the colon is inside the
# bold markers, e.g. **CAMERA:** or **MATRIARCH (Cold, Commanding):**
# Pattern: ** then capture group (tag text including optional emotion) then :**
_BOLD_TAG_RE = re.compile(r"^\*\*(.+?):\*\*\s*$")

# Regex to match the timestamp line:  Start: (MM:SS.cc) | End: (MM:SS.cc)
_TIMESTAMP_RE = re.compile(
    r"Start:\s*\(([^)]*)\)\s*\|\s*End:\s*\(([^)]*)\)",
    re.IGNORECASE,
)

# Regex to split body into named scenes, keeping "SCENE XX" in the split result
_SCENE_SPLIT_RE = re.compile(r"(?m)^(SCENE\s+\S+)\s*$")

# Regex to extract scene-level header fields
_SCENE_HEADING_RE = re.compile(r"Scene heading:\s*(.+)", re.IGNORECASE)
_SCENE_START_RE = re.compile(r"Scene start:\s*([^\s]+)", re.IGNORECASE)
_SCENE_END_RE = re.compile(r"Scene end:\s*([^\s]+)", re.IGNORECASE)

# Regex to extract character name and optional emotion from a tag like:
#   MATRIARCH (Cold, Commanding)
_CHARACTER_EMOTION_RE = re.compile(r"^(.+?)\s*\(([^)]+)\)\s*$")

# Regex to match episode header fields
_EP_NUMBER_RE = re.compile(r"EPISODE NUMBER:\s*(.+)", re.IGNORECASE)
_EP_LOGLINE_RE = re.compile(r"EPISODE LOGLINE:\s*(.+)", re.IGNORECASE)
_CONTINUITY_RE = re.compile(r"CONTINUITY NOTES:\s*(.+)", re.IGNORECASE)

# Timestamp pattern: MM:SS.cc
_TS_VALUE_RE = re.compile(r"^(\d+):(\d+)(?:\.(\d+))?$")


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------


class TimestampStatus(str, Enum):
    """Indicates whether timestamp data for a block is reliable."""

    AVAILABLE = "available"
    ESTIMATED = "estimated"
    UNAVAILABLE = "unavailable"


class DialogueLine(BaseModel):
    """
    A single character dialogue block extracted from the screenplay.

    Attributes:
        character: The speaking character's name (uppercased).
        emotion:   Optional acting direction in parentheses, e.g. "Cold, Commanding".
        text:      The spoken dialogue, with surrounding quotes stripped.
        start_time: Raw timestamp string from the script, e.g. "00:11.30".
        end_time:   Raw end timestamp string, e.g. "00:13.10".
        start_seconds: start_time converted to total seconds (float).
        end_seconds:   end_time converted to total seconds (float).
        timestamp_status: Whether the timestamp was present and valid.
        line_number: Approximate line number in the original source file (1-based).
    """

    character: str
    emotion: str = ""
    text: str
    start_time: str
    end_time: str
    start_seconds: float
    end_seconds: float
    timestamp_status: TimestampStatus = TimestampStatus.AVAILABLE
    line_number: int


class ActionLine(BaseModel):
    """
    A non-dialogue action/camera/sound block extracted from the screenplay.

    Attributes:
        action_type:  One of "ACTION", "CAMERA", "SOUND FX", etc.
        description:  The free-text content of the block.
        start_time:   Raw start timestamp, e.g. "00:00.00".
        end_time:     Raw end timestamp.
        start_seconds: Converted start time in seconds.
        end_seconds:   Converted end time in seconds.
        timestamp_status: Whether timestamp data was present and valid.
        line_number:  Approximate line number in the original source file.
    """

    action_type: str
    description: str
    start_time: str
    end_time: str
    start_seconds: float
    end_seconds: float
    timestamp_status: TimestampStatus = TimestampStatus.AVAILABLE
    line_number: int


class Scene(BaseModel):
    """
    A single scene parsed from the screenplay body.

    Attributes:
        scene_number:      Two-digit scene identifier, e.g. "01".
        heading:           Scene heading, e.g. "INT. CATHEDRAL – DAY".
        start_time:        Raw scene start timestamp.
        end_time:          Raw scene end timestamp.
        start_seconds:     Scene start in total seconds.
        end_seconds:       Scene end in total seconds.
        duration_seconds:  Computed duration (end - start).
        dialogues:         All dialogue blocks in scene order.
        actions:           All action/camera/sound blocks in scene order.
        characters_present: Unique character names appearing in this scene.
        raw_text:          The original raw text of this scene block.
        parse_errors:      Any non-fatal parse errors encountered (debug).
    """

    scene_number: str
    heading: str
    start_time: str
    end_time: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    dialogues: list[DialogueLine] = Field(default_factory=list)
    actions: list[ActionLine] = Field(default_factory=list)
    characters_present: list[str] = Field(default_factory=list)
    raw_text: str
    parse_errors: list[str] = Field(default_factory=list)

    @property
    def dialogue_lines(self) -> list[DialogueLine]:
        """Convenience alias for dialogues."""
        return self.dialogues


class Episode(BaseModel):
    """
    A fully-parsed episode of the screenplay.

    Attributes:
        episode_label:   The raw label string, e.g. "Episode 1".
        episode_number:  Extracted integer episode number.
        logline:         The episode's one-line story summary.
        continuity_notes: Notes for script continuity.
        filename:        Source filename (without directory).
        scenes:          Ordered list of parsed Scene objects.
        all_characters:  Unique character names across the whole episode.
        total_duration_seconds: Sum of all scene durations.
        total_scenes:    Number of scenes parsed.
        raw_content:     The complete raw text of the source file.
        parse_errors:    Any non-fatal episode-level parse errors.
    """

    episode_label: str
    episode_number: int
    logline: str
    continuity_notes: str
    filename: str
    scenes: list[Scene] = Field(default_factory=list)
    all_characters: list[str] = Field(default_factory=list)
    total_duration_seconds: float
    total_scenes: int
    raw_content: str
    parse_errors: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


def parse_timestamp(ts_str: str) -> float:
    """
    Convert a "MM:SS.cc" timestamp string to total seconds as a float.

    The centiseconds part (cc) represents hundredths of a second, so
    "02:18.50" means 2 minutes, 18 seconds, and 50 centiseconds
    (= 138.50 total seconds).

    Args:
        ts_str: A timestamp string in "MM:SS.cc" format.
                Examples: "00:04.80", "02:18.00", "01:30"

    Returns:
        Total seconds as a float.  Returns 0.0 for any malformed input
        rather than raising an exception, so a bad timestamp never crashes
        the parser.
    """
    if not ts_str or not ts_str.strip():
        return 0.0

    ts_str = ts_str.strip()
    match = _TS_VALUE_RE.match(ts_str)
    if not match:
        logger.debug("parse_timestamp: unrecognised format %r — returning 0.0", ts_str)
        return 0.0

    minutes = int(match.group(1))
    seconds = int(match.group(2))
    # Centiseconds group may be absent
    centiseconds_str = match.group(3) or "0"
    # Pad or truncate to two digits for consistent interpretation
    centiseconds_str = (centiseconds_str + "00")[:2]
    centiseconds = int(centiseconds_str)

    return float(minutes * 60 + seconds) + centiseconds / 100.0


def _extract_timestamps(line: str) -> tuple[str, str, TimestampStatus]:
    """
    Parse a "Start: (MM:SS.cc) | End: (MM:SS.cc)" line.

    Returns:
        (start_str, end_str, status) where status reflects whether both
        values were present and parseable.
    """
    match = _TIMESTAMP_RE.search(line)
    if not match:
        return "00:00.00", "00:00.00", TimestampStatus.UNAVAILABLE

    start_str = match.group(1).strip()
    end_str = match.group(2).strip()

    # Validate they look like timestamps
    status = TimestampStatus.AVAILABLE
    if not _TS_VALUE_RE.match(start_str) or not _TS_VALUE_RE.match(end_str):
        status = TimestampStatus.ESTIMATED

    return start_str, end_str, status


def _is_action_tag(tag: str) -> bool:
    """
    Return True if the tag name belongs to an action/camera/sound block
    rather than a character dialogue block.
    """
    tag_upper = tag.strip().upper()
    if tag_upper in ACTION_TAGS:
        return True
    # Partial match for compound tags like "SOUND FX", "SOUND DESIGN"
    for known in ACTION_TAGS:
        if tag_upper.startswith(known):
            return True
    return False


def _parse_character_tag(tag: str) -> tuple[str, str]:
    """
    Split a character tag into (name, emotion).

    Examples:
        "MATRIARCH (Cold, Commanding)"  -> ("MATRIARCH", "Cold, Commanding")
        "JULIANA"                       -> ("JULIANA", "")
        "NARRATOR (V.O.)"               -> ("NARRATOR", "V.O.")
    """
    match = _CHARACTER_EMOTION_RE.match(tag.strip())
    if match:
        return match.group(1).strip().upper(), match.group(2).strip()
    return tag.strip().upper(), ""


def _clean_dialogue_text(text: str) -> str:
    """
    Strip surrounding double-quotes and extra whitespace from a dialogue line.
    Handles both straight quotes and curly/smart quotes.
    """
    text = text.strip()
    # Remove surrounding straight or curly double-quotes
    text = re.sub(r'^["\u201c\u201d]|["\u201c\u201d]$', "", text).strip()
    return text


# ---------------------------------------------------------------------------
# Core parsing functions
# ---------------------------------------------------------------------------


def extract_episode_header(content: str) -> tuple[str, str, str]:
    """
    Extract the episode header fields from raw screenplay content.

    Looks for lines of the form:
        EPISODE NUMBER: Episode 1
        EPISODE LOGLINE: Some logline text...
        CONTINUITY NOTES: Some notes...

    Multi-line continuation for logline / continuity notes is not currently
    supported (only the first matching line is captured).

    Args:
        content: Full raw text of the screenplay file.

    Returns:
        A 3-tuple of (episode_label, logline, continuity_notes).
        Each element defaults to "" if not found.
    """
    episode_label = ""
    logline = ""
    continuity_notes = ""

    # Only scan the header section (before --- SCRIPT START ---)
    header_section = content
    script_start_idx = content.find("--- SCRIPT START ---")
    if script_start_idx != -1:
        header_section = content[:script_start_idx]

    for line in header_section.splitlines():
        if not episode_label:
            m = _EP_NUMBER_RE.match(line.strip())
            if m:
                episode_label = m.group(1).strip()
        if not logline:
            m = _EP_LOGLINE_RE.match(line.strip())
            if m:
                logline = m.group(1).strip()
        if not continuity_notes:
            m = _CONTINUITY_RE.match(line.strip())
            if m:
                continuity_notes = m.group(1).strip()

    return episode_label, logline, continuity_notes


def _extract_episode_number(episode_label: str) -> int:
    """
    Pull the integer episode number out of a label such as "Episode 1" or
    "Episode 12 – Finale".

    Returns 0 if no number can be found.
    """
    match = re.search(r"\d+", episode_label)
    return int(match.group()) if match else 0


def parse_bold_blocks(
    scene_body: str,
    filename: str,
    line_offset: int = 0,
) -> tuple[list[DialogueLine], list[ActionLine]]:
    """
    Parse all **TAG:** blocks from the body of a single scene.

    Each block has the structure:
        **TAG:**
        Start: (MM:SS.cc) | End: (MM:SS.cc)
        Content text (may be multiple lines)

    The function classifies each block as either a DialogueLine (character
    speaking) or an ActionLine (CAMERA, ACTION, SOUND FX, etc.).

    Args:
        scene_body:   The raw text of the scene body (after the scene header).
        filename:     Source filename, used for logging context only.
        line_offset:  Line number offset to give accurate line numbers in the
                      context of the full original file.

    Returns:
        A 2-tuple of (dialogues, actions).
    """
    dialogues: list[DialogueLine] = []
    actions: list[ActionLine] = []

    lines = scene_body.splitlines()

    # Find all **TAG:** positions, then slice content between them
    block_starts: list[tuple[int, str]] = []  # (line_index, tag_name)
    for idx, line in enumerate(lines):
        m = _BOLD_TAG_RE.match(line.strip())
        if m:
            block_starts.append((idx, m.group(1).strip()))

    for i, (start_idx, tag) in enumerate(block_starts):
        # Content runs from the line after the tag to the line before the next tag
        end_idx = block_starts[i + 1][0] if i + 1 < len(block_starts) else len(lines)
        block_lines = lines[start_idx + 1 : end_idx]

        # First non-empty line should be the timestamp line
        ts_line = ""
        content_lines: list[str] = []
        ts_found = False
        for bl in block_lines:
            stripped = bl.strip()
            if not ts_found and _TIMESTAMP_RE.search(stripped):
                ts_line = stripped
                ts_found = True
            elif stripped:
                content_lines.append(stripped)

        start_str, end_str, ts_status = _extract_timestamps(ts_line)
        start_sec = parse_timestamp(start_str)
        end_sec = parse_timestamp(end_str)
        content_text = " ".join(content_lines).strip()

        # Approximate line number (1-based, in source file)
        source_line = line_offset + start_idx + 1

        if _is_action_tag(tag):
            actions.append(
                ActionLine(
                    action_type=tag.strip().upper(),
                    description=content_text,
                    start_time=start_str,
                    end_time=end_str,
                    start_seconds=start_sec,
                    end_seconds=end_sec,
                    timestamp_status=ts_status,
                    line_number=source_line,
                )
            )
        else:
            char_name, emotion = _parse_character_tag(tag)
            dialogues.append(
                DialogueLine(
                    character=char_name,
                    emotion=emotion,
                    text=_clean_dialogue_text(content_text),
                    start_time=start_str,
                    end_time=end_str,
                    start_seconds=start_sec,
                    end_seconds=end_sec,
                    timestamp_status=ts_status,
                    line_number=source_line,
                )
            )

    return dialogues, actions


def parse_scene_block(
    scene_text: str,
    filename: str,
    scene_num: str,
    line_offset: int = 0,
) -> Scene:
    """
    Parse a single SCENE block into a Scene model.

    The expected block structure is:
        SCENE 01
        Scene heading: INT. CATHEDRAL – DAY
        Scene start: 00:00.00
        Scene end: 02:18.00

        Actions and dialogue:

        **CAMERA:**
        ...

    Args:
        scene_text:  The raw text of the scene block (including the
                     "SCENE XX" header line).
        filename:    Source filename for log context.
        scene_num:   Scene number string (e.g. "01") already extracted by
                     the caller from the split token.
        line_offset: Line number within the source file where this block starts.

    Returns:
        A Scene object.  If the block is malformed, fields fall back to
        defaults and errors are recorded in Scene.parse_errors.
    """
    parse_errors: list[str] = []
    lines = scene_text.splitlines()

    # --- Extract scene-level metadata ---
    heading = ""
    start_time_raw = "00:00.00"
    end_time_raw = "00:00.00"

    for line in lines[:20]:  # Header fields are always near the top
        stripped = line.strip()
        m = _SCENE_HEADING_RE.match(stripped)
        if m and not heading:
            heading = m.group(1).strip()
            continue
        m = _SCENE_START_RE.match(stripped)
        if m and start_time_raw == "00:00.00":
            start_time_raw = m.group(1).strip()
            continue
        m = _SCENE_END_RE.match(stripped)
        if m and end_time_raw == "00:00.00":
            end_time_raw = m.group(1).strip()

    if not heading:
        parse_errors.append(f"Scene {scene_num}: 'Scene heading' not found.")
        heading = f"UNKNOWN SCENE {scene_num}"

    start_sec = parse_timestamp(start_time_raw)
    end_sec = parse_timestamp(end_time_raw)
    duration = max(0.0, end_sec - start_sec)

    # --- Find the body (after "Actions and dialogue:") ---
    body_start = 0
    for idx, line in enumerate(lines):
        if re.match(r"^\s*Actions and dialogue\s*:", line, re.IGNORECASE):
            body_start = idx + 1
            break

    scene_body = "\n".join(lines[body_start:])

    try:
        dialogues, actions = parse_bold_blocks(
            scene_body, filename, line_offset=line_offset + body_start
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "parse_bold_blocks failed for scene %s in %s: %s",
            scene_num,
            filename,
            exc,
        )
        parse_errors.append(
            f"Scene {scene_num}: bold-block parsing failed — {exc}"
        )
        dialogues, actions = [], []

    # Unique characters in scene order
    seen_chars: dict[str, None] = {}
    for dl in dialogues:
        seen_chars[dl.character] = None
    characters_present = list(seen_chars.keys())

    return Scene(
        scene_number=scene_num,
        heading=heading,
        start_time=start_time_raw,
        end_time=end_time_raw,
        start_seconds=start_sec,
        end_seconds=end_sec,
        duration_seconds=duration,
        dialogues=dialogues,
        actions=actions,
        characters_present=characters_present,
        raw_text=scene_text,
        parse_errors=parse_errors,
    )


def parse_episode(episode_file) -> Episode:
    """
    Parse an EpisodeFile object into a fully-structured Episode model.

    The function:
    1. Reads the raw content from episode_file.content.
    2. Extracts the episode header (number, logline, continuity notes).
    3. Splits the script body on "--- SCRIPT START ---" / "--- SCRIPT END ---".
    4. Splits the body on "SCENE XX" markers.
    5. Parses each scene block.
    6. Assembles and returns an Episode.

    Args:
        episode_file: An EpisodeFile instance from file_processor.py with at
                      least the attributes:
                        - filename (str)
                        - content  (str)

    Returns:
        An Episode model populated with all parsed data.

    Raises:
        Does NOT raise.  Any parse failures are logged and recorded in
        Episode.parse_errors / Scene.parse_errors, allowing the pipeline to
        continue with partial data.
    """
    parse_errors: list[str] = []
    filename: str = getattr(episode_file, "filename", "<unknown>")
    raw_content: str = getattr(episode_file, "content", "") or ""

    # --- 1. Extract header ---
    try:
        episode_label, logline, continuity_notes = extract_episode_header(raw_content)
    except Exception as exc:  # noqa: BLE001
        logger.error("extract_episode_header failed for %s: %s", filename, exc)
        parse_errors.append(f"Header extraction failed: {exc}")
        episode_label, logline, continuity_notes = "", "", ""

    episode_number = _extract_episode_number(episode_label)

    # --- 2. Isolate the script body ---
    script_body = ""
    start_marker = "--- SCRIPT START ---"
    end_marker = "--- SCRIPT END ---"

    if start_marker in raw_content:
        after_start = raw_content.split(start_marker, 1)[1]
        if end_marker in after_start:
            script_body = after_start.split(end_marker, 1)[0]
        else:
            script_body = after_start
            parse_errors.append("'--- SCRIPT END ---' marker not found.")
    else:
        # Fallback: treat everything as the body
        script_body = raw_content
        parse_errors.append(
            "'--- SCRIPT START ---' marker not found; treating full content as body."
        )

    # --- 3. Split body into scenes ---
    # _SCENE_SPLIT_RE matches "SCENE XX" on its own line; we keep the token
    # so we know the scene number.
    parts = _SCENE_SPLIT_RE.split(script_body)
    # parts = [pre_scene_preamble, "SCENE 01", scene1_body, "SCENE 02", scene2_body, ...]
    # Tokens at odd indices are the "SCENE XX" labels; even indices are bodies.

    scenes: list[Scene] = []

    if len(parts) < 3:
        # No scene markers found
        parse_errors.append(
            f"No 'SCENE XX' markers found in {filename}. Script body may be empty or malformed."
        )
    else:
        # Walk in pairs: (scene_label, scene_body)
        # parts[0] is preamble before the first SCENE
        for i in range(1, len(parts) - 1, 2):
            scene_label = parts[i].strip()   # e.g. "SCENE 01"
            scene_body_text = parts[i + 1] if i + 1 < len(parts) else ""

            # Extract just the number/identifier portion
            scene_num_match = re.search(r"SCENE\s+(\S+)", scene_label, re.IGNORECASE)
            scene_num = scene_num_match.group(1) if scene_num_match else str(i)

            full_scene_text = scene_label + "\n" + scene_body_text

            # Approximate line offset within the full file
            line_offset = raw_content[: raw_content.find(scene_label)].count("\n")

            try:
                scene = parse_scene_block(
                    full_scene_text, filename, scene_num, line_offset=line_offset
                )
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "parse_scene_block failed for scene %s in %s: %s",
                    scene_num,
                    filename,
                    exc,
                )
                parse_errors.append(
                    f"Scene {scene_num} parse failed entirely: {exc}"
                )
                # Create a minimal stub scene so we don't silently drop it
                scene = Scene(
                    scene_number=scene_num,
                    heading=f"PARSE ERROR — SCENE {scene_num}",
                    start_time="00:00.00",
                    end_time="00:00.00",
                    start_seconds=0.0,
                    end_seconds=0.0,
                    duration_seconds=0.0,
                    dialogues=[],
                    actions=[],
                    characters_present=[],
                    raw_text=full_scene_text,
                    parse_errors=[f"Fatal parse error: {exc}"],
                )
            scenes.append(scene)

    # --- 4. Aggregate episode-level fields ---
    all_chars_seen: dict[str, None] = {}
    for sc in scenes:
        for ch in sc.characters_present:
            all_chars_seen[ch] = None
    all_characters = list(all_chars_seen.keys())

    total_duration = sum(sc.duration_seconds for sc in scenes)

    return Episode(
        episode_label=episode_label or f"Episode {episode_number}",
        episode_number=episode_number,
        logline=logline,
        continuity_notes=continuity_notes,
        filename=filename,
        scenes=scenes,
        all_characters=all_characters,
        total_duration_seconds=total_duration,
        total_scenes=len(scenes),
        raw_content=raw_content,
        parse_errors=parse_errors,
    )


def parse_all_episodes(processing_result) -> list[Episode]:
    """
    Parse every valid EpisodeFile in a ProcessingResult into Episode objects.

    Iterates over processing_result.valid_episodes (a list of EpisodeFile
    objects), calls parse_episode() on each, then returns the list sorted
    by episode_number ascending.

    Args:
        processing_result: A ProcessingResult from file_processor.process_uploaded_files().
                           Must expose a .valid_episodes attribute.

    Returns:
        Sorted list of Episode objects (ascending by episode_number).
        Empty list if no valid episodes exist or the input is None.
    """
    if processing_result is None:
        logger.warning("parse_all_episodes received None — returning empty list.")
        return []

    valid_episodes = getattr(processing_result, "valid_episodes", None)
    if valid_episodes is None:
        valid_episodes = [
            ep for ep in getattr(processing_result, "episodes", [])
            if getattr(ep, "is_valid", False)
        ]
    if not valid_episodes:
        logger.info("parse_all_episodes: no valid episodes to parse.")
        return []

    episodes: list[Episode] = []
    for ep_file in valid_episodes:
        filename = getattr(ep_file, "filename", "<unknown>")
        try:
            episode = parse_episode(ep_file)
            episodes.append(episode)
            logger.info(
                "Parsed %s — %d scene(s), %d character(s), %.1fs total.",
                filename,
                episode.total_scenes,
                len(episode.all_characters),
                episode.total_duration_seconds,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to parse episode %s: %s", filename, exc)

    episodes.sort(key=lambda ep: ep.episode_number)
    return episodes
