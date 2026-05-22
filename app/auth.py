from __future__ import annotations

import logging
import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode
from uuid import UUID

import httpx
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import AppSession, User


logger = logging.getLogger(__name__)
SESSION_KEY = "revisi_app_session_id"
AUTH_TIMEOUT_SECONDS = 10.0
REFRESH_SKEW_SECONDS = 60
PASSWORD_ERROR_MESSAGE = "Use at least 8 characters with uppercase, lowercase, a number, and a symbol."
PASSWORD_CONFIRMATION_ERROR_MESSAGE = "Passwords do not match."
CAPTCHA_ERROR_MESSAGE = "Complete the verification before continuing."


class AuthError(Exception):
    def __init__(self, user_message: str, *, log_message: str | None = None) -> None:
        super().__init__(log_message or user_message)
        self.user_message = user_message


def password_validation_error(password: str) -> str | None:
    checks = (
        len(password) >= 8,
        bool(re.search(r"[A-Z]", password)),
        bool(re.search(r"[a-z]", password)),
        bool(re.search(r"\d", password)),
        bool(re.search(r"[^A-Za-z0-9]", password)),
    )
    return None if all(checks) else PASSWORD_ERROR_MESSAGE


def password_confirmation_error(password: str, confirmation: str) -> str | None:
    return None if password == confirmation else PASSWORD_CONFIRMATION_ERROR_MESSAGE


def auth_user_message(raw_message: str) -> str:
    normalized = raw_message.lower()
    if "invalid login" in normalized or "invalid credentials" in normalized:
        return "That email and password combination did not match."
    if "email not confirmed" in normalized or "not confirmed" in normalized:
        return "Check your email to confirm your account before logging in."
    if "already registered" in normalized or "already exists" in normalized:
        return "That email is already in use. Try logging in instead."
    return raw_message


def _supabase_auth_url(path: str) -> str:
    settings = get_settings()
    if not settings.supabase_url:
        raise AuthError("Authentication is not configured yet.")
    return f"{settings.supabase_url.rstrip('/')}/auth/v1{path}"


def _supabase_headers(*, access_token: str | None = None) -> dict[str, str]:
    settings = get_settings()
    if not settings.supabase_publishable_key:
        raise AuthError("Authentication is not configured yet.")
    headers = {
        "apikey": settings.supabase_publishable_key,
        "content-type": "application/json",
    }
    if access_token:
        headers["authorization"] = f"Bearer {access_token}"
    return headers


