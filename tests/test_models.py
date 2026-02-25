import pytest
from pydantic import ValidationError

from models import UserCreate, UserLogin, Token, SummarySave


def test_user_create_valid_model():
    user = UserCreate(username="juan", password="123456")

    assert user.username == "juan"
    assert user.password == "123456"


def test_user_login_valid_model():
    user = UserLogin(username="maria", password="abc123")

    assert user.username == "maria"
    assert user.password == "abc123"


def test_token_valid_model():
    token = Token(access_token="token_demo", token_type="bearer")

    assert token.access_token == "token_demo"
    assert token.token_type == "bearer"


def test_summary_save_defaults_title_to_none():
    summary = SummarySave(
        summary="Resumen breve",
        key_points="Punto 1\nPunto 2",
        questions="Pregunta 1?\nPregunta 2?",
    )

    assert summary.title is None


def test_summary_save_requires_summary_field():
    with pytest.raises(ValidationError):
        SummarySave(
            key_points="Punto 1",
            questions="Pregunta 1?",
        )
