"""
file_processor.py — Episode File Processing Module for PromoAI

This module handles all aspects of ingesting screenplay files uploaded by the user.
It supports two upload modes:
  1. Direct .txt upload — one or more individual screenplay files
  2. ZIP upload — a zip archive containing multiple .txt screenplay files

Design principles:
  - Never crash on bad input; always return structured errors instead
  - Validate at every boundary (extension, content markers, path safety)
  - Use only Python stdlib: zipfile, io, pathlib, re, dataclasses
  - Accept both Streamlit UploadedFile objects and plain (filename, bytes) tuples
    so this module is fully testable without a running Streamlit session

Screenplay file format expected:
    EPISODE NUMBER: Episode 1
    EPISODE LOGLINE: ...
    CONTINUITY NOTES: ...
    --- SCRIPT START ---
    SCENE 01
    Scene heading: INT. CATHEDRAL – DAY
    ...
    --- SCRIPT END ---

Filename pattern: episode-001-Episode 1671703.txt
"""

import io
import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# The sentinel marker that every valid screenplay file must contain.
SCRIPT_START_MARKER = "--- SCRIPT START ---"

# Minimum content length (chars) to be considered a non-trivial file.
MIN_CONTENT_LENGTH = 100

# Maximum number of files we will extract from a single ZIP archive.
# This guards against "ZIP bombs" and runaway processing loops.
MAX_FILES_IN_ZIP = 100

# Dangerous executable extensions that must never be extracted from a ZIP.
BLOCKED_EXTENSIONS = {
    ".exe", ".sh", ".bat", ".cmd", ".ps1", ".py", ".js",
    ".vbs", ".dll", ".so", ".dylib", ".msi", ".jar",
}

# Regex to parse the canonical episode label from file content.
# Matches lines like: "EPISODE NUMBER: Episode 1" or "EPISODE NUMBER: Episode 42"
_CONTENT_EPISODE_RE = re.compile(
    r"EPISODE\s+NUMBER\s*:\s*(Episode\s+\d+)", re.IGNORECASE
)

