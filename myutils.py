# -*- coding: utf-8 -*-
"""
Created on Thu Oct 28 14:41:20 2021

@author: 27zig
"""
import numpy as np
# import pandas as pd

def split_series(series, n_past, n_future):
    #
    # n_past ==> no of past observations
    #
    # n_future ==> no of future observations 
    #
    X, y = list(), list()
    for window_start in range(len(series)):
        past_end = window_start + n_past
        future_end = past_end + n_future
        if future_end > len(series):
          break
        # slicing the past and future parts of the window
        past, future = series[window_start:past_end, :], series[past_end:future_end, :]
        X.append(past)
        y.append(future)
    return np.array(X), np.array(y)


def pd_update(df1, df2):
    # pandas merge
    df1.combine(df2, np.minimum)
    return df1