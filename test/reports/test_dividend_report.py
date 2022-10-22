from pathlib import Path

import pytest

from sp.testing.env import TEST_DATA_ROOT
from sp.tracker.core.class_model import ExecutionConfig
from sp.tracker.data.history import DividendHistory
from sp.tracker.reports.dividend_report import DividendReport


@pytest.mark.parametrize("input_path", [(TEST_DATA_ROOT)])
def test_dividend_report_execution(input_path: Path) -> None:

    wanted_tickers = ["VECP", "VGTY"]

    div_report = DividendReport(
        tickers=wanted_tickers,
        exec_config=ExecutionConfig(n_workers=1),
        dividend_history=DividendHistory(path=input_path),
    )

    report_df = div_report.create_report()

    assert not report_df.empty
    assert set(report_df["Ticker"].values) == set(wanted_tickers)


@pytest.mark.parametrize("input_path", [(TEST_DATA_ROOT)])
def test_dividend_report_single_ticker(input_path: Path) -> None:

    wanted_tickers = ["VECP", "VGTY"]

    div_report = DividendReport(
        tickers=wanted_tickers,
        exec_config=ExecutionConfig(n_workers=1),
        dividend_history=DividendHistory(path=input_path),
    )

    report_df = div_report.create_report_by_ticker(ticker=wanted_tickers[0])

    assert not report_df.empty
    assert set(report_df["Ticker"].values) == set(wanted_tickers[0:1])
