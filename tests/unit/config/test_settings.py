from camp_match.config.settings import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.app_name == "Camp Match API"
    assert settings.app_env == "local"
    assert settings.debug is False
    assert settings.log_level == "INFO"


def test_settings_override(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    settings = Settings()
    assert settings.app_env == "test"
