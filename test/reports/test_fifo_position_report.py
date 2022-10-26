import pytest

from sp.testing.env import HISTORY_DATA_ROOT, PRECISION_GUARD
from sp.tracker.core.class_model import ExecutionConfig
from sp.tracker.data.history import PositionHistory
from sp.tracker.reports.fifo_position_report import FifoPositionReport


@pytest.mark.parametrize("ticker", ["GME", "BMO", "LGGL", "LGEU", "DBXG", "RTX", "GD", "ABBV", "STOR"])
def test_fifo_report_single_ticker(ticker: str) -> None:

    fifo_report = FifoPositionReport(
        exec_config=ExecutionConfig(n_workers=1),
        history=PositionHistory(path=HISTORY_DATA_ROOT),
    )

    report_df = fifo_report.create_report_by_ticker(ticker=ticker)
    input_history_df = fifo_report.history.read(f"Ticker == '{ticker}'")

    if ticker in ["LGGL", "LGEU"]:
        assert report_df.empty
        return

    assert not report_df.empty
    assert set(report_df["TICKER"].values) == {ticker}
    assert (
        input_history_df.query("Action == 'Market sell'")["No. of shares"].sum() - report_df["NUM_SHARES"].sum()
        < PRECISION_GUARD
    )
