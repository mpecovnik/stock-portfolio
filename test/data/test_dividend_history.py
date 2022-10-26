from pathlib import Path

from sp.testing.env import HISTORY_DATA_ROOT
from sp.tracker.data.history import DividendHistory


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
