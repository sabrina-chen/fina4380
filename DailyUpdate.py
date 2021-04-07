# Tentative structure of class dailyUpdate
# new DailyUpdate() object is created every day

import pandas as pd

class DailyUpdate:
    def __init__(self, logreturns, tickers, portfolio=None):    # logreturns of past 1 year (for testing)
        # example of portfolio (and newPort): (in pd.DataFrame() form?)
        # [[stock-A1, industry-A, weight-A1], 
        #  [stock-A2, industry-A, weight-A2],
        #  [stock-B1, industry-B, weight-B1],
        #  [stock-B2, industry-B, weight-B2], ...]
        
        self.logreturns = logreturns.copy()
        if portfolio is not None:
            self.port = portfolio.copy()
        else:
            self.port = pd.DataFrame()
        self.tickers = tickers
        self.newPort = pd.DataFrame()

    def rebalancing(self):
        # for each pair of current portfolio:
        #     1st regression: find current epsilon
        #     2nd regression (ADF test) using epsilon: find t-stat
        #     if some condition is met (epsilon mean reversed or t-stat increased or return reached some percentage(may need to get extra data from main.py)):
        #         self.newPort.append(findPair(industry))    # current portfolio using findPair()
        #     else:
        #         self.newport.append(currentpair)
        pass

    def findPair(self):    # find pairs of stock where arbitrage exists "within industry groups"
        # for each pair of stocks in industry:
        #     2-stage regression find cointegration ratio and t-stat
        # sort t-stat
        # find |epsilon| > 3%(?) from smallest t-stat
        # result = {"pair": [stockA, stockB], "beta": cointegration ratio, "tstat": t-stat}
        # return result
        pass

    def getUpdatedPort(self):
        return self.newPort

