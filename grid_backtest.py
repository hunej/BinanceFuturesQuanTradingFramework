#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 02:52:38 2021

@author: 27zig
"""
import pickle
from mybacktest import run_backtest

pairlist = ['BTCUSDT', 'ETHUSDT', '1000SHIBUSDT', 'SOLUSDT', 'DOGEUSDT', 'FTMUSDT', 'AXSUSDT', 'DOTUSDT', 'LINKUSDT', 'XRPUSDT', 'ONEUSDT', 'ADAUSDT']
report_all = {}
for target_pair in pairlist:
    report_target = {}
    print(target_pair)
    for Strategy_idx in range(1,3+1):#assume total 3 strategies
        sqn, trades, portfolio = run_backtest(target_pair, Strategy_idx=Strategy_idx, backtest_days=7)
        report_target['Strategy' + str(Strategy_idx)] = [sqn, trades, portfolio]
    report_all[target_pair] = report_target
        
    
best_strategy = {}
for target_pair in pairlist:
    sqn_max = 0
    for st in report_all[target_pair]:
        if report_all[target_pair][st][0]>sqn_max:
            sqn_max = report_all[target_pair][st][0]
            best_strategy[target_pair] = st
            
a_file = open("strategy_report.pkl", "wb")
pickle.dump(best_strategy, a_file)     
