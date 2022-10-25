from queue import Queue
from typing import Dict, List, TypeVar

import numpy as np
import pandas as pd
import panel as pn
import param

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
            raise ValueError  # pragma: no cover

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

            actions_dict["BUY_DATE"].append(current_buy.time)
            actions_dict["BUY_PRICE_PER_SHARE"].append(current_buy.price)
            actions_dict["SELL_DATE"].append(current_sell.time)
            actions_dict["SELL_PRICE_PER_SHARE"].append(current_sell.price)

        report_df = pd.DataFrame(actions_dict)
        report_df.loc[:, ["TICKER", "NAME", "ISIN", "CURRENCY"]] = ticker, name, isin, currency
        report_df.loc[:, "TAX_YEAR"] = report_df.SELL_DATE.astype("datetime64[ns]").apply(lambda x: x.year).values
        report_df.loc[:, "RESULT"] = report_df.loc[:, "NUM_SHARES"] * (
            report_df.loc[:, "SELL_PRICE_PER_SHARE"] - report_df.loc[:, "BUY_PRICE_PER_SHARE"]
        )

        return report_df


class FifoPositionDashboard(BaseModel):
    fifo_position_report: FifoPositionReport

    def serve_dashboard(self) -> param.Parameterized:

        report_df = self.fifo_position_report.create_report()

        tickers = self.fifo_position_report.tickers

        if tickers is None:
            raise ValueError(
                "Please provide tickers to the input 'FifoPositionReport' to render the dashboard!"
            )  # pragma: no cover

        tickers = sorted(tickers)
        ticker_selector = pn.widgets.Select(name="Ticker Selector", options=tickers, value="")
        tax_year_selector = pn.widgets.Select(name="Tax Year selector", options=[])

        @pn.depends(ticker=ticker_selector.param.value, year=tax_year_selector.param.value)
        def introduction_markdown(ticker: str | None = None, year: int | None = None) -> pn.pane.Markdown:
            if ticker is None:
                message = "# Please choose a ticker to display it's tax report."
            else:
                possible_years = list(report_df.query(f"TICKER == '{ticker}'").TAX_YEAR.unique())

                if year is None:
                    if len(possible_years) > 0:
                        message = (
                            f"# Report for {ticker}\n\nPlease also choose a tax year from the list of available ones on"
                            " the left."
                        )
                    else:
                        message = f"# Report for {ticker}\n\nNo taxable events detected in the provided history."

                else:
                    message = f"# Report for {ticker} for {year}"
            return pn.pane.Markdown(message, width=1800)

        def update_tax_year_options(event: param.parameterized.Event) -> None:
            available_tax_years = list(report_df.query(f"TICKER == '{event.new}'").TAX_YEAR.unique())
            tax_year_selector.options = available_tax_years

        ticker_selector.param.watch(update_tax_year_options, "value")

        @pn.depends(ticker=ticker_selector.param.value, year=tax_year_selector.param.value)
        def ticker_table_for_tax_year(ticker: str | None = None, year: int | None = None) -> pn.pane.DataFrame:
            if ticker is None or year is None:
                return pn.pane.DataFrame()
            return pn.pane.DataFrame(report_df.query(f"TICKER == '{ticker}' and TAX_YEAR == {year}"), width=1800)

        @pn.depends(ticker=ticker_selector.param.value, year=tax_year_selector.param.value)
        def ticker_result_summary_for_tax_year(ticker: str | None = None, year: int | None = None) -> pn.pane.Markdown:

            if ticker is None or year is None:
                return pn.pane.Markdown(
                    "### Please select a ticker and tax year in the options on the right.", width=1800
                )

            df = report_df.query(f"TICKER == '{ticker}' and TAX_YEAR == {year}")

            num_shares = df.NUM_SHARES.sum()
            currency = df.CURRENCY.unique()[0]
            avg_buy = np.round(df.BUY_PRICE_PER_SHARE.mean(), 2)
            avg_sell = np.round(df.SELL_PRICE_PER_SHARE.mean(), 2)
            result = np.round(df.RESULT.sum(), 2)

            summary = (
                f"For ticker {ticker} and tax year {year}, a total of {num_shares} shares were sold.\n\nThe average"
                " prices are:"
            )
            summary += f"\n\n- buy price: {avg_buy} {currency},\n\n- sell price: {avg_sell} {currency}.\n\n"
            summary += f"The overall result is a {'profit' if result >= 0 else 'loss'} of {result} {currency}."

            return pn.pane.Markdown(summary, width=1800)

        return pn.template.FastListTemplate(
            site="Panel",
            title="FIFO report",
            sidebar=[ticker_selector, tax_year_selector],
            main=[introduction_markdown, ticker_table_for_tax_year, ticker_result_summary_for_tax_year],
        ).servable()
