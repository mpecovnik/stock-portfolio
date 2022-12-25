from .model import HistoryModel


class DividendHistory(HistoryModel):
    _columns = [
        "Time",
        "ISIN",
        "Ticker",
        "Name",
        "No. of shares",
        "Price / share",
        "Total (EUR)",
        "Withholding tax",
        "Exchange rate",
    ]
    _actions = ["Dividend (Ordinary)"]


class PositionHistory(HistoryModel):
    _columns = [
        "Time",
        "ISIN",
        "Ticker",
        "Name",
        "No. of shares",
        "Currency (Price / share)",
        "Price / share",
        "Total (EUR)",
        "Exchange rate",
    ]
    _actions = ["Market buy", "Market sell"]
