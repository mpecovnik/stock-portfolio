from pathlib import Path

import pytest

from sp.testing.env import HISTORY_DATA_ROOT
from sp.tracker.core.class_model import ExecutionConfig
from sp.tracker.data.history import DividendHistory
from sp.tracker.reports.dividend_report import DividendReport


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT)])
def test_dividend_report_execution(input_path: Path) -> None:

    div_report = DividendReport(
        exec_config=ExecutionConfig(n_workers=1),
        history=DividendHistory(path=input_path),
    )

    report_df = div_report.create_report()

    assert not report_df.empty


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT)])
def test_dividend_report_single_ticker(input_path: Path) -> None:

    div_report = DividendReport(
        exec_config=ExecutionConfig(n_workers=1),
        history=DividendHistory(path=input_path),
    )

    report_df = div_report.create_report_by_ticker(ticker="VECP")

    assert not report_df.empty
    assert set(report_df["Ticker"].values) == {"VECP"}
