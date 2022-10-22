from pathlib import Path

import pytest

from sp.testing.env import TEST_DATA_ROOT
from sp.tracker.data.history import History


@pytest.mark.parametrize(
    "input_path,expected",
    [(TEST_DATA_ROOT / "test_2020.csv", False), (TEST_DATA_ROOT / "fake_test", False), (TEST_DATA_ROOT, True)],
)
def test_exists(input_path: Path, expected: bool) -> None:
    assert History(path=input_path).exists() == expected


@pytest.mark.parametrize("input_path", [(TEST_DATA_ROOT)])
def test_read(input_path: Path) -> None:

    read_columns = set(["Time", "ISIN", "Price / share"])
    read_actions = set(["Market buy"])

    data = History(path=input_path, _columns=read_columns, _actions=read_actions).read(None)

    assert set(data.columns) == read_columns | {"Action"}
    assert set(data["Action"].values) == read_actions
    assert set(data.Time.astype("datetime64[ns]").apply(lambda x: x.year).values) == {2020, 2021, 2022}


@pytest.mark.parametrize("input_path", [(TEST_DATA_ROOT / "fake_test_2020.csv")])
def test_read_exception(input_path: Path) -> None:

    read_columns = set(["ISIN", "Price / share"])
    read_actions = set(["Market buy"])

    hist = History(path=input_path, _columns=read_columns, _actions=read_actions)

    with pytest.raises(ValueError):
        _ = hist.read(None)
