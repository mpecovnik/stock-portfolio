from pathlib import Path

from sp.testing.env import HISTORY_DATA_ROOT
from sp.tracker.data.history import TransactionHistory


def test_transaction_history() -> None:
    trans_history = TransactionHistory(path=Path(HISTORY_DATA_ROOT))

    assert set(trans_history.columns) == set(["Time", "Total (EUR)", "Action"])
    assert set(trans_history.actions) == set(["Deposit", "Withdraw"])
