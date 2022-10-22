from queue import Queue
from typing import Dict, List, TypeVar

import pandas as pd

from sp.testing.env import PRECISION_GUARD
from sp.tracker.core.class_model import BaseModel, ReportBaseModel
from sp.tracker.data.history import PositionHistory

A = TypeVar("A", bound="Action")


class Action(BaseModel):
    type: str
    time: str
    num_shares: float
    price: float

    def __sub__(self: A, other: A) -> A:
        returned_action = self.copy()
        returned_action.num_shares -= other.num_shares

        return returned_action


class BuyAction(Action):
    type = "Buy"


class SellAction(Action):
    type = "Sell"


class FifoPositionReport(ReportBaseModel):
    position_history: PositionHistory

    def create_report_in_full(self) -> pd.DataFrame:
        ...  # pragma: no cover

    def create_report_by_ticker(self, ticker: str) -> pd.DataFrame:
        ticker_position_history = self.position_history.read(f"Ticker == '{ticker}'").sort_values("Time")

        if "Market sell" not in ticker_position_history["Action"].unique():
            return pd.DataFrame()

        buy_sell_counts = ticker_position_history.value_counts("Action")
        buy_queue: Queue[BuyAction] = Queue(buy_sell_counts["Market buy"])
        sell_queue: Queue[SellAction] = Queue(buy_sell_counts["Market sell"])

        isin = ticker_position_history["ISIN"].unique()[0]
        name = ticker_position_history["Name"].unique()[0]
        currencies = ticker_position_history["Currency (Price / share)"].unique()

        if len(currencies) != 1:
            raise ValueError

        currency = currencies[0]

        for _, row in ticker_position_history.iterrows():
            if row["Action"] == "Market buy":
                buy_queue.put(
                    BuyAction(
                        time=row["Time"],
                        num_shares=row["No. of shares"],
                        price=row["Price / share"],
                        currency=row["Currency (Price / share)"],
                    )
                )
            else:
                sell_queue.put(
                    SellAction(
                        time=row["Time"],
                        num_shares=row["No. of shares"],
                        price=row["Price / share"],
                        currency=row["Currency (Price / share)"],
                    )
                )

        # pair buys and sells in a FIFO fashion

        sell_action = None
        buy_action = None

        actions_dict: Dict[str, List[str | float]] = {
            "BUY_DATE": [],
            "NUM_BOUGHT_SHARES": [],
            "BUY_PRICE_PER_SHARE": [],
            "SELL_DATE": [],
            "NUM_SOLD_SHARES": [],
            "SELL_PRICE_PER_SHARE": [],
        }

        while not (sell_queue.empty() and sell_action is None):

            if buy_action is not None and buy_action.num_shares < PRECISION_GUARD:
                buy_action = None

            if sell_action is not None and sell_action.num_shares < PRECISION_GUARD:
                sell_action = None

            buy_action = buy_queue.get() if not buy_action else buy_action
            sell_action = sell_queue.get() if not sell_action else sell_action

            if sell_action.num_shares >= buy_action.num_shares:
                paired_sell_action = sell_action.copy()
                paired_sell_action.num_shares = buy_action.num_shares
                action_tuple = (buy_action, paired_sell_action)

                sell_action = sell_action - paired_sell_action
                if sell_action.num_shares < PRECISION_GUARD:
                    sell_action = None
                buy_action = None
            else:
                paired_buy_action = buy_action.copy()
                paired_buy_action.num_shares = sell_action.num_shares
                action_tuple = (paired_buy_action, sell_action)

                buy_action = buy_action - paired_buy_action
                if buy_action.num_shares < PRECISION_GUARD:
                    buy_action = None
                sell_action = None

            current_buy, current_sell = action_tuple

            actions_dict["BUY_DATE"].append(current_buy.time)
            actions_dict["NUM_BOUGHT_SHARES"].append(current_buy.num_shares)
            actions_dict["BUY_PRICE_PER_SHARE"].append(current_buy.price)

            actions_dict["SELL_DATE"].append(current_sell.time)
            actions_dict["NUM_SOLD_SHARES"].append(current_sell.num_shares)
            actions_dict["SELL_PRICE_PER_SHARE"].append(current_sell.price)

        report_df = pd.DataFrame(actions_dict)
        report_df.loc[:, ["TICKER", "NAME", "ISIN", "CURRENCY"]] = ticker, name, isin, currency

        return report_df
