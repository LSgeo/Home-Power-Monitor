from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.models import DatetimeTickFormatter, LinearAxis, Range1d
from bokeh.plotting import figure, curdoc, ColumnDataSource
from bokeh.palettes import Category10
from bokeh.server.server import Server

PRICE_PER_KWH = 0.322957


if 1: # __name__ == "__main__":

    def make_document(doc, log_path="logs/log.txt"):
        """Generate a html file containing an autorefreshing plot
        of the data in log_path csv.
        """

        data_dict = {
            "timestamps": [],
            "Server": [],
            "Desk": [],
            "Kasa": [],
            "Today": [],
        }
        source = ColumnDataSource(data_dict)

        def update():
            data = pd.read_csv(log_path)
            data["Timestamp (ISO)"] = pd.to_datetime(data["Timestamp (ISO)"])
            sensors = ["Server", "Desk", "Kasa"]
            new_data = {
                "timestamps": data["Timestamp (ISO)"],
                "Server": -data["Consumption_server (W)"],
                "Desk": -data["Consumption_desk (W)"],
                "Kasa": -data["Consumption_kasa (W)"],
                "Today": (
                    PRICE_PER_KWH
                    * (
                        -data["Consumption_desk_total (kWh)"]
                        - data["Consumption_server_total (kWh)"]
                        - data["Consumption_kasa_total (kWh)"]
                    )
                ),
            }

            source.stream(new_data)

        doc.addperiodic_callback(update, 61000)  # 1 minute 1 sec

        plot = figure(
            x_axis_type="datetime",
            sizing_mode="scale_width",
        )
        plot.background_fill_color = "black"
        plot.background_fill_alpha = 1
        plot.border_fill_color = "black"
        plot.border_fill_alpha = 1

        plot.y_range = Range1d(-1000, 0)  # 1 kW display limit
        plot.vbar_stack(
            sensors,
            source=source,
            x="timestamps",
            width=timedelta(seconds=50),
            legend_label=sensors,
            color=Category10[3],
        )
        plot.yaxis.axis_label = "Watts"

        plot.extra_y_ranges["cumulative"] = Range1d(start=-20, end=0)
        plot.add_layout(
            LinearAxis(y_range_name="cumulative", axis_label="Cumulative $"), "right"
        )
        plot.line(
            x=source["timestamps"],
            y=source["Today"],
            y_range_name="cumulative",
            legend_label="Cumulative",
            line_width=2.5,
            color="#DDBBBB",  # "#2CA02C",
        )

        # plot.x_range = times
        plot.xaxis.formatter = DatetimeTickFormatter(
            hours="%m-%d %H:%M", days="%m-%d %H:%M", months="%m-%d %H:%M"
        )
        plot.xaxis.axis_label = "Time"
        plot.xaxis.axis_label_text_color = "#BBBBBB"
        plot.xaxis.major_label_text_color = "#BBBBBB"
        plot.yaxis.axis_label_text_color = "#BBBBBB"
        plot.yaxis.major_label_text_color = "#BBBBBB"

        plot.legend.location = "bottom_left"
        plot.legend.orientation = "horizontal"

        doc.title("Power meter data")
        doc.add_root(plot)
        # show(plot)

    apps = {"/": Application(FunctionHandler(make_document))}

    server = Server(apps, port=5006)
    server.start()
