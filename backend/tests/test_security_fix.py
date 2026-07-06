import os
import secrets
import importlib
from unittest.mock import patch
import auth

def test_random_password_generation_when_missing():
    # Mock os.getenv to return None for ADMIN_PASSWORD
    with patch("os.getenv", side_effect=lambda key, default=None: None if key == "ADMIN_PASSWORD" else os.environ.get(key, default)):
        # We need to reload main to trigger the startup logic
        import main
        importlib.reload(main)

        # Verify that ADMIN_PASSWORD_HASH is not the hash of "admin"
        # Since bcrypt uses a salt, we can't just compare hashes.
        # We should use verify_password.
        assert not auth.verify_password("admin", main.ADMIN_PASSWORD_HASH)
        # It should be a strong random password, so "password", "123456" etc should also fail
        assert not auth.verify_password("password", main.ADMIN_PASSWORD_HASH)
        assert not auth.verify_password("123456", main.ADMIN_PASSWORD_HASH)

def test_random_password_generation_when_weak():
    # Mock os.getenv to return a weak password
    for weak_pw in ("admin", "password", "123456", "test"):
        with patch("os.getenv", side_effect=lambda key, default=None: weak_pw if key == "ADMIN_PASSWORD" else os.environ.get(key, default)):
            import main
            importlib.reload(main)

            # Verify that ADMIN_PASSWORD_HASH is NOT the hash of the weak password
            assert not auth.verify_password(weak_pw, main.ADMIN_PASSWORD_HASH)

def test_explicit_password_preserved():
    strong_pw = "my-super-strong-password-123!"
    with patch("os.getenv", side_effect=lambda key, default=None: strong_pw if key == "ADMIN_PASSWORD" else os.environ.get(key, default)):
        import main
        importlib.reload(main)

        # Verify that ADMIN_PASSWORD_HASH IS the hash of the strong password
        assert auth.verify_password(strong_pw, main.ADMIN_PASSWORD_HASH)
