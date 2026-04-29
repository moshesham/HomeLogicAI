from __future__ import annotations

from datetime import timedelta

import pytest

from core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from fastapi import HTTPException


def test_password_hash_and_verify() -> None:
    plain = "MySecurePassword1!"
    hashed = get_password_hash(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)


def test_password_verify_wrong() -> None:
    hashed = get_password_hash("correct")
    assert not verify_password("wrong", hashed)


def test_create_and_verify_token() -> None:
    data = {"sub": "user-uuid-123", "email": "user@example.com"}
    token = create_access_token(data, expires_delta=timedelta(minutes=15))
    assert isinstance(token, str)
    payload = verify_token(token)
    assert payload["sub"] == "user-uuid-123"
    assert payload["email"] == "user@example.com"


def test_verify_invalid_token() -> None:
    with pytest.raises(HTTPException) as exc_info:
        verify_token("not.a.valid.jwt.token")
    assert exc_info.value.status_code == 401


def test_verify_tampered_token() -> None:
    token = create_access_token({"sub": "abc"}, expires_delta=timedelta(minutes=1))
    tampered = token[:-4] + "XXXX"
    with pytest.raises(HTTPException):
        verify_token(tampered)
