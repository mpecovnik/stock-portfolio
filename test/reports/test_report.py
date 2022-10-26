from pathlib import Path

import pytest

from sp.testing.env import HISTORY_DATA_ROOT
from sp.tracker.core.class_model import ExecutionConfig
from sp.tracker.data.history import DividendHistory
from sp.tracker.reports.dividend_report import DividendReport


@pytest.mark.parametrize("input_path", [(HISTORY_DATA_ROOT)])
def test_raise_on_invalid_desired_years(input_path: Path) -> None:

    div_report = DividendReport(
        years=[2019, 2020, 2021],
        exec_config=ExecutionConfig(n_workers=1),
        history=DividendHistory(path=input_path),
    )

    with pytest.raises(ValueError):
        _ = div_report.create_report()
