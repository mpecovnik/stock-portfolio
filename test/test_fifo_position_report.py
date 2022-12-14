import pytest

from sp._testing.env import HISTORY_DATA_ROOT, PRECISION_GUARD
from sp.history import PositionHistory
from sp.report import FifoPositionReport


@pytest.mark.parametrize("ticker", ["GME", "BMO", "LGGL", "LGEU", "DBXG", "RTX", "GD", "ABBV", "STOR", "RDSA"])
def test_fifo_report_single_ticker(ticker: str) -> None:

    fifo_report = FifoPositionReport(
        n_workers=1,
        history=PositionHistory(path=HISTORY_DATA_ROOT, query=f"Ticker == '{ticker}'"),
    )

    report_df = fifo_report.create_report_by_ticker(ticker=ticker)
    input_history_df = fifo_report.history.read()

    if ticker in ["LGGL", "LGEU"]:
        assert report_df.empty
        return

    assert not report_df.empty
    assert set(report_df["TICKER"].values) == {ticker}
    assert (
        input_history_df.query("Action == 'Market sell'")["No. of shares"].sum() - report_df["NUM_SHARES"].sum()
        < PRECISION_GUARD
    )
