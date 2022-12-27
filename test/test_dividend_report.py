from pathlib import Path

import pytest

from sp._testing.env import HISTORY_DATA_ROOT
from sp.history import DividendHistory
from sp.report import DividendReport


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT)])
def test_raise_on_invalid_desired_years(input_path: Path) -> None:

    div_report = DividendReport(
        years=[2019, 2020, 2021],
        history=DividendHistory(path=input_path),
    )

    with pytest.raises(ValueError):
        _ = div_report.create_report()


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT)])
def test_create_report_for_single_ticker(input_path: Path) -> None:

    div_report = DividendReport(
        years=[2022],
        history=DividendHistory(path=input_path),
    )

    report = div_report.create_report_by_ticker(ticker="VECP")

    assert set(report.columns) == {"DATE", "TICKER", "NAME", "ISIN", "TOTAL", "TAX", "TAX_YEAR"}
    assert report["TAX"].sum() == 0.0
    assert abs(report["TOTAL"].sum() - 15.12) < 0.001


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT)])
def test_create_report_for_all(input_path: Path) -> None:
    div_report = DividendReport(
        years=[2022],
        history=DividendHistory(path=input_path),
    )

    full_report = div_report.create_report()

    assert abs(full_report.query("TICKER == 'VECP'")["TOTAL"].sum() - 15.12) < 0.001
    assert set(full_report.TICKER.unique()) == {"VECP", "VGTY", "CORP"}
