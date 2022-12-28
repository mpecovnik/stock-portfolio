from pathlib import Path
from typing import Optional

import pytest

from sp._testing.env import HISTORY_DATA_ROOT
from sp.model import HistoryModel


class Data(HistoryModel):
    def exists(self) -> bool:
        return True  # pragma: no cover

    def read(self, query: Optional[str] = None) -> Optional[str]:
        return query  # pragma: no cover


def test_no_columns_exception() -> None:
    test_model = Data(path=Path("fake_path"), _actions=["Buy", "Sell"])

    with pytest.raises(AttributeError):
        _ = test_model.columns


def test_no_actions_exception() -> None:
    test_model = Data(path=Path("fake_path"), _columns=["Time", "Total (Eur)"])

    with pytest.raises(AttributeError):
        _ = test_model.actions


@pytest.mark.parametrize(
    "input_path,expected",
    [(HISTORY_DATA_ROOT / "test_2020.csv", False), (HISTORY_DATA_ROOT / "fake_test", False), (HISTORY_DATA_ROOT, True)],
)
def test_exists(input_path: Path, expected: bool) -> None:
    assert HistoryModel(path=input_path).exists() == expected


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT)])
def test_read(input_path: Path) -> None:

    read_columns = set(["Time", "ISIN", "Price / share"])
    read_actions = set(["Market buy"])

    data = HistoryModel(path=input_path, _columns=read_columns, _actions=read_actions).read()

    assert set(data.columns) == read_columns | {"Action"}
    assert set(data["Action"].values) == read_actions
    assert set(data.Time.astype("datetime64[ns]").apply(lambda x: x.year).values) == {2020, 2021, 2022}


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT / "fake_test_2020.csv")])
def test_read_exception(input_path: Path) -> None:

    read_columns = set(["ISIN", "Price / share"])
    read_actions = set(["Market buy"])

    hist = HistoryModel(path=input_path, _columns=read_columns, _actions=read_actions)

    with pytest.raises(ValueError):
        _ = hist.read()
