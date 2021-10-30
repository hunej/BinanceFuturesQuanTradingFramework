
import numpy as np
import matplotlib
import pandas as pd
import datetime
import os.path
import sys
import math
import backtrader as bt

from backtrader_plotting import Bokeh
from backtrader_plotting.schemes import Tradimo
matplotlib.use('QT5Agg')


from enum import Enum
class OrderDirection(Enum):
    NOTHING = 1
    BUY = 2
    SELL = 3

def StrategyN(n):
    return globals()['Strategy'+str(n)]



def Strategy1(df, profit_ratio=2.5):
    pexec = df.tail(1)['close'].values[0]
    direction = OrderDirection.NOTHING
    pslimit = psloss = np.nan
    #insert your strategy here
    return direction, pexec, pslimit, psloss
def Strategy2(df, profit_ratio=2.5):
    pexec = df.tail(1)['close'].values[0]
    direction = OrderDirection.NOTHING
    pslimit = psloss = np.nan
    #insert your strategy here
    return direction, pexec, pslimit, psloss
def Strategy3(df, profit_ratio=2.5):
    pexec = df.tail(1)['close'].values[0]
    direction = OrderDirection.NOTHING
    pslimit = psloss = np.nan
    #insert your strategy here
    return direction, pexec, pslimit, psloss



    
# Create a Stratey
class TestStrategy(bt.Strategy):
    params = (
        ('Strategy_idx', 1),
        ('backtest_days', 6),
        ('len_df', 10),        
    )

        
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime[0]
        dt = bt.num2date(dt)
        print('%s(%d), %s' % (dt.isoformat(), self.nextcount, txt), file=self.f)

    def __init__(self):
        print('Strategy_idx'+str(self.p.Strategy_idx))
        self.outputpath = 'output.txt'
        self.f = open(self.outputpath, 'w')        
        # self.profit_ratio = 2.5
        self.singleposloss = 5.0
        self.nextcount = 0
        self.dataclose = self.datas[0].close
        # self.lastcounttrade = 4000
        
        # To keep track of pending orders
        self.order = list()
        self.order_executed_price = None
        self.order_takeprofit_price = None
        self.order_stoploss_price = None
        self.order_size = None
        self.sma = bt.indicators.SimpleMovingAverage(period=self.p.len_df-24*self.p.backtest_days)#dummy for prepare data
    
        
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.8f | CURRENT POSITION: %.8f' %(order.executed.price, self.getposition(self.data).size))
            elif order.issell():
                self.log('SELL EXECUTED, %.8f | CURRENT POSITION: %.8f' %(order.executed.price, self.getposition(self.data).size))#, cerebro.broker.getvalue()

            self.bar_executed = len(self)

        elif order.status in [order.Canceled]:
            self.log('Order Canceled')
        elif order.status in [order.Margin]:
            self.log('Order Margin')
        elif order.status in [order.Rejected]:
            self.log('Order Rejected')            

        # Write down: no pending order
        self.order = None
        
    def stop(self):
        self.order = self.order_target_size(target=0)        
        self.log('STOP')
        self.log('CURRENT POSITION: %.8f' %self.getposition(self.data).size)
        self.log('TEST COUNT: %d' %self.nextcount)
        self.f.close()
      
    def next(self):        
        self.nextcount = self.nextcount + 1
        self.log('Close, %.8f' %(self.dataclose[0]))
        
        if self.order:
            return


        # Check if we are in the market
        if not self.position:
            # print(len(self.dataclose))
            # print(self.datas[0].datetime.get(size=len(self.dataclose)))
            coldata_time = self.data.datetime.get(size=len(self.dataclose))
            coldata_open = self.data.open.get(size=len(self.dataclose))
            coldata_high = self.data.high.get(size=len(self.dataclose))
            coldata_low = self.data.low.get(size=len(self.dataclose))
            coldata_close = self.data.close.get(size=len(self.dataclose))
            coldata_volume = self.data.volume.get(size=len(self.dataclose))
            df_new = pd.DataFrame({'open': coldata_open,
                                   'high': coldata_high,
                                   'low': coldata_low,
                                   'close': coldata_close,
                                   'volume': coldata_volume})
            df_new.index = pd.to_datetime(df_new.index, format = '%Y-%m-%d %H:%M:%S')
            df_new.index.name = 'dateTime'

            direction, pexec, pslimit, psloss =  StrategyN(self.p.Strategy_idx)(df_new)

            
            #sanity check
            if direction == OrderDirection.BUY and (pexec<psloss or pslimit<pexec):
                direction = OrderDirection.NOTHING
            elif direction == OrderDirection.SELL and (pexec>psloss or pslimit>pexec):
                direction = OrderDirection.NOTHING
                    
            if direction == OrderDirection.BUY:
                self.order_size = self.singleposloss/(pexec-psloss)
                self.log('BUY CREATE, (price: %.8f, pos: %.8f, cost: %.8f, lim: %.8f, sl: %.8f)' %(pexec,
                    self.order_size,
                    pexec*self.order_size,
                    pslimit,
                    psloss))
                self.order = self.buy_bracket(
                    price=pexec, size=self.order_size,
                    stopprice=psloss,
                    limitprice=pslimit)
            
            
            
            elif direction == OrderDirection.SELL:  
                self.order_size = self.singleposloss/(psloss-pexec)
                self.log('SELL CREATE, (price: %.8f, pos: %.8f, cost: %.8f, lim: %.8f, sl: %.8f)' %(pexec,
                    self.order_size,
                    pexec*self.order_size,
                    pslimit,
                    psloss))                    
                self.order = self.sell_bracket(
                    price=pexec, size=self.order_size,
                    stopprice=psloss,
                    limitprice=pslimit)
            



