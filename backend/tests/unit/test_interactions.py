"""Unit tests for interaction filtering logic."""

import pytest
from datetime import datetime, timezone

from app.models.interaction import InteractionLog, InteractionLogCreate, InteractionModel
from app.models.learner import Learner, LearnerCreate
from app.models.item import ItemCreate, ItemRecord
from app.routers.interactions import _filter_by_item_id


def _make_log(id: int, learner_id: int, item_id: int) -> InteractionLog:
    return InteractionLog(id=id, learner_id=learner_id, item_id=item_id, kind="attempt")


def test_filter_returns_all_when_item_id_is_none() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, None)
    assert result == interactions


def test_filter_returns_empty_for_empty_input() -> None:
    result = _filter_by_item_id([], 1)
    assert result == []


def test_filter_returns_interaction_with_matching_ids() -> None:
    interactions = [_make_log(1, 1, 1), _make_log(2, 2, 2)]
    result = _filter_by_item_id(interactions, 1)
    assert len(result) == 1
    assert result[0].id == 1


def test_filter_includes_interaction_with_different_learner_id() -> None:
    interaction = _make_log(1, 2, 1)
    interactions = [interaction]
    result = _filter_by_item_id(interactions, 1)
    assert interaction in result


def test_interaction_log_create_accepts_empty_kind() -> None:
    """Граничный случай: пустая строка kind допускается Pydantic."""
    log = InteractionLogCreate(learner_id=1, item_id=1, kind="")
    assert log.kind == ""


def test_interaction_log_create_with_negative_ids() -> None:
    """Граничный случай: отрицательные ID learner_id и item_id."""
    log = InteractionLogCreate(learner_id=-1, item_id=-1, kind="attempt")
    assert log.learner_id == -1
    assert log.item_id == -1


def test_interaction_model_with_unicode_kind() -> None:
    """Граничный случай: Unicode-символы в поле kind."""
    model = InteractionModel(
        id=1,
        learner_id=1,
        item_id=1,
        kind="попытка_🚀_尝试",
        created_at=datetime.now(timezone.utc)
    )
    assert model.kind == "попытка_🚀_尝试"


def test_learner_create_accepts_empty_name_and_email() -> None:
    """Граничный случай: пустые строки name и email допускаются Pydantic."""
    learner = LearnerCreate(name="", email="")
    assert learner.name == ""
    assert learner.email == ""


def test_item_create_with_very_long_title() -> None:
    """Граничный случай: очень длинная строка title (10000 символов)."""
    long_title = "A" * 10000
    item = ItemCreate(type="step", parent_id=None, title=long_title, description="")
    assert len(item.title) == 10000
    assert item.title == long_title
