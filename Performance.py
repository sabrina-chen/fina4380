import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from pandas_datareader import data


class Performance:
    def __init__(self, NAV):
        self.nav = NAV

    def printarray(self):
        print(np.array(self.nav).shape)
        print(len(np.array(self.nav)))
        print(np.array(self.nav)[4])
        print(np.array(self.nav)[0:5])
        #print(np.array(self.nav).reshape(-1).shape)

    def analyze(self, rf):
        nav = np.array(self.nav)
        cr = nav[-1] / nav[0] - 1
        ar = (nav[-1] / nav[0]) ** (250 / len(nav)) - 1
        ann_vol = nav.std() * 16
        asr = (ar - rf) / ann_vol
        drawdown = []
        i = 1
        while i <= len(nav):
            a = (nav[i-1] / np.amax(nav[0:i])) - 1
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

    def plotting(self):
        # compared with S&P500
        #start_date = datetime.datetime(2019, 1, 2)
        #end_date = datetime.datetime(2019, 12, 27)
        benchmark = pd.read_csv("SP500.csv", index_col=0)
        benchmark.index = pd.to_datetime(benchmark.index)
        #all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')
        plt.plot(self.nav, label='Portfolio')
        plt.plot(benchmark, label="S&P500")
        #ax.format_xdata = mdates.DateFormatter('%Y-%m')
        #ax.format_ydata = lambda x: f'${x:.2f}'  # Format the price.
        #plt.xlim('2020-01-02', '2021-01-04')
        plt.xlabel('Date')
        plt.ylabel('Value of US$10m')
        plt.title('Our Strategy vs S&P500')
        plt.legend()
        plt.show()


NAVlog = pd.read_csv("AAPL.csv", index_col=0)
NAVlog.index = pd.to_datetime(NAVlog.index)
portfolio = Performance(NAV=NAVlog)
Performance.analyze(self=portfolio, rf=0.017)
Performance.plotting(self=portfolio)
