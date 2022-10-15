from sp.tracker.core.history import History


class TransactionHistory(History):
    _columns = ["Time", "Total (EUR)"]
    _actions = ["Deposit", "Withdraw"]
