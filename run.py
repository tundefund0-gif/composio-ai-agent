#!/usr/bin/env python3
"""Zen Agent — Unified launcher (CLI or Web)."""
from __future__ import annotations

import os
import sys

# Ensure API keys are loaded from environment early
REQUIRED_KEYS = {
    "OPENGATE_API_KEY": "OpenCode/OpenAI API key",
    "COMPOSIO_API_KEY": "Composio API key",
}

def main():
    # Warn about missing keys but don't block
    for key, desc in REQUIRED_KEYS.items():
        if not os.environ.get(key):
            print(f"⚠️  Warning: {key} ({desc}) not set. Things may not work.", file=sys.stderr)

    mode = sys.argv[1] if len(sys.argv) > 1 else "web"
    sys.argv = [sys.argv[0]] + sys.argv[2:]

    if mode == "cli" or mode == "chat":
        from cli.main import app as typer_app
        typer_app()
    elif mode == "web" or mode == "server":
        import uvicorn
        from config import config
        print(f"🚀 Zen Agent — http://localhost:{config.port}")
        uvicorn.run("server.main:app", host=config.host, port=config.port, log_level="info")
    else:
        print(f"Usage: {sys.argv[0]} [web|cli] [args]")
        sys.exit(1)


if __name__ == "__main__":
    main()