# Create a cerebro entity
   
def run_backtest(target_pair, Strategy_idx, backtest_days):
    cerebro = bt.Cerebro()
    # df.to_csv('rawdata.csv',index=False)
    df = pd.read_csv('./1h_all/' + target_pair + '.csv', index_col="dateTime", infer_datetime_format=True, parse_dates=True)
    df = df[["open", "high", "low", "close", "volume"]]
    df.columns = ["Open", "High", "Low", "Close", "Volume"]
    # df = df.tail(24*30*2)#60days backtest
    
    df.to_csv('./backtest/' + target_pair + '.csv')
    
    
    

    

    
    # Add a strategy
    cerebro.addstrategy(TestStrategy, Strategy_idx=Strategy_idx, backtest_days=backtest_days, len_df=len(df))
    

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, './backtest/' + target_pair + '.csv')
    
    rawdata = bt.feeds.GenericCSVData(
                    dataname=datapath,
                    dtformat=('%Y-%m-%d %H:%M:%S'),
                    name='rawdata',
                    openinterest=-1
                    )
    cerebro.adddata(rawdata)
    
    
    cerebro.resampledata(
                    rawdata, 
                    timeframe=bt.TimeFrame.Days, #timeframe=bt.TimeFrame.Minutes, 
                    compression=1, #compression=60*8, 
                    name='daydata'
                    )#8HR S/R
    # cerebro.adddata(pivotdata)
    
    cerebro.addobserver(bt.observers.Benchmark,
                                timeframe=bt.TimeFrame.Weeks
                                )
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")

    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")
        # 1.6 - 1.9 Below average
        # 2.0 - 2.4 Average
        # 2.5 - 2.9 Good
        # 3.0 - 5.0 Excellent
        # 5.1 - 6.9 Superb
        # 7.0 - Holy Grail?
    
    # Set our desired cash start
    cerebro.broker.setcash(162*10.0)
    
    
    
    # Print out the starting conditions
    print('Starting Portfolio Value: %.8f' % cerebro.broker.getvalue())
    myportfolio = cerebro.broker.getvalue()
    # Run over everything
    # cerebro.run(runonce=False)
    strategies = cerebro.run()
    firstStrat = strategies[0]
    
    # Print out the final result
    print('Final Portfolio Value: %.8f' % cerebro.broker.getvalue())
    myportfolio = cerebro.broker.getvalue() - myportfolio
    # cerebro.plot(style="candle", iplot=False)
    
    # b = Bokeh(filename='chart.html', style='bar', plot_mode='single', scheme=Tradimo())
    # cerebro.plot(b, iplot=False)
    
    
    
    sqn = firstStrat.analyzers[1].get_analysis()['sqn']
    trades = firstStrat.analyzers[1].get_analysis()['trades']

    
    return sqn, trades, myportfolio

if __name__ == '__main__':
    
    try:
        target_pair = (sys.argv[1])
        Strategy_idx = (sys.argv[2])
        backtest_days = (sys.argv[3])
    except:
        target_pair = "BTCUSDT"
        Strategy_idx = 3#3:0.6, 4:0.3
        backtest_days = 7
        
    run_backtest(target_pair, Strategy_idx, backtest_days)
        