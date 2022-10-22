from pathlib import Path

from sp.testing.env import TEST_DATA_ROOT
from sp.tracker.core.history import PositionHistory


def test_position_history() -> None:
    trans_history = PositionHistory(path=Path(TEST_DATA_ROOT))

    assert set(trans_history.columns) == set(
        [
            "Time",
            "ISIN",
            "Ticker",
            "Name",
            "No. of shares",
            "Currency (Price / Share)",
            "Price / Share",
            "Total (EUR)",
            "Action",
        ]
    )
    assert set(trans_history.actions) == set(["Market buy", "Market sell"])
