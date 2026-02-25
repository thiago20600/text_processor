from datetime import timedelta

from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
)


def test_password_hash_and_verify_success():
    password = "mi_password_super_seguro_123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True


def test_password_hash_and_verify_failure():
    password = "password_correcto"
    hashed = get_password_hash(password)

    assert verify_password("otro_password", hashed) is False


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "usuario_test"})

    assert isinstance(token, str)
    assert len(token) > 20


def test_create_access_token_with_custom_expiration():
    token = create_access_token(
        {"sub": "usuario_test"},
        expires_delta=timedelta(minutes=5),
    )

    assert isinstance(token, str)
    assert len(token) > 20
