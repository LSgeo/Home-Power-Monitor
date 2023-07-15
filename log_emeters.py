#!/home/luke/Home-Power-Monitor/home/bin/python3

import asyncio
import json
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError

import kasa
from kasa import SmartPlug


desk = "http://10.0.0.101/cm?cmnd=Status%208"
server = "http://10.0.0.102/cm?cmnd=Status%208"
kasa_addr = "10.0.0.59"

price_per_kwh = 0.322957  # 2023 Synergy AUD/kWh
delay = 60  # Seconds, delay between measurements
timer = 0
first_run = True


def get_data(addr: str, field: str) -> str:
    """Get the contents of field from address"""
    response = urllib.request.urlopen(addr).read().decode()
    jsn = json.loads(response)
    # print(json.dumps(jstruct, sort_keys=True, indent=4)) #Pretty Print
    return str(jsn["StatusSNS"]["ENERGY"][field])


def get_kasa_data(dev: SmartPlug, field: str) -> str:
    """Query Kasa device using python-kasa
    https://github.com/python-kasa/python-kasa
    """
    if dev is None:
        return "0"

    if not dev.has_emeter:
        raise ValueError(f"Device {dev} does not support energy monitoring")

    e = dev.emeter_realtime

    return dict(Power=e.power, Total=e.total)[field]


def log_data(log_dir: str = "logs", kasa_dev=None) -> Path:
    """Log data to log_dir, making new file each month"""
    name_date = ""  # datetime.now().strftime("%m_%Y")
    log_path = Path(log_dir) / f"log{name_date}.txt"

    if not log_path.exists():  # Make a new file for a new date
        newfile = open(log_path, "w")
        newfile.write(
            "Consumption_server (W),"
            "Consumption_server_total (kWh),"
            "Consumption_desk (W),"
            "Consumption_desk_total (kWh),"
            "Consumption_kasa (W),"
            "Consumption_kasa_total (kWh),"
            "Timestamp (ISO)"
            "\n"
        )  # Header
        newfile.close()
        print(f"Writing to new file: {log_path}")

    text_num = (
        f"{get_data(server, 'Power')},"
        f"{get_data(server, 'Total')},"
        f"{get_data(desk, 'Power')},"
        f"{get_data(desk, 'Total')},"
        f"{get_kasa_data(kasa_dev, 'Power')},"
        f"{get_kasa_data(kasa_dev, 'Total')},"
        f"{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}"
        "\n"
    )

    txt_file = open(log_path, "a")
    txt_file.write(text_num)
    txt_file.close()

    return log_path


async def main():
    try:
        dev = SmartPlug(kasa_addr)
        await dev.update()
    except kasa.exceptions.SmartDeviceException:
        dev = None

    while True:
        try:
            if dev is not None:
                await dev.update()
            log_data(kasa_dev=dev)
            await asyncio.sleep(delay)
        except (HTTPError, ConnectionResetError, URLError):
            await asyncio.sleep(300)  # 5 minute time out to try again


if __name__ == "__main__":
    asyncio.run(main())
