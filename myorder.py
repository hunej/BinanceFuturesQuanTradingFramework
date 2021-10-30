#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 23:19:15 2021

@author: 27zig
"""

import binance_f

from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
from binance_f.model.constant import *


        


def mybuy(target_pair, order_executed_price, order_takeprofit_price, order_stoploss_price, singleposloss):
    order_executed_price = order_executed_price*0.99#delay entry
    api_key = 'api_key'
    api_secret = 'api_secret'
    
    order_size = singleposloss/(order_executed_price-order_stoploss_price)
        
        
    try:
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        info = request_client.get_exchange_information()
        for i in range(len(info.symbols)):
            if info.symbols[i].symbol==target_pair:
                pricePrecision = info.symbols[i].pricePrecision
                quantityPrecision = info.symbols[i].quantityPrecision
        
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.change_initial_leverage(symbol=target_pair, leverage=10)
        PrintBasic.print_obj(result)
        

        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.get_open_orders()
        PrintMix.print_data(result)
        order_count = 0
        for i in range(len(result)):
            if result[i].symbol==target_pair:
                order_count = order_count + 1
        if order_count == 2:#assume SL+TP
            print('position already opened')
            return
        else:
            request_client = RequestClient(api_key=api_key, secret_key=api_secret)
            result = request_client.cancel_all_orders(symbol=target_pair)
            PrintBasic.print_obj(result)
                
                
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.post_order(symbol=target_pair, side=OrderSide.BUY, ordertype=OrderType.LIMIT, quantity='{:0.0{}f}'.format(order_size, quantityPrecision), price='{:0.0{}f}'.format(order_executed_price, pricePrecision), timeInForce=TimeInForce.GTC)
        PrintBasic.print_obj(result)
        
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.post_order(symbol=target_pair, side=OrderSide.SELL, ordertype=OrderType.STOP_MARKET, stopPrice='{:0.0{}f}'.format(order_stoploss_price, pricePrecision), closePosition=True)
        PrintBasic.print_obj(result)
        
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.post_order(symbol=target_pair, side=OrderSide.SELL, ordertype=OrderType.TAKE_PROFIT_MARKET, stopPrice='{:0.0{}f}'.format(order_takeprofit_price, pricePrecision), closePosition=True)
        PrintBasic.print_obj(result)
    except:
        print("except")


def mysell(target_pair, order_executed_price, order_takeprofit_price, order_stoploss_price, singleposloss):
    order_executed_price = order_executed_price*1.01#delay entry
    api_key = 'api_key'
    api_secret = 'api_secret'
    
    order_size = singleposloss/(order_stoploss_price-order_executed_price)
        
        
    try:
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        info = request_client.get_exchange_information()
        for i in range(len(info.symbols)):
            if info.symbols[i].symbol==target_pair:
                pricePrecision = info.symbols[i].pricePrecision
                quantityPrecision = info.symbols[i].quantityPrecision
                
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.change_initial_leverage(symbol=target_pair, leverage=10)
        PrintBasic.print_obj(result)
        
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.get_open_orders()
        PrintMix.print_data(result)
        order_count = 0
        for i in range(len(result)):
            if result[i].symbol==target_pair:
                order_count = order_count + 1
        if order_count == 2:#assume SL+TP
            print('position already opened')
            return
        else:
            request_client = RequestClient(api_key=api_key, secret_key=api_secret)
            result = request_client.cancel_all_orders(symbol=target_pair)
            PrintBasic.print_obj(result)    
                
                
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.post_order(symbol=target_pair, side=OrderSide.SELL, ordertype=OrderType.LIMIT, quantity='{:0.0{}f}'.format(order_size, quantityPrecision), price='{:0.0{}f}'.format(order_executed_price, pricePrecision), timeInForce=TimeInForce.GTC)
        PrintBasic.print_obj(result)
        
        
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.post_order(symbol=target_pair, side=OrderSide.BUY, ordertype=OrderType.STOP_MARKET, stopPrice='{:0.0{}f}'.format(order_stoploss_price, pricePrecision), closePosition=True)
        PrintBasic.print_obj(result)
        
        request_client = RequestClient(api_key=api_key, secret_key=api_secret)
        result = request_client.post_order(symbol=target_pair, side=OrderSide.BUY, ordertype=OrderType.TAKE_PROFIT_MARKET, stopPrice='{:0.0{}f}'.format(order_takeprofit_price, pricePrecision), closePosition=True)
        PrintBasic.print_obj(result)    
    except:
        print("except")
