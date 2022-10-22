from pathlib import Path

import pytest

from sp.testing.env import TEST_DATA_ROOT
from sp.tracker.data.csv import CsvFile


@pytest.mark.parametrize(
    "input_path,expected", [(TEST_DATA_ROOT / "test_2020.csv", True), (TEST_DATA_ROOT / "fake_test_2020.csv", False)]
)
def test_exists(input_path: Path, expected: bool) -> None:
    assert CsvFile(path=input_path).exists() == expected


@pytest.mark.parametrize("input_path", [(TEST_DATA_ROOT / "test_2020.csv")])
def test_read(input_path: Path) -> None:

    read_columns = set(["ISIN", "Price / share"])
    read_actions = set(["Market buy"])

    data = CsvFile(path=input_path, _columns=read_columns, _actions=read_actions).read(query=None)

    assert set(data.columns) == read_columns | {"Action"}
    assert set(data["Action"].values) == read_actions


@pytest.mark.parametrize("input_path", [(TEST_DATA_ROOT / "fake_test_2020.csv")])
def test_read_exception(input_path: Path) -> None:

    read_columns = set(["ISIN", "Price / share"])
    read_actions = set(["Market buy"])

    csv = CsvFile(path=input_path, _columns=read_columns, _actions=read_actions)

    with pytest.raises(ValueError):
        _ = csv.read(query=None)
