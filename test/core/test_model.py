from pathlib import Path

import pytest

from sp.tracker.core.class_model import DataBaseModel


def test_no_columns_exception() -> None:
    test_model = DataBaseModel(path=Path("fake_path"), _actions=["Buy", "Sell"])

    with pytest.raises(AttributeError):
        _ = test_model.columns


def test_no_actions_exception() -> None:
    test_model = DataBaseModel(path=Path("fake_path"), _columns=["Time", "Total (Eur)"])

    with pytest.raises(AttributeError):
        _ = test_model.actions
