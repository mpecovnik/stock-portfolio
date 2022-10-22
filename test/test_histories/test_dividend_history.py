from pathlib import Path

from sp.testing.env import TEST_DATA_ROOT
from sp.tracker.core.history import DividendHistory


def test_dividend_history() -> None:
    trans_history = DividendHistory(path=Path(TEST_DATA_ROOT))

    assert set(trans_history.columns) == set(
        ["Time", "ISIN", "Ticker", "Name", "No. of shares", "Price / Share", "Total (EUR)", "Witholding tax", "Action"]
    )
    assert set(trans_history.actions) == set(["Dividend (Ordinary)"])
