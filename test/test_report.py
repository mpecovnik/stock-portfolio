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

    assert report["Withholding tax"].sum() == 0.07
    assert report["Total (EUR)"].sum() == 24.76


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT)])
def test_create_report_for_all(input_path: Path) -> None:
    div_report = DividendReport(
        years=[2022],
        history=DividendHistory(path=input_path),
    )

    full_report = div_report.create_report()

    assert full_report.query("Ticker == 'VECP'")["Total (EUR)"].sum() == 24.76
    assert set(full_report.Ticker.unique()) == {'VECP', "VGTY", "CORP"}