import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Performance:
    def __init__(self, NAV):
        self.nav = np.array(NAV).reshape(-1)
    
    def analyze(self, rf):
        cr = self.nav[-1] / self.nav[0] - 1
        ar = (self.nav[-1] / self.nav[0]) ^ (250/len(self.nav)) - 1
        ann_vol = self.nav.std() * 16
        asr = (ar - rf) / ann_vol
        drawdown = []
        for i in len(self.nav):
            a = (self.nav[i]/self.nav[0:i].max()) - 1
            drawdown.append(a)
        md = drawdown.min()
        calmer_ratio = ar/md
        print("Cumulative return: " + cr,
              "Annualized goemetric return: " + ar,
              "Annualized std. : " + ann_vol,
              "Annualized Sharpe Ratio: " + asr,
              "Max drawdown: " + md,
              "Calmer ratio: " + calmer_ratio,
              sep="\n")

    def plotting(self):
        plt.plot(self.nav)
        plt.show()

        