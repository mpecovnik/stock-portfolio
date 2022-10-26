from sp.testing.env import HISTORY_DATA_ROOT
from sp.tracker.core.class_model import ExecutionConfig
from sp.tracker.data.history import PositionHistory
from sp.tracker.reports.fifo_position_report import (
    FifoPositionDashboard,
    FifoPositionReport,
)


def test_fifo_dashboard() -> None:

    fifo_report = FifoPositionReport(
        exec_config=ExecutionConfig(n_workers=1),
        history=PositionHistory(path=HISTORY_DATA_ROOT),
    )

    dashboard = FifoPositionDashboard(fifo_position_report=fifo_report)

    served_dashboard = dashboard.serve_dashboard()

    assert served_dashboard.initialized
