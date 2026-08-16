import pytest

from camp_match.modules.identity.domain.value_objects import EmailAddress


def test_email_normalization():
    email = EmailAddress("  TEST@example.com  ")
    assert email.value == "test@example.com"


def test_email_equality():
    email1 = EmailAddress("test@example.com")
    email2 = EmailAddress("  TEST@EXAMPLE.COM  ")
    assert email1 == email2


def test_invalid_email_format():
    with pytest.raises(ValueError, match="Invalid email address format"):
        EmailAddress("invalid-email")

    with pytest.raises(ValueError, match="Invalid email address format"):
        EmailAddress("test@domain")


def test_email_too_long():
    long_email = "a" * 245 + "@example.com"  # 245 + 12 = 257 chars
    with pytest.raises(ValueError, match="Email address too long"):
        EmailAddress(long_email)


def test_valid_email_str():
    email = EmailAddress("test@example.com")
    assert str(email) == "test@example.com"
