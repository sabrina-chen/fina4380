# new DailyUpdate() object is created every day

import pandas as pd
import numpy as np
from scipy import odr
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller


class DailyUpdate:
    def __init__(self, cumlogRet, tickers, portfolio=None, startEpsilon=None):
        """
        cumlogRet: cumulative log return (ln(P_t/P_0)) of past 1 year for running regression and ADF test
        """
        # example of portfolio (and newPort): (in pd.DataFrame() form?)
        #         0                                               1         2
        # 0     ROP                                   Capital Goods  1.000000
        # 1     IEX                                   Capital Goods -1.156573
        # 2     VFC                     Consumer Durables & Apparel  1.000000
        # 3     HBI                     Consumer Durables & Apparel -1.570413
        # 4     DFS                          Diversified Financials  1.000000
        # 5     BEN                          Diversified Financials -0.837092
        # 6     OXY                                          Energy  1.000000
        # 7     OKE                                          Energy -0.864398
        
        self.cumlogRet = cumlogRet.copy()
        if portfolio is not None:
            self.port = portfolio.groupby([1])
        else:
            self.port = pd.DataFrame()
        self.tickers = tickers.groupby("Industry Group")
        self.newPort = pd.DataFrame()
        
        if startEpsilon is None:
            self.startEpsilon = pd.Series([0.0]*24, index=self.tickers.size().index)    # update everyday
        else:
            self.startEpsilon = startEpsilon

        

    def rebalancing(self):
        # for each pair of current portfolio:
        #     1st regression: find current epsilon
        #     2nd regression (ADF test) using epsilon: find t-stat
        #     if some condition is met (epsilon mean reversed or t-stat increased or return reached some percentage(may need to get extra data from main.py)):
        #         self.newPort.append(findPair(industry))    # current portfolio using findPair()
        #     else:
        #         self.newport.append(currentpair)
        try:
            self.port.empty
            for industry, group in self.tickers:
                print("finding: "+industry+"...")
                newpair = self.findPair(industry)
                self.newPort = self.newPort.append(newpair, ignore_index=True)
        except:
            for industry, group in self.port:
                if pd.isna(group.iloc[0, 0]):
                    print("finding newpair: "+industry)
                    newpair = self.findPair(industry)
                    self.newPort = self.newPort.append(newpair, ignore_index=True)
                else:
                    linear = odr.Model(self.__linearReg__)
                    datafit = odr.Data(self.cumlogRet[group.iloc[0,0]], self.cumlogRet[group.iloc[1,0]])    # "stock" subject to change
                    reg1_odr = odr.ODR(datafit, linear, beta0=[1., 1.])
                    reg1_res = reg1_odr.run()
                    
                    deltaEps = reg1_res.eps[1:] - reg1_res.eps[:-1]
                    # AIC test to find lag variable to include?
                    reg2 = sm.OLS(deltaEps, reg1_res.eps[1:])
                    reg2_res = reg2.fit()
                    et = reg1_res.eps[-1]
                    e0 = self.startEpsilon[industry]
                    if reg2_res.tvalues > -3 or (abs(et - e0) > np.sqrt(reg1_res.res_var) * 2):    # np.sqrt(reg1_res.res_var) / 10 < reg1_res.eps[-1] < -np.sqrt(reg1_res.res_var) / 10) or abs(reg1_res.eps[-1]) > np.sqrt(reg1_res.res_var) * 2.5:
                        print("finding newpair: "+industry)
                        newpair = self.findPair(industry)
                        self.newPort = self.newPort.append(newpair, ignore_index=True)
                    else:
                        self.newPort = self.newPort.append(group, ignore_index=True)
            

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
        same = 0
        for i in range(n - 1):
            for j in range(i + 1, n):
                
                if type(self.port) != type(pd.DataFrame()) and (self.port.get_group(industry).iloc[0, 0] in [group.iloc[i,0], group.iloc[j,0]] and self.port.get_group(industry).iloc[1, 0] in [group.iloc[i,0], group.iloc[j,0]]):
                    k += 1
                    same = 1
                else:
                    linear = odr.Model(self.__linearReg__)
                    datafit = odr.Data(self.cumlogRet[group.iloc[i,0]], self.cumlogRet[group.iloc[j,0]])
                    reg1_odr = odr.ODR(datafit, linear, beta0=[1., 1.])
                    reg1_res = reg1_odr.run()

                    # deltaEps = reg1_res.eps[1:] - reg1_res.eps[:-1]

                    reg2 = adfuller(reg1_res.eps, autolag='AIC', regression="nc")
                    
                    tstat = tstat.append([[group.iloc[i,0], group.iloc[j,0], reg2[0]]], ignore_index=True)
                    betas = betas.append([[group.iloc[i,0], group.iloc[j,0], reg1_res.beta[0]]], ignore_index=True)
                    epsilon = epsilon.append([[group.iloc[i,0], group.iloc[j,0], reg1_res.eps[-1]]], ignore_index=True)
                    sigma = sigma.append([[group.iloc[i,0], group.iloc[j,0], np.std(reg1_res.eps)]], ignore_index=True)
                    k += 1
        tstat_sort = tstat.sort_values([2])
        found = False
        k = 0
        n_pair = n * (n-1) / 2 - same
        
        while tstat_sort.iloc[k,2] < -3 and k < n_pair and not found:
            e = float(epsilon[(epsilon[0] == tstat_sort.iloc[k,0]) & (epsilon[1] == tstat_sort.iloc[k,1])][2])
            s = float(sigma[(sigma[0] == tstat_sort.iloc[k,0]) & (sigma[1] == tstat_sort.iloc[k,1])][2])
            
            if 2.5*s > abs(e) > s:    # subject to change
                ratio = float(betas[(betas[0] == tstat_sort.iloc[k,0]) & (betas[1] == tstat_sort.iloc[k,1])][2])
                if ratio > 0:
                    if e > 0:
                        pair = pd.DataFrame([[tstat_sort.iloc[k,0], industry, 1],
                                            [tstat_sort.iloc[k,1], industry, -ratio]])
                    else:
                        pair = pd.DataFrame([[tstat_sort.iloc[k,0], industry, -1],
                                            [tstat_sort.iloc[k,1], industry, ratio]])
                    found = True
                    print(tstat_sort.iloc[k,2])
            k += 1
        if found:
            print(e)
            self.startEpsilon[industry] = float(e)
            return pair
        else:
            print("No pairs found!")
            return pd.DataFrame([[np.nan, industry, 0],
                                [np.nan, industry, 0]])    # tstat_sort, epsilon  # for debig

    def getUpdatedPort(self):
        return self.newPort

    def __linearReg__(self, B, x):
        return B[0] * x + B[1]

    def TLS(self, x, y):
        

