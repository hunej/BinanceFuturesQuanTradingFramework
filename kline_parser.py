#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 20:57:12 2021

@author: 27zig
"""


from barloader.barloader import BarLoader
from binance.client import Client
from datetime import datetime, timedelta

bl = BarLoader()
api_key = 'api_key'
api_secret = 'api_secret'
client = Client(api_key, api_secret)


start = datetime(2016, 1, 1)
interval = '1h'


bl.binance(['BTCUSDT', 'ETHUSDT', '1000SHIBUSDT', 'SOLUSDT', 'DOGEUSDT', 'FTMUSDT', 'AXSUSDT', 'DOTUSDT', 'LINKUSDT', 'XRPUSDT', 'ONEUSDT', 'ADAUSDT'], 
           client=client, start=start, interval=interval)



