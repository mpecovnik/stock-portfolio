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
