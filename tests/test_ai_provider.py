"""
test_ai_provider.py — Unit Tests for AI Provider Error Handling & Demo Mode

Tests missing API key handling, demo mode fallbacks, and API failure handling using mocks.
No live API keys or paid network calls are required.
"""

from unittest.mock import MagicMock, patch
import pytest
from src.ai.base_provider import ProviderStatus
from src.ai.gemini_provider import GeminiProvider, generate_demo_promos, generate_demo_analysis


def test_missing_api_key_returns_demo_mode():
    """Provider without an API key gracefully returns demo mode response."""
    provider = GeminiProvider(api_key="")
    response = provider.generate_promo_candidates([])
    assert response.success
    assert response.is_demo
    assert response.status == ProviderStatus.DEMO_MODE
    assert "promos" in response.data


def test_missing_api_key_episode_analysis_demo():
    """Provider without API key generates synthetic episode analysis."""
    provider = GeminiProvider(api_key="")
    response = provider.analyze_episode("Sample content", "Episode 1")
    assert response.success
    assert response.is_demo
    assert response.data["episode_label"] == "Episode 1"
    assert len(response.data["main_characters"]) > 0


def test_health_check_no_key():
    """Health check without key informs user that demo mode will be used."""
    provider = GeminiProvider(api_key="")
    is_ok, msg = provider.health_check()
    assert not is_ok
    assert "demo mode" in msg.lower() or "not set" in msg.lower()


def test_api_failure_handled_gracefully(monkeypatch):
    """Network or API exceptions are caught and classified into clean error status."""
    provider = GeminiProvider(api_key="fake_key_12345")

    # Mock _get_client to raise an exception simulating API failure
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("403 Forbidden: API key expired or quota reached")
    monkeypatch.setattr(provider, "_get_client", lambda: mock_client)

    response = provider._call_api("test prompt")
    assert not response.success
    assert response.error != ""
    assert response.status in {ProviderStatus.API_KEY_INVALID, ProviderStatus.QUOTA_EXCEEDED, ProviderStatus.RESPONSE_ERROR}


def test_malformed_json_response_handled(monkeypatch):
    """When LLM returns invalid non-JSON string, returns error status without crashing."""
    provider = GeminiProvider(api_key="fake_key_12345")

    mock_resp = MagicMock()
    mock_resp.text = "Here is your analysis: { this is totally invalid json [ broken "
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = mock_resp
    monkeypatch.setattr(provider, "_get_client", lambda: mock_client)

    response = provider._call_api("test prompt")
    assert not response.success
    assert "json" in response.error.lower() or response.status == ProviderStatus.RESPONSE_ERROR
