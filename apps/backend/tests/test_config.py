from app.core.config import Settings


def test_cors_default_is_wildcard():
    assert Settings(cors_origins="*").cors_origins_list == ["*"]


def test_cors_empty_is_wildcard():
    assert Settings(cors_origins="").cors_origins_list == ["*"]


def test_cors_parses_comma_separated_list():
    settings = Settings(cors_origins="https://a.example, https://b.example")
    assert settings.cors_origins_list == ["https://a.example", "https://b.example"]


def test_cors_strips_blank_entries():
    settings = Settings(cors_origins="https://a.example, ,https://b.example,")
    assert settings.cors_origins_list == ["https://a.example", "https://b.example"]


def test_database_url_sync_upgrades_driver():
    settings = Settings(database_url="postgresql://u:p@host:5432/db")
    assert settings.database_url_sync.startswith("postgresql+psycopg://")
