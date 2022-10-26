from sp.testing.env import TEST_DATA_ROOT
from sp.tracker.core.class_model import ExecutionConfig
from sp.tracker.data.history import PositionHistory
from sp.tracker.reports.fifo_position_report import (
    FifoPositionDashboard,
    FifoPositionReport,
)

fifo_report = FifoPositionReport(
    exec_config=ExecutionConfig(n_workers=1),
    history=PositionHistory(path=TEST_DATA_ROOT),
)

fifo_dashboard = FifoPositionDashboard(fifo_position_report=fifo_report)
fifo_dashboard.serve_dashboard()
