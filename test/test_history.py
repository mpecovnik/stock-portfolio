from pathlib import Path

from sp._testing.env import HISTORY_DATA_ROOT
from sp.history import DividendHistory, PositionHistory


def test_dividend_history() -> None:
    trans_history = DividendHistory(path=Path(HISTORY_DATA_ROOT))

    assert set(trans_history.columns) == set(
        [
            "Time",
            "ISIN",
            "Ticker",
            "Name",
            "No. of shares",
            "Price / share",
            "Total (EUR)",
            "Withholding tax",
            "Action",
            "Exchange rate",
        ]
    )
    assert set(trans_history.actions) == set(["Dividend (Ordinary)"])


def test_position_history() -> None:
    trans_history = PositionHistory(path=Path(HISTORY_DATA_ROOT))

    assert set(trans_history.columns) == set(
        [
            "Time",
            "ISIN",
            "Ticker",
            "Name",
            "No. of shares",
            "Currency (Price / share)",
            "Price / share",
            "Total (EUR)",
            "Action",
            "Exchange rate",
        ]
    )
    assert set(trans_history.actions) == set(["Market buy", "Market sell"])
