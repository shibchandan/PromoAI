"""
base_provider.py — Abstract AI Provider Interface

Separating the AI provider from business logic means:
1. We can swap Gemini for another LLM without changing business logic
2. We can mock the provider in tests without real API calls
3. Each provider handles its own error patterns
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ProviderStatus(str, Enum):
    OK = "ok"
    API_KEY_MISSING = "api_key_missing"
    API_KEY_INVALID = "api_key_invalid"
    QUOTA_EXCEEDED = "quota_exceeded"
    NETWORK_ERROR = "network_error"
    RESPONSE_ERROR = "response_error"
    DEMO_MODE = "demo_mode"


@dataclass
class AIResponse:
    success: bool
    data: dict  # parsed JSON response
    raw_text: str = ""
    error: str = ""
    status: ProviderStatus = ProviderStatus.OK
    is_demo: bool = False  # True when this is synthetic demo data


class BaseAIProvider(ABC):
    @abstractmethod
    def analyze_episode(self, episode_content: str, episode_label: str) -> AIResponse:
        """Analyze a single episode and return structured analysis."""
        pass

    @abstractmethod
    def generate_promo_candidates(self, episodes_summary: list[dict]) -> AIResponse:
        """Generate promo candidates from episode summaries."""
        pass

    @abstractmethod
    def health_check(self) -> tuple[bool, str]:
        """Check if the provider is accessible. Returns (is_ok, message)."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        pass
