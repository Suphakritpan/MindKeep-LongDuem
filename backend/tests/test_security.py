"""Unit tests for password hashing + JWT (no DB required)."""
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_roundtrip():
    h = hash_password("s3cret-pw")
    assert h != "s3cret-pw"
    assert verify_password("s3cret-pw", h)
    assert not verify_password("wrong", h)


def test_jwt_roundtrip():
    token = create_access_token("user-123", {"role": "owner_manager"})
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "owner_manager"
