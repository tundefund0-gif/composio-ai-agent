"""Application configuration — environment variables with .env support."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


def _load_dotenv():
    """Load .env file if present (lightweight, no dependency)."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.isfile(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip()
                # Remove surrounding quotes if present
                if len(val) > 1 and val[0] == val[-1] and val[0] in ('"', "'"):
                    val = val[1:-1]
                if key not in os.environ:  # Don't override already-set env vars
                    os.environ[key] = val


_load_dotenv()


@dataclass
class Config:
    opencode_api_key: str = field(default_factory=lambda: os.getenv("OPENGATE_API_KEY", ""))
    opencode_base_url: str = field(default_factory=lambda: os.getenv("OPENGATE_BASE_URL", "https://opencode.ai/zen/v1"))
    opencode_model: str = field(default_factory=lambda: os.getenv("OPENGATE_MODEL", "deepseek-v4-flash-free"))
    opencode_max_tokens: int = 131000
    composio_api_key: str = field(default_factory=lambda: os.getenv("COMPOSIO_API_KEY", ""))
    composio_base_url: str = field(default_factory=lambda: os.getenv("COMPOSIO_BASE_URL", "https://backend.composio.dev"))
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "9090")))


config = Config()
