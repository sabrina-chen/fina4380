import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from pandas_datareader import data


class Performance:
    def __init__(self, NAV):
        self.nav = NAV

    def printarray(self):
        print(np.array(self.nav)[0:10])

    def analyze(self, rf):
        nav = np.array(self.nav).reshape(-1)
        cr = nav[-1] / nav[0] - 1
        ar = (nav[-1] / nav[0]) ** (250 / len(nav)) - 1
        ann_vol = nav.std() * 16
        asr = (ar - rf) / ann_vol
        drawdown = []
        i = 0
        while i < len(nav):
            a = nav[i] / np.amax(nav[0:i]) - 1
            drawdown.append(a)
            i += 1
        md = np.amin(drawdown)
        calmer_ratio = ar / md
        print("Cumulative return: " + str(cr),
              "Annualized geometric return: " + str(ar),
              "Annualized std. : " + str(ann_vol),
              "Annualized Sharpe Ratio: " + str(asr),
              "Max drawdown: " + str(md),
              "Calmer ratio: " + str(calmer_ratio),
              sep="\n")

    def plotting(self, symbol: str):
        # symbol is the benchmark. if we use s&P500 the symbol is sp500
        start_date = datetime.datetime(2016, 1, 1)
        end_date = datetime.datetime(2021, 4, 9)
        benchmark = data.DataReader(symbol, 'fred', start_date, end_date)
        all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')
        # = close.reindex(all_weekdays)
        # close = close.fillna(method='ffill')
        # portfolio_value = [v for v in self.nav if self.nav[self.nav == v].index[0] in all_weekdays]
        # benchmark = [v for v in benchmark if v.date in all_weekdays]
        plt.plot(all_weekdays, self.nav, label='Portfolio')
        plt.plot(all_weekdays, benchmark, label=symbol)

        title = f'Portfolio vs {symbol}'
        plt.title(title)
        plt.legend()
        plt.show()

