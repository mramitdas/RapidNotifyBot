"""Scaffold smoke test: modern stack importable from repo root, no CWD hacks."""


def test_modern_stack_importable() -> None:
    import fastapi
    import pydantic
    import sqlalchemy
    import telegram

    assert fastapi.__version__ >= "0.118"
    assert pydantic.__version__ >= "2.11"
    assert sqlalchemy.__version__ >= "2.0"
    assert telegram.__version__ >= "22"
