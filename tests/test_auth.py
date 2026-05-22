from types import SimpleNamespace

from app import auth


def test_sign_in_sends_turnstile_payload(monkeypatch, db_session) -> None:
    calls = []

    def fake_auth_request(method, path, **kwargs):
        calls.append((method, path, kwargs))
        return {
            "user": {"id": "00000000-0000-4000-8000-000000000001", "email": "Editor@Example.com"},
            "access_token": "access-token",
            "refresh_token": "refresh-token",
            "expires_in": 3600,
        }

    monkeypatch.setattr(auth, "auth_request", fake_auth_request)
    request = SimpleNamespace(session={})

    user = auth.sign_in_with_password(request, db_session, "editor@example.com", "Valid1!Pass", "turnstile-token")

    assert user.email == "editor@example.com"
    assert request.session[auth.SESSION_KEY]
    assert calls == [
        (
            "POST",
            "/token?grant_type=password",
            {
                "json": {
                    "email": "editor@example.com",
                    "password": "Valid1!Pass",
                    "captcha_token": "turnstile-token",
                    "gotrue_meta_security": {"captcha_token": "turnstile-token"},
                }
            },
        )
    ]


def test_password_validation_requires_mixed_password() -> None:
    assert auth.password_validation_error("short") == auth.PASSWORD_ERROR_MESSAGE
    assert auth.password_validation_error("GoodPass1!") is None
