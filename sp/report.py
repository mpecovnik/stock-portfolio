from queue import Queue
from typing import Dict, List, Union

import pandas as pd

from .history import DividendHistory, PositionHistory
from .model import ReportModel
from .utils import PRECISION_GUARD, BuyAction, SellAction


class DividendReport(ReportModel):
    history: DividendHistory

    def create_report_by_ticker(self, ticker: str) -> pd.DataFrame:
        ticker_history = self.add_ticker_to_history_query(ticker=ticker)
        ticker_history = ticker_history.read()
        ticker_history.loc[:, "DATE"] = (
            ticker_history.Time.astype("datetime64[ns]").apply(lambda x: x.date().strftime("%Y-%m-%d")).values
        )
        ticker_history.loc[:, "TAX_YEAR"] = ticker_history.DATE.astype("datetime64[ns]").apply(lambda x: x.year).values
        report = ticker_history.query(f"TAX_YEAR in {self.years}")

        report = report[["DATE", "Ticker", "Name", "ISIN", "Total (EUR)", "Withholding tax", "TAX_YEAR"]]
        report = report.rename(
            columns={"Name": "NAME", "Ticker": "TICKER", "Total (EUR)": "TOTAL", "Withholding tax": "TAX"}
        )

        return report


class FifoPositionReport(ReportModel):
    history: PositionHistory

    def create_report_by_ticker(self, ticker: str) -> pd.DataFrame:
        ticker_history = self.add_ticker_to_history_query(ticker=ticker)
        ticker_position_history = ticker_history.read().sort_values("Time")

        if "Market sell" not in ticker_position_history["Action"].unique():
            return pd.DataFrame()

        buy_sell_counts = ticker_position_history.value_counts("Action")
        buy_queue: Queue[BuyAction] = Queue(buy_sell_counts["Market buy"])
        sell_queue: Queue[SellAction] = Queue(buy_sell_counts["Market sell"])

        isin = ticker_position_history["ISIN"].unique()[0]
        name = ticker_position_history["Name"].unique()[0]

        ticker_position_history.loc[:, "Price / share"] = ticker_position_history.loc[
            :, "Price / share"
        ] / ticker_position_history.loc[:, "Exchange rate"].astype(float)
        ticker_position_history.loc[:, "DATE"] = (
            ticker_position_history.Time.astype("datetime64[ns]").apply(lambda x: x.date().strftime("%Y-%m-%d")).values
        )
        ticker_position_history = ticker_position_history[["DATE", "No. of shares", "Price / share", "Action"]]

        for _, row in ticker_position_history.iterrows():
            if row["Action"] == "Market buy":
                buy_queue.put(
                    BuyAction(
                        date=row["DATE"],
                        num_shares=row["No. of shares"],
                        price=row["Price / share"],
                    )
                )
            else:
                sell_queue.put(
                    SellAction(
                        date=row["DATE"],
                        num_shares=row["No. of shares"],
                        price=row["Price / share"],
                    )
                )

        # pair buys and sells in a FIFO fashion

        sell_action = None
        buy_action = None

        actions_dict: Dict[str, List[Union[str, float]]] = {
            "NUM_SHARES": [],
            "BUY_DATE": [],
            "BUY_PRICE_PER_SHARE": [],
            "SELL_DATE": [],
            "SELL_PRICE_PER_SHARE": [],
        }

        while not (sell_queue.empty() and sell_action is None):

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

            actions_dict["NUM_SHARES"].append(current_sell.num_shares)

            actions_dict["BUY_DATE"].append(current_buy.date)
            actions_dict["BUY_PRICE_PER_SHARE"].append(current_buy.price)
            actions_dict["SELL_DATE"].append(current_sell.date)
            actions_dict["SELL_PRICE_PER_SHARE"].append(current_sell.price)

        report_df = pd.DataFrame(actions_dict)
        report_df.loc[:, ["TICKER", "NAME", "ISIN", "CURRENCY"]] = (
            ticker,
            name,
            isin,
            "EUR",
        )
        report_df.loc[:, "TAX_YEAR"] = report_df.SELL_DATE.astype("datetime64[ns]").apply(lambda x: x.year).values
        report_df.loc[:, "RESULT"] = report_df.loc[:, "NUM_SHARES"] * (
            report_df.loc[:, "SELL_PRICE_PER_SHARE"] - report_df.loc[:, "BUY_PRICE_PER_SHARE"]
        )

        return report_df
