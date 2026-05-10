import os

from pathlib import Path

from dotenv import load_dotenv

ENABLE_STREAMLIT = False

# =========================
# PROJECT ROOT
# =========================

BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

PROJECT_ROOT = (
    BASE_DIR.parent
)

# =========================
# LOAD ENV FILE
# =========================

load_dotenv(
    PROJECT_ROOT / ".env"
)

# =========================
# RUNTIME DATA
# =========================

RUNTIME_DATA_DIR = (
    BASE_DIR / "runtime_data"
)

# =========================
# OPENROUTER CONFIG
# =========================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_MODEL = (
    "deepseek/deepseek-chat"
)