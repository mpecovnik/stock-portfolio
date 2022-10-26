from queue import Queue
from typing import Dict, List, Optional, TypeVar

import numpy as np
import pandas as pd
import panel as pn
import param
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.formatters import PrintfTickFormatter
from bokeh.plotting import Figure, figure

from sp.testing.env import PRECISION_GUARD
from sp.tracker.core.class_model import BaseModel
from sp.tracker.data.history import PositionHistory
from sp.tracker.reports.model import ReportBaseModel

A = TypeVar("A", bound="Action")


class Action(BaseModel):
    type: str
    date: str
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
    history: PositionHistory

    def create_report_in_full(self) -> pd.DataFrame:
        ...  # pragma: no cover

    def create_report_by_ticker(self, ticker: str) -> pd.DataFrame:
        ticker_position_history = self.history.read(f"Ticker == '{ticker}'").sort_values("Time")

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


class FifoPositionDashboard(BaseModel):
    fifo_position_report: FifoPositionReport
    display_width: int = 1800

    def plot(self, year: int, report_df: Optional[pd.DataFrame] = None) -> Figure:

        if report_df is None:
            report_df = self.fifo_position_report.create_report()

        ticker_name_map = report_df[["TICKER", "NAME"]].drop_duplicates()

        results = report_df.query(f"TAX_YEAR == {year}").groupby("TICKER", as_index=False)["RESULT"].sum()
        results_with_names = pd.merge(results, ticker_name_map, on="TICKER", how="left")
        results_with_names = results_with_names.set_index("TICKER")
        results_with_names.loc[:, "COLOR"] = np.where(results_with_names.loc[:, "RESULT"] >= 0, "green", "red")
        results_with_names = results_with_names.sort_values("RESULT")

        results_with_names["running_total"] = results_with_names["RESULT"].cumsum()
        results_with_names["y_start"] = results_with_names["running_total"] - results_with_names["RESULT"]

        results_with_names["label_pos"] = results_with_names["y_start"].copy()
        results_with_names["bar_label"] = results_with_names["RESULT"].map("{:,.0f}".format)

        total_result = results_with_names.RESULT.sum()
        results_with_names.loc["Total", ["RESULT", "NAME", "COLOR", "y_start", "running_total"]] = (
            total_result,
            "Total",
            "green" if total_result > 0 else "red",
            0,
            total_result,
        )
        results_with_names = results_with_names.reset_index()

        plot_width = self.display_width
        padding_perc = 25
        column_width = (plot_width / len(results_with_names)) / (1 + padding_perc / 100)

        TOOLS = "box_zoom,reset,save"

        hover = HoverTool(
            tooltips=[
                ("ticker", "@TICKER"),
                ("name", "@NAME"),
                ("result", "@RESULT{%0.2f €}"),
            ],
            formatters={
                "@RESULT": "printf",
            },
            mode="vline",
        )

        source = ColumnDataSource(results_with_names)
        p = figure(
            tools=TOOLS,
            x_range=list(results_with_names.TICKER),
            y_range=(results_with_names.running_total.min() * 1.1, results_with_names.running_total.max() * 1.1),
            plot_width=plot_width,
            title="Tax report per ticker for year 2020",
        )
        p.add_tools(hover)

        p.segment(
            x0="TICKER",
            y0="y_start",
            x1="TICKER",
            y1="running_total",
            source=source,
            color="COLOR",
            line_width=column_width,
        )

        p.grid.grid_line_alpha = 0.3
        p.yaxis[0].formatter = PrintfTickFormatter(format="%0.2f €")
        p.xaxis.axis_label = "Tickers"
        p.yaxis.axis_label = "Result"
        p.xaxis.major_label_orientation = "vertical"

        return p

    def serve_dashboard(self) -> param.Parameterized:

        report_df = self.fifo_position_report.create_report()
        currency = "EUR"

        year_options = self.fifo_position_report.years
        if year_options is None:
            raise ValueError(
                "Please provide 'year_options' to the input 'FifoPositionReport' to render the dashboard!"
            )  # pragma: no cover

        tax_year_selector = pn.widgets.Select(name="Tax Year selector", options=year_options)
        available_tickers = list(report_df.query(f"TAX_YEAR == {tax_year_selector.value}").TICKER.unique())
        ticker_selector = pn.widgets.Select(name="Ticker Selector", options=available_tickers)

        @pn.depends(year=tax_year_selector.param.value)
        def year_report_image(year: int | None = None) -> pn.pane.Bokeh | pn.pane.Markdown | None:

            if year is None:
                return None

            if report_df.query(f"TAX_YEAR == {year}").empty:
                return pn.pane.Markdown(
                    "### Nothing to display, since to taxable events occured.", width=self.display_width
                )

            return pn.pane.Bokeh(self.plot(year=year, report_df=report_df), width=self.display_width)

        @pn.depends(ticker=ticker_selector.param.value, year=tax_year_selector.param.value)
        def introduction_markdown(ticker: str | None = None, year: int | None = None) -> pn.pane.Markdown:

            if year is None:
                if report_df.TAX_YEAR.nunique() > 0:
                    message = "# Please choose a year to display the available tickers."
            else:
                if ticker is None:
                    message = "# Please choose a ticker to display it's tax report."
                else:
                    name = report_df.query(f"TICKER == '{ticker}'").NAME.unique()[0]
                    message = f"# Report for {name} ({ticker}) for {year}"
            return pn.pane.Markdown(message, width=self.display_width)

        def update_ticker_options(event: param.parameterized.Event) -> None:
            available_tickers = list(report_df.query(f"TAX_YEAR == {event.new}").TICKER.unique())
            ticker_selector.options = available_tickers

        tax_year_selector.param.watch(update_ticker_options, "value")

        @pn.depends(ticker=ticker_selector.param.value, year=tax_year_selector.param.value)
        def ticker_table_for_tax_year(ticker: str | None = None, year: int | None = None) -> pn.pane.DataFrame | None:
            if ticker is None or year is None:
                return None
            return pn.pane.DataFrame(
                report_df.query(f"TICKER == '{ticker}' and TAX_YEAR == {year}"), width=self.display_width, index=False
            )

        @pn.depends(ticker=ticker_selector.param.value, year=tax_year_selector.param.value)
        def ticker_result_summary_for_tax_year(ticker: str | None = None, year: int | None = None) -> pn.pane.Markdown:

            if ticker is None or year is None:
                return pn.pane.Markdown(
                    "### Please select a ticker and tax year in the options on the right.", width=self.display_width
                )

            df = report_df.query(f"TICKER == '{ticker}' and TAX_YEAR == {year}")

            num_shares = df.NUM_SHARES.sum()
            name = df.NAME.unique()[0]
            avg_buy = df.BUY_PRICE_PER_SHARE.mean()
            avg_sell = df.SELL_PRICE_PER_SHARE.mean()
            result = df.RESULT.sum()

            summary = (
                f"For ticker {name} ({ticker}) and tax year {year}, a total of {num_shares:.5f} shares were"
                " sold.\n\nThe average prices are:"
            )
            summary += f"\n\n- buy price: {avg_buy:.2f} {currency},\n\n- sell price: {avg_sell:.2f} {currency}.\n\n"
            summary += f"The overall result is a {'profit' if result >= 0 else 'loss'} of {result:.2f} {currency}."

            return pn.pane.Markdown(summary, width=self.display_width)

        return pn.template.FastListTemplate(
            site="Panel",
            title="FIFO report",
            sidebar=[tax_year_selector, ticker_selector],
            main=[
                year_report_image,
                introduction_markdown,
                ticker_table_for_tax_year,
                ticker_result_summary_for_tax_year,
            ],
        ).servable()