def auth_request(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    access_token: str | None = None,
) -> dict[str, Any]:
    try:
        response = httpx.request(
            method,
            _supabase_auth_url(path),
            headers=_supabase_headers(access_token=access_token),
            json=json,
            timeout=AUTH_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        raise AuthError("Authentication is temporarily unavailable.", log_message=str(exc)) from exc

    if response.status_code >= 400:
        message = "Authentication failed. Try again."
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        if isinstance(payload, dict):
            raw_message = payload.get("msg") or payload.get("message") or payload.get("error_description")
            if isinstance(raw_message, str) and raw_message.strip():
                message = auth_user_message(raw_message)
        raise AuthError(message, log_message=f"Supabase Auth returned {response.status_code}: {response.text}")

    if not response.content:
        return {}
    payload = response.json()
    return payload if isinstance(payload, dict) else {}


def _parse_user(payload: dict[str, Any]) -> tuple[str, str] | None:
    user_payload = payload.get("user")
    if not isinstance(user_payload, dict):
        user_payload = payload
    raw_id = user_payload.get("id")
    raw_email = user_payload.get("email")
    if not isinstance(raw_id, str) or not isinstance(raw_email, str):
        return None
    try:
        user_id = str(UUID(raw_id))
    except ValueError:
        return None
    return user_id, raw_email.strip().lower()


def _session_expires_at(payload: dict[str, Any]) -> datetime | None:
    expires_in = payload.get("expires_in")
    if isinstance(expires_in, int):
        return datetime.now(UTC) + timedelta(seconds=max(0, expires_in))
    return None


def auth_callback_url() -> str:
    base_url = get_settings().public_site_url or "http://127.0.0.1:8000"
    return f"{base_url.rstrip('/')}/auth/callback"


def ensure_user(db: Session, user_id: str, email: str) -> User:
    user = db.get(User, user_id)
    if user is None:
        user = User(id=user_id, email=email)
        db.add(user)
    else:
        user.email = email
    db.commit()
    db.refresh(user)
    return user


def create_app_session(request: Request, db: Session, user: User, payload: dict[str, Any]) -> None:
    access_token = payload.get("access_token")
    refresh_token = payload.get("refresh_token")
    if not isinstance(access_token, str) or not isinstance(refresh_token, str):
        return
    session_id = secrets.token_urlsafe(32)
    db.add(
        AppSession(
            id=session_id,
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=_session_expires_at(payload),
        )
    )
    db.commit()
    request.session[SESSION_KEY] = session_id


def sign_up_with_password(request: Request, db: Session, email: str, password: str, captcha_token: str) -> User:
    payload = auth_request(
        "POST",
        f"/signup?{urlencode({'redirect_to': auth_callback_url()})}",
        json=_password_payload(email, password, captcha_token),
    )
    parsed = _parse_user(payload)
    if parsed is None:
        raise AuthError("Signup did not return a user. Try again.")
    user = ensure_user(db, *parsed)
    create_app_session(request, db, user, payload)
    return user


def sign_in_with_password(request: Request, db: Session, email: str, password: str, captcha_token: str) -> User:
    payload = auth_request(
        "POST",
        "/token?grant_type=password",
        json=_password_payload(email, password, captcha_token),
    )
    parsed = _parse_user(payload)
    if parsed is None:
        raise AuthError("Login did not return a user. Try again.")
    user = ensure_user(db, *parsed)
    create_app_session(request, db, user, payload)
    return user


def _password_payload(email: str, password: str, captcha_token: str) -> dict[str, Any]:
    return {
        "email": email,
        "password": password,
        "captcha_token": captcha_token,
        "gotrue_meta_security": {"captcha_token": captcha_token},
    }


def verify_email_otp(request: Request, db: Session, token_hash: str, otp_type: str) -> User:
    payload = auth_request("POST", "/verify", json={"token_hash": token_hash, "type": otp_type})
    parsed = _parse_user(payload)
    if parsed is None and isinstance(payload.get("access_token"), str):
        parsed = _parse_user(auth_request("GET", "/user", access_token=payload["access_token"]))
    if parsed is None:
        raise AuthError("That email link is invalid or expired.")
    user = ensure_user(db, *parsed)
    create_app_session(request, db, user, payload)
    return user


def create_app_session_from_tokens(
    request: Request,
    db: Session,
    *,
    access_token: str,
    refresh_token: str,
    expires_in: int | None = None,
) -> User:
    parsed = _parse_user(auth_request("GET", "/user", access_token=access_token))
    if parsed is None:
        raise AuthError("That email link is invalid or expired.")
    user = ensure_user(db, *parsed)
    payload: dict[str, Any] = {"access_token": access_token, "refresh_token": refresh_token}
    if expires_in is not None:
        payload["expires_in"] = expires_in
    create_app_session(request, db, user, payload)
    return user


def request_password_reset(email: str) -> None:
    auth_request(
        "POST",
        f"/recover?{urlencode({'redirect_to': auth_callback_url()})}",
        json={"email": email},
    )


def update_current_user_password(request: Request, db: Session, password: str) -> None:
    app_session = _session_from_request(request, db)
    if app_session is None:
        raise AuthError("Your reset session expired. Request a new password reset link.")
    auth_request("PUT", "/user", json={"password": password}, access_token=app_session.access_token)


def _session_from_request(request: Request, db: Session) -> AppSession | None:
    session_id = request.session.get(SESSION_KEY)
    if not isinstance(session_id, str):
        return None
    return db.get(AppSession, session_id)


def _session_needs_refresh(app_session: AppSession) -> bool:
    if app_session.expires_at is None:
        return False
    expires_at = app_session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    return expires_at <= datetime.now(UTC) + timedelta(seconds=REFRESH_SKEW_SECONDS)


def _refresh_app_session(db: Session, app_session: AppSession) -> bool:
    payload = auth_request(
        "POST",
        "/token?grant_type=refresh_token",
        json={"refresh_token": app_session.refresh_token},
    )
    access_token = payload.get("access_token")
    refresh_token = payload.get("refresh_token")
    if not isinstance(access_token, str) or not isinstance(refresh_token, str):
        return False
    app_session.access_token = access_token
    app_session.refresh_token = refresh_token
    app_session.expires_at = _session_expires_at(payload)
    db.commit()
    return True


def _clear_invalid_session(request: Request, db: Session, app_session: AppSession | None) -> None:
    request.session.clear()
    if app_session is not None:
        db.delete(app_session)
        db.commit()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    app_session = _session_from_request(request, db)
    if app_session is None:
        request.session.clear()
        return None
    try:
        if _session_needs_refresh(app_session) and not _refresh_app_session(db, app_session):
            _clear_invalid_session(request, db, app_session)
            return None
        parsed = _parse_user(auth_request("GET", "/user", access_token=app_session.access_token))
    except AuthError:
        logger.info("Clearing rejected Revisi auth session.", exc_info=True)
        _clear_invalid_session(request, db, app_session)
        return None
    if parsed is None:
        _clear_invalid_session(request, db, app_session)
        return None
    return ensure_user(db, *parsed)


def logout_user(request: Request, db: Session) -> None:
    app_session = _session_from_request(request, db)
    request.session.clear()
    if app_session is None:
        return
    try:
        auth_request("POST", "/logout", access_token=app_session.access_token)
    except AuthError:
        logger.info("Supabase logout failed while local session was clearing.", exc_info=True)
    db.delete(app_session)
    db.commit()
