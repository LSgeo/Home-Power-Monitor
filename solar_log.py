from datetime import datetime, timedelta
import urllib.request, json, time
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html

server = "http://10.0.0.101/cm?cmnd=Status%208"  # IP of Enovy s energy meter
desk   = "http://10.0.0.102/cm?cmnd=Status%208"
delay = 3  ## Seconds, delay between measurements
timer = 0
first_run = True

print("Program Running...")

while True:
    ## Getting data off Envoy S
    # get html object, read it and decode it from byte to str
    envoy_str = (urllib.request.urlopen(server).read().decode())
    envoy_jsn = json.loads(envoy_str)
    # print(json.dumps(jstruct, sort_keys=True, indent=4)) #Pretty Print the structure
    s_cons_wnow = envoy_jsn["StatusSNS"]["ENERGY"]["Power"]
    s_cons_day  = envoy_jsn["StatusSNS"]["ENERGY"]["Today"]  # Net power

    desk_str = (urllib.request.urlopen(desk).read().decode())
    desk_jsn = json.loads(desk_str)
    # print(json.dumps(jstruct, sort_keys=True, indent=4)) #Pretty Print the structure
    d_cons_wnow = desk_jsn["StatusSNS"]["ENERGY"]["Power"]
    d_cons_day  = desk_jsn["StatusSNS"]["ENERGY"]["Today"]  # Net power

    ## Print to Text File
    name_date = time.strftime("%d_%m_%Y")
    log_path = Path(f"logs/log_{name_date}.txt")
    if not log_path.exists():  # Make a new file for a new date
        newfile = open(log_path, "w")
        newfile.write("Consumption_server (W), Consumption_desk (W), H:M:S\n")  # Header
        newfile.close()
        print(f"Writing to new file: {log_path}")
    text_num = f"{s_cons_wnow}, {d_cons_wnow}, {time.strftime('%H:%M:%S')}" 
    txt_file = open(log_path, "a")
    txt_file.write(f'{text_num}\n')
    txt_file.close()

    time.sleep(delay)

    data = np.genfromtxt(
        log_path,
        delimiter=",",
        skip_header=1,
        names=["Consumption_s", "Consumption_d"],
        usecols=(0, 1),
    )

    timestamp = np.loadtxt(log_path, dtype="U", delimiter=",", skiprows=1, usecols=(2))
    times = [datetime.strptime(t, " %H:%M:%S") for t in timestamp]
    x = mpl.dates.date2num(times)
    tfmt = mpl.dates.DateFormatter(" %H:%M:%S")

    plot = figure()
    plot.vbar(x, top=-data["Consumption_s"], width=0.0002)
    plot.vbar(x, top=-data["Consumption_d"], width=0.0002)
    html = file_html(plot, CDN, "my plot")
    html_list = html.split("\n")
    html_list.insert(10, '<meta http-equiv="refresh" content="10" >\n')

    html_new = "".join(html_list)

    with open("derp.html", "w") as file1:
        file1.write(html_new)
        file1.close()
