"""
config.py — Application Configuration

This module loads all application settings from environment variables.
Using python-dotenv means .env file values are auto-loaded.
Pydantic BaseSettings ensures type checking and validation at startup.

Why not hardcode values?
- API keys must stay secret (never commit to git)
- Settings should be adjustable without code changes
- Different environments (dev/prod) need different values
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
load_dotenv()

# --- Path Definitions ---
# BASE_DIR is the project root (one level up from src/)
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input" / "screenplay"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- AI Settings ---
def get_gemini_api_key() -> str:
    """Retrieve the Gemini API key, reloading .env if needed."""
    key = os.getenv("GEMINI_API_KEY", "")
    if not key or key == "your_gemini_api_key_here":
        load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
        key = os.getenv("GEMINI_API_KEY", "")
    return key


def get_gemini_model() -> str:
    """Retrieve the configured Gemini model."""
    load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)
    return os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")


def save_gemini_api_key(new_key: str) -> None:
    """Save API key to environment and update .env file."""
    os.environ["GEMINI_API_KEY"] = new_key.strip()
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        if "GEMINI_API_KEY=" in content:
            import re
            content = re.sub(r"GEMINI_API_KEY=.*", f"GEMINI_API_KEY={new_key.strip()}", content)
        else:
            content += f"\nGEMINI_API_KEY={new_key.strip()}\n"
        env_path.write_text(content, encoding="utf-8")
    else:
        env_path.write_text(f"GEMINI_API_KEY={new_key.strip()}\nGEMINI_MODEL=gemini-3.1-flash-lite\n", encoding="utf-8")


GEMINI_API_KEY: str = get_gemini_api_key()
GEMINI_MODEL: str = get_gemini_model()

# Fallback models for resilience during high-traffic hackathons
FALLBACK_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-2.5-pro",
]

# --- App Mode ---
# "demo" mode uses synthetic responses when API key is missing
APP_MODE: str = os.getenv("APP_MODE", "production")

# --- Analysis Settings ---
MAX_EPISODES_PER_ANALYSIS: int = int(os.getenv("MAX_EPISODES_PER_ANALYSIS", "50"))

# Scoring weights (must sum to 1.0)
# As defined in the PRD scoring formula:
# S = 0.25H + 0.20E + 0.25C + 0.15K + 0.15P
SCORING_WEIGHTS = {
    "hook_strength": 0.25,
    "emotional_impact": 0.20,
    "cliffhanger_strength": 0.25,
    "story_coherence": 0.15,
    "promo_suitability": 0.15,
}

# Promo duration constraints (seconds)
PROMO_MIN_DURATION: int = 20
PROMO_MAX_DURATION: int = 60

# Average reading/speaking speed for duration estimation
# ~125 words per minute in dramatic dialogue
WORDS_PER_MINUTE: int = 125

# Log level
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


def is_api_key_configured() -> bool:
    """
    Check whether a Gemini API key has been provided.
    Returns True if the key looks valid (non-empty, not the placeholder).
    """
    key = get_gemini_api_key()
    return bool(key and key != "your_gemini_api_key_here")


def get_app_mode() -> str:
    """
    Determine effective app mode.
    Forces 'demo' mode if no API key is configured.
    """
    if not is_api_key_configured():
        return "demo"
    return APP_MODE
