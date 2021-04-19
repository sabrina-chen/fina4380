import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, MonthLocator


class Performance:
    def __init__(self, NAV):
        self.nav = NAV
        self.daily_return = NAV.pct_change()

    def analyze(self, rf):
        nav = np.array(self.nav)
        cr = nav[-1] / nav[0] - 1
        ar = (nav[-1] / nav[0]) ** (250 / len(nav)) - 1
        daily_return = np.array(self.daily_return)
        negative_return = []
        for returns in daily_return[1:]:
            if returns < 0:
                negative_return.append(returns)
        sr = (ar-rf)/np.array(negative_return).std()
        wr = 1 - (len(negative_return) / len(nav))
        ann_vol = daily_return[1:].std() * 16
        asr = (ar - rf) / ann_vol
        drawdown = []
        i = 1
        while i <= len(nav):
            a = (nav[i-1] / np.amax(nav[0:i])) - 1
            drawdown.append(a)
            i += 1
        #md = (np.amax(nav)-np.amin(nav))/np.amax(nav)
        md = abs(np.amin(drawdown))
        calmer_ratio = ar / md
        print("Winning rate: " + str(wr),
              "Cumulative return: " + str(cr),
              "Annualized geometric return: " + str(ar),
              "Annualized std. : " + str(ann_vol),
              "Annualized Sharpe Ratio: " + str(asr),
              "Sortino Ratio: " + str(sr),
              "Max drawdown: " + str(md),
              "Calmer ratio: " + str(calmer_ratio),
              sep="\n")

        self.drawdown = pd.Series(drawdown, index=self.nav.index)
        plt.plot(self.drawdown)
        plt.show()


    def plotting(self):
        benchmark = pd.read_csv("FTLS.csv", index_col=0)
        benchmark.index = pd.to_datetime(benchmark.index, dayfirst=True)
        fig, ax = plt.subplots(figsize=(15, 8))
        plt.plot(self.nav.index.astype('O'), self.nav, label='Portfolio')
        plt.plot(benchmark.index.astype('O'), benchmark, label="Benchmark")
        fig.autofmt_xdate()
        plt.xlabel('Date')
        plt.ylabel('Value of US$10m')
        plt.title('Our Strategy vs S&P500')
        plt.legend()
        ax.grid(True)
        months = MonthLocator(interval=2)
        monthsFmt = DateFormatter("%b/%y")
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(monthsFmt)
        plt.show()

NAVlog = pd.read_csv("./NAVlog.csv", index_col=0)
NAVlog.index = pd.to_datetime(NAVlog.index, dayfirst=True)
portfolio = Performance(NAV=NAVlog)
Performance.analyze(self=portfolio, rf=0.017)
Performance.plotting(self=portfolio)