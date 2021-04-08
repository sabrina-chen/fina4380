# Tentative structure of class dailyUpdate
# new DailyUpdate() object is created every day

import pandas as pd
import numpy as np
from scipy import odr
import statsmodels.api as sm


class DailyUpdate:
    def __init__(self, logreturns, tickers, portfolio=None):    # logreturns of past 1 year (for testing)
        # example of portfolio (and newPort): (in pd.DataFrame() form?)
        # [[stock-A1, industry-A, weight-A1], 
        #  [stock-A2, industry-A, weight-A2],
        #  [stock-B1, industry-B, weight-B1],
        #  [stock-B2, industry-B, weight-B2], ...]
        
        self.logreturns = logreturns.copy()
        if portfolio is not None:
            self.port = portfolio.groupby("Industry Group")
        else:
            self.port = pd.DataFrame()
        self.tickers = tickers.groupby("Industry Group")
        self.newPort = pd.DataFrame()
        

    def rebalancing(self):
        # for each pair of current portfolio:
        #     1st regression: find current epsilon
        #     2nd regression (ADF test) using epsilon: find t-stat
        #     if some condition is met (epsilon mean reversed or t-stat increased or return reached some percentage(may need to get extra data from main.py)):
        #         self.newPort.append(findPair(industry))    # current portfolio using findPair()
        #     else:
        #         self.newport.append(currentpair)
        if not self.port.empty:
            for industry, group in self.port:
                linear = odr.Model(self.__linearReg__)
                datafit = odr.Data(self.logreturns[group["stock"]].iloc[:,0], self.logreturns[group["stock"]].iloc[:,1])    # "stock" subject to change
                reg1_odr = odr.ODR(datafit, linear, beta0=[1., 1.])
                reg1_res = reg1_odr.run()
                
                deltaEps = reg1_res.eps[1:] - reg1_res.eps[:-1]
                # AIC test to find lag variable to include?
                reg2 = sm.OLS(deltaEps, reg1_res.eps[1:])
                reg2_res = reg2.fit()
                if reg2_res.tvalues > -3 or -np.sqrt(reg1_res.res_var) / 10 < reg1_res.eps[-1] < -np.sqrt(reg1_res.res_var) / 10:
                    newpair = self.findPair(industry)
                    self.newPort = self.newPort.append(newpair, ignore_index=True)
                else:
                    self.newPort = self.newPort.append(group, ignore_index=True)
        else:
            for industry, group in self.tickers:
                newpair = self.findPair(industry)
                self.newPort = self.newPort.append(newpair, ignore_index=True)
            

    def findPair(self, industry):    # find pairs of stock where arbitrage exists "within industry groups"
        # for each pair of stocks in industry:
        #     2-stage regression find cointegration ratio and t-stat
        # sort t-stat
        # find |epsilon| > 3%(?) from smallest t-stat
        # result = {"pair": [stockA, stockB], "beta": cointegration ratio, "tstat": t-stat}
        # return result
        group = self.tickers.get_group(industry)
        n = group.shape[0]
        tstat = pd.DataFrame()
        betas = pd.DataFrame()
        epsilon = pd.DataFrame()
        sigma = pd.DataFrame()
        k = 0
        for i in range(n - 1):
            for j in range(i + 1, n):
                linear = odr.Model(self.__linearReg__)
                datafit = odr.Data(self.logreturns[group.iloc[i,0]], self.logreturns[group.iloc[j,0]])
                reg1_odr = odr.ODR(datafit, linear, beta0=[1., 1.])
                reg1_res = reg1_odr.run()

                deltaEps = reg1_res.eps[1:] - reg1_res.eps[:-1]
                # AIC?
                reg2 = sm.OLS(deltaEps, reg1_res.eps[:-1])
                reg2_res = reg2.fit()
                
                tstat = tstat.append([[group.iloc[i,0], group.iloc[j,0], reg2_res.tvalues]], ignore_index=True)
                betas = betas.append([[group.iloc[i,0], group.iloc[j,0], reg1_res.beta[0]]], ignore_index=True)
                epsilon = epsilon.append([[group.iloc[i,0], group.iloc[j,0], reg1_res.eps[-1]]], ignore_index=True)
                sigma = sigma.append([[group.iloc[i,0], group.iloc[j,0], np.std(reg1_res.eps)]], ignore_index=True)
                k += 1
        tstat_sort = tstat.sort_values([2])
        found = False
        k = 0
        n_pair = n * (n-1) / 2
        while k < n_pair and not found:
            e = float(epsilon[(epsilon[0] == tstat_sort.iloc[k,0]) & (epsilon[1] == tstat_sort.iloc[k,1])][2])
            s = float(sigma[(sigma[0] == tstat_sort.iloc[k,0]) & (sigma[1] == tstat_sort.iloc[k,1])][2])
            
            if abs(e) > s:    # subject to change
                ratio = float(betas[(betas[0] == tstat_sort.iloc[k,0]) & (betas[1] == tstat_sort.iloc[k,1])][2])
                if e > 0:
                    pair = pd.DataFrame([[tstat_sort.iloc[k,0], industry, -1],
                                        [tstat_sort.iloc[k,1], industry, ratio]])
                else:
                    pair = pd.DataFrame([[tstat_sort.iloc[k,0], industry, 1],
                                        [tstat_sort.iloc[k,1], industry, -ratio]])
                found = True
            else:
                k += 1
        if found:
            return pair
        else:
            print("No pairs found!")
            return pd.DataFrame()    # tstat_sort, epsilon  # for debig

    def getUpdatedPort(self):
        return self.newPort

    def __linearReg__(self, B, x):
        return B[0] * x + B[1]