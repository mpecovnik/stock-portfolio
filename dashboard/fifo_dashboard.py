from sp.testing.env import TEST_DATA_ROOT
from sp.tracker.core.class_model import ExecutionConfig
from sp.tracker.data.history import PositionHistory
from sp.tracker.reports.fifo_position_report import (
    FifoPositionDashboard,
    FifoPositionReport,
)

position_history = PositionHistory(path=TEST_DATA_ROOT)
wanted_tickers = list(position_history.read(None).Ticker.unique())

fifo_report = FifoPositionReport(
    tickers=wanted_tickers,
    exec_config=ExecutionConfig(n_workers=1),
    position_history=position_history,
)

fifo_dashboard = FifoPositionDashboard(fifo_position_report=fifo_report)
fifo_dashboard.serve_dashboard()
