"""Configuration behavior tests."""

from app.core.config import Settings


def test_settings_parse_cors_origins() -> None:
    """Comma-delimited configuration is normalized into immutable origins."""
    settings = Settings(CORS_ORIGINS="https://one.example, https://two.example")

    assert settings.cors_origins == ("https://one.example", "https://two.example")
