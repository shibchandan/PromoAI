"""
test_file_processor.py — Unit Tests for File Processing Module

Tests TXT upload, ZIP extraction, path traversal security, and validation.
"""

import io
import zipfile
import pytest
from src.file_processor import (
    validate_file_extension,
    validate_file_content,
    extract_episode_label,
    process_txt_files,
    process_zip_file,
    process_uploaded_files,
    EpisodeFile,
    ProcessingResult,
)


def test_valid_txt_file_accepted(sample_screenplay_text):
    """A valid TXT file with script markers must be accepted."""
    files = [("episode-001.txt", sample_screenplay_text.encode("utf-8"))]
    result = process_txt_files(files)
    assert result.successful_count == 1
    assert len(result.errors) == 0
    ep = result.episodes[0]
    assert ep.is_valid
    assert ep.episode_label == "Episode 1"


def test_invalid_extension_rejected():
    """Non-TXT files like PDF or MP4 must be rejected."""
    assert not validate_file_extension("script.pdf")
    assert not validate_file_extension("screenplay.docx")
    assert validate_file_extension("episode-01.txt")


def test_empty_file_rejected():
    """An empty file must be flagged as invalid."""
    is_valid, err = validate_file_content("", "empty.txt")
    assert not is_valid
    assert "empty" in err.lower()


def test_missing_script_markers_rejected():
    """Files without SCRIPT START marker must be flagged."""
    content = "Some random text that is sufficiently long to exceed one hundred characters in total length, but does not have the screenplay markers at all."
    is_valid, err = validate_file_content(content, "bad.txt")
    assert not is_valid
    assert "marker" in err.lower()


def test_zip_extraction_valid(sample_screenplay_text):
    """A ZIP file with valid screenplay TXT files must be extracted safely."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ep1.txt", sample_screenplay_text)
        zf.writestr("ep2.txt", sample_screenplay_text.replace("Episode 1", "Episode 2"))
    
    zip_bytes = zip_buffer.getvalue()
    result = process_zip_file(("screenplays.zip", zip_bytes))
    assert result.successful_count == 2
    assert len(result.errors) == 0
    labels = [ep.episode_label for ep in result.episodes]
    assert "Episode 1" in labels
    assert "Episode 2" in labels


def test_zip_path_traversal_blocked(sample_screenplay_text):
    """Zip slip / path traversal attempts must be rejected."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("../evil.txt", sample_screenplay_text)
        zf.writestr("valid.txt", sample_screenplay_text)
    
    zip_bytes = zip_buffer.getvalue()
    result = process_zip_file(("attack.zip", zip_bytes))
    # valid.txt should succeed, ../evil.txt should be blocked or warned
    assert any("traversal" in err.lower() or "suspicious" in err.lower() or "skipped" in err.lower() for err in result.errors) or result.successful_count == 1


def test_zip_executable_skipped(sample_screenplay_text):
    """Non-TXT files inside a ZIP must be skipped."""
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("malware.exe", b"fake binary")
        zf.writestr("valid.txt", sample_screenplay_text)
    
    zip_bytes = zip_buffer.getvalue()
    result = process_zip_file(("mixed.zip", zip_bytes))
    assert result.successful_count == 1
    assert result.episodes[0].filename == "valid.txt"


def test_corrupted_zip_handled():
    """Corrupted ZIP files should not crash the application."""
    bad_bytes = b"NOT_A_REAL_ZIP_FILE_DATA_CORRUPT"
    result = process_zip_file(("broken.zip", bad_bytes))
    assert result.successful_count == 0
    assert len(result.errors) > 0


def test_multiple_txt_files(sample_screenplay_text):
    """Processing multiple TXT files should return all valid ones."""
    files = [
        ("ep1.txt", sample_screenplay_text.encode("utf-8")),
        ("ep2.txt", sample_screenplay_text.replace("Episode 1", "Episode 2").encode("utf-8")),
    ]
    result = process_uploaded_files(files)
    assert result.successful_count == 2


def test_episode_label_extracted_from_header():
    """Label is extracted from 'EPISODE NUMBER: Episode 42'."""
    text = "EPISODE NUMBER: Episode 42\n--- SCRIPT START ---\n"
    label = extract_episode_label("random_filename.txt", text)
    assert label == "Episode 42"
