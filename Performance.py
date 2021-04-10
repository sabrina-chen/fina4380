import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from pandas_datareader import data


class Performance:
    def __init__(self, NAV):
        self.nav = np.array(NAV).reshape(-1)

    def analyze(self, rf):
        cr = self.nav[-1] / self.nav[0] - 1
        ar = (self.nav[-1] / self.nav[0]) ^ (250 / len(self.nav)) - 1
        ann_vol = self.nav.std() * 16
        asr = (ar - rf) / ann_vol
        drawdown = []
        for i in len(self.nav):
            a = (self.nav[i] / self.nav[0:i].max()) - 1
            drawdown.append(a)
        md = drawdown.min()
        calmer_ratio = ar / md
        print("Cumulative return: " + cr,
              "Annualized geometric return: " + ar,
              "Annualized std. : " + ann_vol,
              "Annualized Sharpe Ratio: " + asr,
              "Max drawdown: " + md,
              "Calmer ratio: " + calmer_ratio,
              sep="\n")

    def plotting(self, symbol: str):
        # symbol is the benchmark. if we use s&P500 the symbol is sp500
        start_date = datetime.datetime(2016, 1, 1)
        end_date = datetime.datetime(2021, 4, 9)
        benchmark = data.DataReader([symbol], 'fred', start_date, end_date)
        all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')
        # = close.reindex(all_weekdays)
        # close = close.fillna(method='ffill')
        portfolio_value = [v for v in self.nav if self.nav[self.nav == v].index[0] in all_weekdays]
        benchmark = [v for v in benchmark if v.date in all_weekdays]
        plt.plot(list(self.nav[self.nav == i].index[0] for i in self.nav),
                 list(i.price for i in self.nav),
                 label='Portfolio')
        plt.plot(list(i.date for i in benchmark),
                 list(i.price for i in benchmark),
                 label=symbol)

        title = f'Portfolio vs {symbol}'
        plt.title(title)
        plt.legend()
        plt.show()
