import time
import urllib.request, json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from bokeh.embed import file_html
from bokeh.models import Range1d, DatetimeTickFormatter
from bokeh.plotting import figure, show
from bokeh.palettes import Category10
from bokeh.resources import CDN

# from bokeh.io import output_notebook
# output_notebook()

server = "http://10.0.0.101/cm?cmnd=Status%208"  
desk   = "http://10.0.0.102/cm?cmnd=Status%208"
delay = 60  ## Seconds, delay between measurements
timer = 0
first_run = True

def get_data(addr, field):
    """Get the contents of field from address"""
    response = (urllib.request.urlopen(addr).read().decode())
    jsn = json.loads(response)
    # print(json.dumps(jstruct, sort_keys=True, indent=4)) #Pretty Print
    return jsn["StatusSNS"]["ENERGY"][field]

def log_data(log_dir="logs"):
    """Log data to log_dir, making new file each day"""
    name_date = datetime.now().strftime("%d_%m_%Y")
    log_path = Path(log_dir) / f"log_{name_date}.txt"

    if not log_path.exists():  # Make a new file for a new date
        newfile = open(log_path, "w")
        newfile.write(
            "Consumption_server (W),"
            "Consumption_server_day (kWh),"
            "Consumption_desk (W),"
            "Consumption_desk_day (kWh),"
            "Timestamp (ISO)"
            "\n"
            )  # Header
        newfile.close()
        print(f"Writing to new file: {log_path}")

    text_num = (
        f"{get_data(server, 'Power')},"
        f"{get_data(server, 'Today')},"
        f"{get_data(desk, 'Power')},"
        f"{get_data(desk, 'Today')},"
        f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}"
        "\n" 
        )

    txt_file = open(log_path, "a")
    txt_file.write(text_num)
    txt_file.close()

    return log_path

def plot_log(log_path, html_path="plot.html"):
    """Generate a html file containing an autorefreshing plot
    of the data in log_path csv.
    """

    data = pd.read_csv(log_path)
    data["Timestamp (ISO)"] = pd.to_datetime(data["Timestamp (ISO)"])
    sensors = ["Server", "Desk"]
    data_dict = {
        "timestamps": data["Timestamp (ISO)"],
        "Server": -data["Consumption_server (W)"],
        "Desk": -data["Consumption_desk (W)"],
    }

    # Rpi Screen is 800*480, but there is some padding
    plot = figure(x_axis_type="datetime", width=790, height=465)
    plot.background_fill_color = "black"
    plot.background_fill_alpha = 1
    plot.border_fill_color = "black"
    plot.border_fill_alpha = 1
    
    plot.vbar_stack(
        sensors,
        x="timestamps",
        source=data_dict,
        width=timedelta(minutes=1),
        legend_label=sensors,
        color=Category10[3][:2],
        )

    # plot.y_range = Range1d(-300, 0) # 300 W display limit
    # plot.x_range = times
    plot.xaxis.formatter=DatetimeTickFormatter(
        hours=["%m-%d %H:%M"],
        days=["%m-%d %H:%M"],
        months=["%m-%d %H:%M"]
    )

    plot.xaxis.axis_label = "Time"
    plot.xaxis.axis_label_text_color = "#333333"
    plot.xaxis.major_label_text_color = "#333333"
    plot.yaxis.axis_label = "Watts"
    plot.yaxis.axis_label_text_color = "#000000"
    plot.yaxis.major_label_text_color = "#000000"

    plot.legend.location = "bottom_right"
    plot.legend.orientation = "horizontal"

    # show(plot)

    html = file_html(plot, CDN, "Power Consumption")
    html_list = html.split("\n") # Add an auto-refresh
    html_list.insert(10, '<meta http-equiv="refresh" content="6" >\n')
    html_new = "".join(html_list)

    with open(html_path, "w") as f:
        f.write(html_new)
        f.close()

    # return html_path

def main():
    while True: 
        log_path = log_data()
        plot_log(log_path)

        time.sleep(delay)

if __name__ == "__main__":
    main()