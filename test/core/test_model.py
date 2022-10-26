from pathlib import Path

import pytest

from sp.tracker.core.class_model import HistoryModel


class Data(HistoryModel):
    def exists(self) -> bool:
        return True  # pragma: no cover

    def read(self, query: str | None = None) -> str | None:
        return query  # pragma: no cover


def test_no_columns_exception() -> None:
    test_model = Data(path=Path("fake_path"), _actions=["Buy", "Sell"])

    with pytest.raises(AttributeError):
        _ = test_model.columns


def test_no_actions_exception() -> None:
    test_model = Data(path=Path("fake_path"), _columns=["Time", "Total (Eur)"])

    with pytest.raises(AttributeError):
        _ = test_model.actions
