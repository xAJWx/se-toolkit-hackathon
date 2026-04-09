"""Configuration loading from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from environment variables.

    Looks for .env.secret in the project root, falling back to .env.example.
    """
    project_dir = Path(__file__).parent.parent

    # Try secret file first, then example
    secret_file = project_dir / ".env.secret"
    example_file = project_dir / ".env.example"

    if secret_file.exists():
        load_dotenv(secret_file, override=True)
    elif example_file.exists():
        load_dotenv(example_file, override=True)

    return {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "POSTGRES_USER": os.getenv("POSTGRES_USER", "remindme"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "remindme_password"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB", "remindme"),
        "POSTGRES_HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "5432"),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_BASE_URL": os.getenv("LLM_API_BASE_URL", "https://openrouter.ai/api/v1"),
    }


def get_dsn(config: dict[str, str]) -> str:
    """Build PostgreSQL DSN from config."""
    return (
        f"postgresql://{config['POSTGRES_USER']}:{config['POSTGRES_PASSWORD']}"
        f"@{config['POSTGRES_HOST']}:{config['POSTGRES_PORT']}/{config['POSTGRES_DB']}"
    )
