import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
from matplotlib.dates import DateFormatter, MonthLocator


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
        ann_vol = nav.pct_.std() * 16
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

        self.drawdown = pd.Series(drawdown, index=self.nav.index)
        plt.plot(self.drawdown)
        plt.show()


    def plotting(self):
        # compared with S&P500
        #start_date = datetime.datetime(2019, 1, 2)
        #end_date = datetime.datetime(2019, 12, 27)
        benchmark = pd.read_csv("SP500.csv", index_col=0)
        benchmark.index = pd.to_datetime(benchmark.index, dayfirst=True)
        #all_weekdays = pd.date_range(start=start_date, end=end_date, freq='B')
        fig, ax = plt.subplots(figsize=(15, 8))
        plt.plot(self.nav.index.astype('O'), self.nav, label='Portfolio')
        plt.plot(benchmark.index.astype('O'), benchmark, label="S&P500")
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