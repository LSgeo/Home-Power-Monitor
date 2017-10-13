"""SolarPiPy 2.0 - Luke Smith 2017

This is yet another Home power monitoring script.
Designed for use with Enphase Envoy S power monitor, which measures Solar and
Grid power statistics, and outputs a JSON web page over the local network.
This script is designed to be run on a RPi, especially with an attached screen.
It may eventually power a web page, and/or home automation.

For now, it will simply plot power statisitcs and weather.
"""

import time
import os.path
import requests
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
