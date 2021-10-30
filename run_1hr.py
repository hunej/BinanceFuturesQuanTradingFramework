# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 13:59:22 2021

@author: 27zig
"""
import sys
import numpy as np
import pandas as pd
from barloader.barloader import BarLoader
from binance.client import Client
from datetime import datetime, timedelta

from myorder import mybuy, mysell

import requests
import configparser
import pickle

import mybacktest

def fetch_kline(target_pair):
    print("fetch_kline")
    # fetch newest 1hr kline
    bl = BarLoader()
    api_key = 'api_key'
    api_secret = 'api_secret'
    client = Client(api_key, api_secret)
    bl.binance([target_pair], client=client, start=datetime.now() - timedelta(hours = 40), interval='1h')
    

    # merge kline data
    df_origin = pd.read_csv('./1h_all/' + target_pair + '.csv', index_col="dateTime", infer_datetime_format=True, parse_dates=True)
    df_origin = df_origin[["close", "volume", "open", "high", "low"]]
    
    df_new = pd.read_csv('./1h/' + target_pair + '.csv', index_col="dateTime", infer_datetime_format=True, parse_dates=True)
    df_new = df_new[["close", "volume", "open", "high", "low"]] 
    
    

    # pandas merge
    df_merge = df_origin.append(df_new)
    df_merge.sort_values('dateTime', inplace=True)
    df_merge = df_merge[~df_merge.index.duplicated()]

    newest = df_merge.tail(1)
    print(newest)
    
    df_merge.drop(df_merge.tail(1).index,inplace=True) # drop last rows(current data)
    df_merge.to_csv('./1h_all/' + target_pair + '.csv')
    
    return newest, df_merge




    
def run_1hr(singleposloss=5.0, pr=2.0, target_pair = "BTCUSDT"):
    
    report_file = open("strategy_report.pkl", "rb")
    report_pkl = pickle.load(report_file)
    
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    token = config.get('line-bot', 'token')    
    
    
    print(target_pair)
    
    
    newest_df, df_merge = fetch_kline(target_pair)
    
    
    
    
    try:
        target_strategy = report_pkl[target_pair]

    
        message_body = target_pair + ': use ' + target_strategy
        direction, pexec, pslimit, psloss = getattr(mybacktest, target_strategy)(df=df_merge)
    
    
        #sanity check
        if direction == mybacktest.OrderDirection.BUY and (pexec<psloss or pslimit<pexec):
            direction = mybacktest.OrderDirection.NOTHING
        elif direction == mybacktest.OrderDirection.SELL and (pexec>psloss or pslimit>pexec):
            direction = mybacktest.OrderDirection.NOTHING
                
        if direction == mybacktest.OrderDirection.BUY:
            order_size = singleposloss/(pexec-psloss)
            message_body = message_body + (', BUY CREATE, (price: %.5f, pos: %.2f, cost: %.3f, lim: %.5f, sl: %.5f)' %(pexec,
                order_size,
                pexec*order_size,
                pslimit,
                psloss))
            mybuy(target_pair, pexec, pslimit, psloss, singleposloss)
        
        
        
        elif direction == mybacktest.OrderDirection.SELL:  
            order_size = singleposloss/(psloss-pexec)
            message_body = message_body + (', SELL CREATE, (price: %.5f, pos: %.2f, cost: %.3f, lim: %.5f, sl: %.5f)' %(pexec,
                order_size,
                pexec*order_size,
                pslimit,
                psloss))                    
            mysell(target_pair, pexec, pslimit, psloss, singleposloss)
            
        else:
            message_body = message_body + ', DO NOTHING'
    except:
        message_body = target_pair + ': no strategy avaliable'
 

    if message_body != False:
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        
        params = {"message": message_body}
    
        r = requests.post("https://notify-api.line.me/api/notify",
                        headers=headers, params=params)
        print(r.status_code)  #200
    
    
    

if __name__ == "__main__":
    try:
        target_pair = (sys.argv[1])
    except:
        target_pair = "BTCUSDT"
    print(target_pair)
    run_1hr(singleposloss=5.0, pr=2.0, target_pair = target_pair)