# Regex to extract the episode label from the filename pattern:
# episode-001-Episode 1671703.txt  →  "Episode 1671703"
# We capture the human-readable "Episode XXXXXXX" portion.
_FILENAME_EPISODE_RE = re.compile(
    r"episode-\d{3}-?(Episode\s+\S+)", re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class EpisodeFile:
    """
    Represents a single successfully (or unsuccessfully) processed screenplay file.

    Fields:
        filename        — original upload filename, e.g. "episode-001-Episode 1671703.txt"
        episode_label   — human-readable episode identifier, e.g. "Episode 1"
        content         — full decoded text content of the file
        file_size_bytes — size of the raw byte payload
        is_valid        — True if the file passed all validation checks
        error_message   — non-empty string explaining why is_valid is False
    """
    filename: str
    episode_label: str
    content: str
    file_size_bytes: int
    is_valid: bool
    error_message: str = ""


@dataclass
class ProcessingResult:
    """
    Aggregated outcome of a file-processing run.

    Fields:
        episodes              — list of EpisodeFile objects (valid and invalid)
        errors                — top-level errors that prevented processing of an
                                entire upload (e.g. corrupt ZIP); per-file errors
                                live inside each EpisodeFile.error_message
        total_files_attempted — how many files we tried to process
        successful_count      — how many files passed all validation checks
    """
    episodes: list = field(default_factory=list)          # list[EpisodeFile]
    errors: list = field(default_factory=list)             # list[str]
    total_files_attempted: int = 0
    successful_count: int = 0

    @property
    def valid_episodes(self) -> list:
        """Return only valid EpisodeFile objects."""
        return [ep for ep in self.episodes if getattr(ep, "is_valid", False)]


# ---------------------------------------------------------------------------
# Helper: normalise an UploadedFile or (filename, bytes) tuple
# ---------------------------------------------------------------------------

def _unpack_file(uploaded_file) -> tuple[str, bytes]:
    """
    Normalise a file argument into a (filename, raw_bytes) pair.

    Accepts:
      - Streamlit UploadedFile  — has .name and .read() / .getvalue()
      - (filename, bytes) tuple — used in unit tests and batch pipelines

    Raises:
        TypeError if the argument is neither of the above.
    """
    if isinstance(uploaded_file, tuple):
        # Test/batch path: (filename_str, bytes_object)
        filename, raw_bytes = uploaded_file
        return str(filename), bytes(raw_bytes)

    # Streamlit UploadedFile path.
    # .getvalue() is preferred over .read() because it is idempotent
    # (calling it multiple times returns the same bytes without rewinding).
    if hasattr(uploaded_file, "getvalue"):
        return uploaded_file.name, uploaded_file.getvalue()

    if hasattr(uploaded_file, "read"):
        return uploaded_file.name, uploaded_file.read()

    raise TypeError(
        f"Cannot unpack file argument of type {type(uploaded_file).__name__}. "
        "Expected a Streamlit UploadedFile or a (filename, bytes) tuple."
    )


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------

def validate_file_extension(filename: str) -> bool:
    """
    Return True only if the filename ends with the .txt extension.

    Why so strict?
      PromoAI only understands plain-text screenplay files.  Accepting .docx,
      .pdf, etc. would silently produce garbage output downstream, so we
      reject them early with a clear error rather than failing mysteriously
      inside the AI analysis step.

    Args:
        filename: The original upload filename (may include path components).

    Returns:
        True  — extension is ".txt" (case-insensitive)
        False — any other extension, or no extension at all
    """
    return Path(filename).suffix.lower() == ".txt"


def validate_file_content(content: str, filename: str) -> tuple[bool, str]:
    """
    Inspect the decoded text of a screenplay file for minimum quality gates.

    Checks (in order):
      1. Not empty
      2. At least MIN_CONTENT_LENGTH characters (guards against stub files)
      3. Contains the SCRIPT_START_MARKER sentinel

    Args:
        content:  Decoded text content of the file.
        filename: Filename used only in error messages.

    Returns:
        (True, "")                    — file passes all checks
        (False, human_readable_error) — file fails at least one check
    """
    # Gate 1: empty check
    if not content or not content.strip():
        return False, f"'{filename}' is empty."

    # Gate 2: minimum length
    if len(content) < MIN_CONTENT_LENGTH:
        return False, (
            f"'{filename}' is too short ({len(content)} chars). "
            f"Expected at least {MIN_CONTENT_LENGTH} chars for a valid screenplay."
        )

    # Gate 3: script marker — proves this is a PromoAI-formatted screenplay
    if SCRIPT_START_MARKER not in content:
        return False, (
            f"'{filename}' is missing the '{SCRIPT_START_MARKER}' marker. "
            "This does not appear to be a PromoAI screenplay file."
        )

    return True, ""


# ---------------------------------------------------------------------------
# Episode label extraction
# ---------------------------------------------------------------------------

def extract_episode_label(filename: str, content: str) -> str:
    """
    Determine a human-readable episode label for a file.

    Strategy (most-reliable first):
      1. Parse "EPISODE NUMBER: Episode X" from the file content.
         This is the canonical source of truth written by the showrunner.
      2. Extract "Episode XXXXXXX" from the filename pattern
         "episode-NNN-Episode XXXXXXX.txt".
      3. Fall back to the filename stem (everything before the last dot).
         This always succeeds, ensuring we never return an empty string.

    Args:
        filename: Original filename, e.g. "episode-001-Episode 1671703.txt"
        content:  Full decoded text of the file.

    Returns:
        A non-empty string label, e.g. "Episode 1" or "Episode 1671703".
    """
    # --- Strategy 1: parse from content header ---
    match = _CONTENT_EPISODE_RE.search(content)
    if match:
        # group(1) captures the matched "Episode X" string
        return match.group(1).strip()

    # --- Strategy 2: parse from filename ---
    match = _FILENAME_EPISODE_RE.search(filename)
    if match:
        return match.group(1).strip()

    # --- Strategy 3: filename stem fallback ---
    # Path().stem strips the extension; e.g. "episode-001-Episode 1671703.txt"
    # becomes "episode-001-Episode 1671703".
    stem = Path(filename).stem
    return stem if stem else filename


# ---------------------------------------------------------------------------
# Processing: individual .txt files
# ---------------------------------------------------------------------------

def process_txt_files(uploaded_files: list) -> ProcessingResult:
    """
    Process a list of uploaded .txt screenplay files.

    Each element may be a Streamlit UploadedFile or a (filename, bytes) tuple.
    Files that fail validation are still added to the result with is_valid=False
    so the UI can show per-file error feedback.

    Args:
        uploaded_files: List of files to process.

    Returns:
        A ProcessingResult with one EpisodeFile per input file.
    """
    result = ProcessingResult()

    for uploaded_file in uploaded_files:
        result.total_files_attempted += 1

        # --- Unpack to (filename, raw_bytes) ---
        try:
            filename, raw_bytes = _unpack_file(uploaded_file)
        except (TypeError, ValueError) as exc:
            # Cannot even get the filename; record as a top-level error.
            result.errors.append(f"Could not read file: {exc}")
            continue

        # --- Extension check ---
        if not validate_file_extension(filename):
            result.episodes.append(EpisodeFile(
                filename=filename,
                episode_label=Path(filename).stem,
                content="",
                file_size_bytes=len(raw_bytes),
                is_valid=False,
                error_message=(
                    f"'{filename}' has an unsupported extension "
                    f"('{Path(filename).suffix}'). Only .txt files are accepted."
                ),
            ))
            continue

        # --- Decode bytes to text ---
        # We try UTF-8 first (most common), then fall back to latin-1
        # which never fails (every byte is valid latin-1).
        try:
            content = raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content = raw_bytes.decode("latin-1")
            except Exception as exc:
                result.episodes.append(EpisodeFile(
                    filename=filename,
                    episode_label=Path(filename).stem,
                    content="",
                    file_size_bytes=len(raw_bytes),
                    is_valid=False,
                    error_message=f"'{filename}' could not be decoded as text: {exc}",
                ))
                continue

        # --- Content validation ---
        is_valid, error_msg = validate_file_content(content, filename)

        # --- Episode label extraction ---
        episode_label = extract_episode_label(filename, content)

        episode = EpisodeFile(
            filename=filename,
            episode_label=episode_label,
            content=content,
            file_size_bytes=len(raw_bytes),
            is_valid=is_valid,
            error_message=error_msg,
        )
        result.episodes.append(episode)

        if is_valid:
            result.successful_count += 1

    return result


# ---------------------------------------------------------------------------
# Processing: ZIP archive
# ---------------------------------------------------------------------------

def process_zip_file(uploaded_file) -> ProcessingResult:
    """
    Extract and process .txt screenplay files from a ZIP archive.

    Security controls applied:
      - Validates the payload is a real ZIP (magic bytes check via zipfile).
      - Rejects any member whose name contains ".." (path traversal attack).
      - Rejects any member with an absolute path (starts with "/" or drive letter).
      - Rejects members with blocked extensions (.exe, .sh, .bat, etc.).
      - Caps extraction at MAX_FILES_IN_ZIP members total.

    Ordering:
      Extracted .txt filenames are sorted alphabetically before processing.
      Because the naming convention is "episode-NNN-…", alphabetic sort equals
      episode order, which is the display order the UI expects.

    Args:
        uploaded_file: Streamlit UploadedFile, raw bytes, or (filename, bytes) tuple.

    Returns:
        ProcessingResult aggregating all extracted files.
    """
    result = ProcessingResult()

    # --- Unpack to raw bytes ---
    try:
        if isinstance(uploaded_file, (bytes, bytearray)):
            zip_bytes = bytes(uploaded_file)
            zip_name = "<zip>"
        else:
            zip_name, zip_bytes = _unpack_file(uploaded_file)
    except (TypeError, ValueError) as exc:
        result.errors.append(f"Could not read ZIP file: {exc}")
        return result

    # --- Validate it is actually a ZIP ---
    # zipfile.is_zipfile() reads the magic bytes; wrapping in BytesIO
    # lets us pass raw bytes without writing a temp file.
    zip_buffer = io.BytesIO(zip_bytes)
    if not zipfile.is_zipfile(zip_buffer):
        result.errors.append(
            f"'{zip_name}' is not a valid ZIP archive "
            "(or it is password-protected / corrupted)."
        )
        return result

    # Rewind so ZipFile can read the central directory from the start.
    zip_buffer.seek(0)

    try:
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            # Collect all member names for security scanning BEFORE extraction.
            all_members = zf.namelist()

            # --- File count limit ---
            if len(all_members) > MAX_FILES_IN_ZIP:
                result.errors.append(
                    f"ZIP archive contains {len(all_members)} files, "
                    f"which exceeds the limit of {MAX_FILES_IN_ZIP}. "
                    "Please split the archive into smaller batches."
                )
                return result

            # --- Collect valid .txt member names, skipping dangerous entries ---
            txt_members: list[str] = []

            for member_name in all_members:
                # Security: block path traversal (e.g. "../../etc/passwd")
                if ".." in member_name:
                    result.errors.append(
                        f"ZIP member '{member_name}' contains '..' — "
                        "rejected (path traversal risk)."
                    )
                    continue

                # Security: block absolute paths (Unix "/" or Windows "C:/")
                # posixpath and ntpath both flag these patterns.
                if member_name.startswith("/") or (
                    len(member_name) >= 2 and member_name[1] == ":"
                ):
                    result.errors.append(
                        f"ZIP member '{member_name}' has an absolute path — "
                        "rejected (path traversal risk)."
                    )
                    continue

                # Skip directories (they end with "/" and have no file content).
                if member_name.endswith("/"):
                    continue

                # Determine the base filename for extension checking.
                # ZIP members can be nested: "subdir/episode-001.txt"
                base_name = Path(member_name).name
                suffix = Path(base_name).suffix.lower()

                # Security: reject blocked executable extensions
                if suffix in BLOCKED_EXTENSIONS:
                    result.errors.append(
                        f"ZIP member '{member_name}' has a blocked extension "
                        f"('{suffix}'). Skipping for security."
                    )
                    continue

                # Only process .txt files; silently skip everything else
                # (images, PDFs, __MACOSX metadata, etc.).
                if suffix != ".txt":
                    continue

                txt_members.append(member_name)

            # --- Sort by member name to preserve episode order ---
            # episode-001-… sorts before episode-002-… alphabetically.
            txt_members.sort()

            # --- Process each .txt member ---
            for member_name in txt_members:
                result.total_files_attempted += 1

                # Use the base filename as the logical filename so that
                # nested paths like "season1/episode-001.txt" show up
                # as "episode-001.txt" everywhere in the UI.
                base_name = Path(member_name).name

                try:
                    raw_bytes = zf.read(member_name)
                except Exception as exc:
                    # Read failure (e.g. CRC error, encrypted entry)
                    result.errors.append(
                        f"Could not read '{member_name}' from ZIP: {exc}"
                    )
                    # Still increment so total_files_attempted is accurate.
                    result.episodes.append(EpisodeFile(
                        filename=base_name,
                        episode_label=Path(base_name).stem,
                        content="",
                        file_size_bytes=0,
                        is_valid=False,
                        error_message=f"Failed to read from ZIP archive: {exc}",
                    ))
                    continue

                # --- Decode bytes to text ---
                try:
                    content = raw_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    content = raw_bytes.decode("latin-1")

                # --- Content validation ---
                is_valid, error_msg = validate_file_content(content, base_name)

                # --- Episode label ---
                episode_label = extract_episode_label(base_name, content)

                episode = EpisodeFile(
                    filename=base_name,
                    episode_label=episode_label,
                    content=content,
                    file_size_bytes=len(raw_bytes),
                    is_valid=is_valid,
                    error_message=error_msg,
                )
                result.episodes.append(episode)

                if is_valid:
                    result.successful_count += 1

    except zipfile.BadZipFile as exc:
        # ZipFile constructor itself can raise BadZipFile on corrupt archives.
        result.errors.append(f"ZIP archive is corrupt or unreadable: {exc}")

    return result


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------

def process_uploaded_files(uploaded_files: list) -> ProcessingResult:
    """
    Main entry point: route uploaded files to the appropriate processor.

    Handles mixed uploads gracefully:
      - .txt files   → process_txt_files()
      - .zip files   → process_zip_file()  (one ZIP at a time)
      - other types  → recorded as invalid EpisodeFile entries

    After all files are processed the combined episodes list is sorted by
    episode_label so the UI always displays episodes in a logical order.

    Args:
        uploaded_files: List of Streamlit UploadedFile objects or
                        (filename, bytes) tuples (mixed is fine).

    Returns:
        A single merged ProcessingResult covering all uploads.
    """
    # Accumulate everything into one master result.
    merged = ProcessingResult()

    # Separate the uploads by type so we can batch .txt files together
    # and process each ZIP individually.
    txt_files: list = []
    zip_files: list = []
    other_files: list = []

    for uploaded_file in uploaded_files:
        try:
            filename, _ = _unpack_file(uploaded_file)
        except (TypeError, ValueError) as exc:
            merged.errors.append(f"Could not inspect file: {exc}")
            merged.total_files_attempted += 1
            continue

        suffix = Path(filename).suffix.lower()
        if suffix == ".txt":
            txt_files.append(uploaded_file)
        elif suffix == ".zip":
            zip_files.append(uploaded_file)
        else:
            other_files.append((filename, suffix))

    # --- Reject unsupported file types upfront ---
    for filename, suffix in other_files:
        merged.total_files_attempted += 1
        merged.episodes.append(EpisodeFile(
            filename=filename,
            episode_label=Path(filename).stem,
            content="",
            file_size_bytes=0,
            is_valid=False,
            error_message=(
                f"'{filename}' has an unsupported type ('{suffix}'). "
                "Please upload .txt screenplay files or a .zip archive."
            ),
        ))

    # --- Process .txt files as a batch ---
    if txt_files:
        txt_result = process_txt_files(txt_files)
        _merge_results(merged, txt_result)

    # --- Process each ZIP individually ---
    for zip_file in zip_files:
        zip_result = process_zip_file(zip_file)
        _merge_results(merged, zip_result)

    # --- Sort all episodes by episode_label for consistent display order ---
    # Natural sort: "Episode 1" < "Episode 2" < "Episode 10"
    # We extract any trailing integer for numeric comparison; fall back to
    # lexicographic order for labels without a trailing number.
    def _sort_key(ep: EpisodeFile) -> tuple:
        """Return (numeric_part, full_label) for natural episode ordering."""
        m = re.search(r"(\d+)\s*$", ep.episode_label)
        numeric = int(m.group(1)) if m else 0
        return (numeric, ep.episode_label.lower())

    merged.episodes.sort(key=_sort_key)

    return merged


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _merge_results(target: ProcessingResult, source: ProcessingResult) -> None:
    """
    Merge `source` into `target` in-place.

    Used by process_uploaded_files to combine results from multiple
    sub-processors into one unified ProcessingResult.
    """
    target.episodes.extend(source.episodes)
    target.errors.extend(source.errors)
    target.total_files_attempted += source.total_files_attempted
    target.successful_count += source.successful_count
