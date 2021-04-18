# new DailyUpdate() object is created every day

import pandas as pd
import numpy as np
from scipy import odr
from statsmodels.tsa.stattools import adfuller
# import statsmodels.api as sm

class DailyUpdate:
    def __init__(self, price, tickers, portfolio=None, startEpsilon=None, startDay=None):
        """
        cumlogRet: cumulative log return (ln(P_t/P_0)) from t_0-250 to the day performing DailyUpdate for running regression and ADF test
        startEpsilon
        startDay: 
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
        
        # self.cumlogRet = cumlogRet.copy()
        
        self.price = price.copy()
        # data in: priceClose.iloc[start-250:start+day,:]
        
        if portfolio is not None:
            self.port = portfolio.copy()
        else:
            self.port = pd.DataFrame()
        self.tickers = tickers.groupby("Industry Group")
        self.newPort = pd.DataFrame()
        
        if startEpsilon is None:
            self.startEpsilon = pd.Series([0.0]*len(self.tickers.size().index), index=self.tickers.size().index)    # update everyday
            self.startDay = pd.Series([0]*len(self.tickers.size().index), index=self.tickers.size().index)    # t_0 of the test for each industry, default 0 = first trading day - 250
        else:
            self.startEpsilon = startEpsilon.copy()
            self.startDay = startDay.copy()

        self.ADFthreshold = -3
        self.ASRthreshold = 1
        

    def rebalancing(self):
        # for each pair of current portfolio:
        #     1st regression: find current epsilon
        #     2nd regression (ADF test) using epsilon: find t-stat
        #     if some condition is met (epsilon mean reversed or t-stat increased or return reached some percentage(may need to get extra data from main.py)):
        #         self.newPort.append(findPair(industry))    # current portfolio using findPair()
        #     else:
        #         self.newport.append(currentpair)
        if self.port.empty:
            for industry, group in self.tickers:
                print("finding: "+industry+"...")
                newpair = self.findPair(industry)
                self.newPort = self.newPort.append(newpair, ignore_index=True)
        else:
            for industry, group in self.port.groupby([1]):
                if pd.isna(group.iloc[0, 0]):
                    print("finding newpair: "+industry)
                    newpair = self.findPair(industry)
                    self.newPort = self.newPort.append(newpair, ignore_index=True)
                else:
                    cumlogRet = np.log(self.price.iloc[-250:,:]) - np.log(self.price.iloc[-250,:])
                    reg1_beta, reg1_eps = self.TLS(cumlogRet[group.iloc[0,0]], cumlogRet[group.iloc[1,0]])
                    reg2 = adfuller(reg1_eps, autolag='AIC', regression="nc")
                    et = reg1_eps[-1]
                    e0 = self.startEpsilon[industry]
                    s = np.std(reg1_eps)
                    ASR = abs(reg1_eps[-1] / s)
                    ADF = reg2[0]
                    ps = ASR ** (self.ADFthreshold - ADF)

                    if ADF > -2.5 or (e0 < 0 and (et > abs(e0)/2)) or (e0 > 0 and (et < -e0/2)):
                        print("finding newpair: " + industry)
                        print(f"Closed: ADF = {ADF}\tet = {et}")
                        
                        newpair = self.findPair(industry)
                        self.newPort = self.newPort.append(newpair, ignore_index=True)
                    else:
                        self.newPort = self.newPort.append(group, ignore_index=True)
                    
                    ##### Use odr #####
                    # linear = odr.Model(self.__linearReg__)
                    # datafit = odr.Data(self.cumlogRet[group.iloc[0,0]], self.cumlogRet[group.iloc[1,0]])    # "stock" subject to change
                    # reg1_odr = odr.ODR(datafit, linear, beta0=[1., 1.])
                    # reg1_res = reg1_odr.run()
                    #
                    # et = reg1_res.eps[-1]
                    # e0 = self.startEpsilon[industry]
                    # if reg2_res.tvalues > -3 or (abs(et - e0) > np.sqrt(reg1_res.res_var) * 2):    # np.sqrt(reg1_res.res_var) / 10 < reg1_res.eps[-1] < -np.sqrt(reg1_res.res_var) / 10) or abs(reg1_res.eps[-1]) > np.sqrt(reg1_res.res_var) * 2.5:
                    #     print("finding newpair: "+industry)
                    #     newpair = self.findPair(industry)
                    #     self.newPort = self.newPort.append(newpair, ignore_index=True)
                    # else:
                    #     self.newPort = self.newPort.append(group, ignore_index=True)
            

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
        PS = pd.DataFrame()

        k = 0
        same = 0
        for i in range(n - 1):
            for j in range(i + 1, n):
                if not self.port.empty and (self.port.groupby([1]).get_group(industry).iloc[0, 0] in [group.iloc[i,0], group.iloc[j,0]] and self.port.groupby([1]).get_group(industry).iloc[1, 0] in [group.iloc[i,0], group.iloc[j,0]]):
                    same = 1
                else:
                    cumlogRet = np.log(self.price.iloc[-250:,:]) - np.log(self.price.iloc[-250,:])
                    reg1_beta, reg1_eps = self.TLS(cumlogRet[group.iloc[i,0]], cumlogRet[group.iloc[j,0]])
                    reg2 = adfuller(reg1_eps, autolag='AIC', regression="nc")

                    s = np.std(reg1_eps)
                    ASR = abs(reg1_eps[-1] / s)
                    ADF = reg2[0]
                    ps = ASR ** (self.ADFthreshold - ADF)

                    tstat = tstat.append([[group.iloc[i,0], group.iloc[j,0], ADF]], ignore_index=True)
                    betas = betas.append([[group.iloc[i,0], group.iloc[j,0], reg1_beta[1]]], ignore_index=True)
                    epsilon = epsilon.append([[group.iloc[i,0], group.iloc[j,0], reg1_eps[-1]]], ignore_index=True)
                    sigma = sigma.append([[group.iloc[i,0], group.iloc[j,0], s]], ignore_index=True)
                    PS = PS.append([[group.iloc[i,0], group.iloc[j,0], ps]], ignore_index=True)

                    # linear = odr.Model(self.__linearReg__)
                    # datafit = odr.Data(self.cumlogRet[group.iloc[i,0]], self.cumlogRet[group.iloc[j,0]])
                    # reg1_odr = odr.ODR(datafit, linear, beta0=[1., 1.])
                    # reg1_res = reg1_odr.run()

                    # reg2 = adfuller(reg1_res.eps, autolag='AIC', regression="nc")
                    
                    # tstat = tstat.append([[group.iloc[i,0], group.iloc[j,0], reg2[0]]], ignore_index=True)
                    # betas = betas.append([[group.iloc[i,0], group.iloc[j,0], reg1_res.beta[0]]], ignore_index=True)
                    # epsilon = epsilon.append([[group.iloc[i,0], group.iloc[j,0], reg1_res.eps[-1]]], ignore_index=True)
                    # sigma = sigma.append([[group.iloc[i,0], group.iloc[j,0], np.std(reg1_res.eps)]], ignore_index=True)
                k += 1
        # tstat_sort = tstat.sort_values([2])
        PS_sort = PS.sort_values([2], ascending=False)
        found = False
        k = 0
        n_pair = n * (n-1) / 2 - same
        
        while k < n_pair and not found:
            e = float(epsilon[(epsilon[0] == PS_sort.iloc[k,0]) & (epsilon[1] == PS_sort.iloc[k,1])][2])
            adf = float(tstat[(tstat[0] == PS_sort.iloc[k,0]) & (tstat[1] == PS_sort.iloc[k,1])][2])
            s = float(sigma[(sigma[0] == PS_sort.iloc[k,0]) & (sigma[1] == PS_sort.iloc[k,1])][2])
            
            if adf < self.ADFthreshold and abs(e / s) > self.ASRthreshold:
                ratio = float(betas[(betas[0] == PS_sort.iloc[k,0]) & (betas[1] == PS_sort.iloc[k,1])][2])
                if ratio > 0:
                    if e > 0:
                        pair = pd.DataFrame([[PS_sort.iloc[k,0], industry, 1],
                                            [PS_sort.iloc[k,1], industry, -ratio]])
                    else:
                        pair = pd.DataFrame([[PS_sort.iloc[k,0], industry, -1],
                                            [PS_sort.iloc[k,1], industry, ratio]])
                    found = True
                    print(PS_sort.iloc[k,2])
            k += 1
        
        # while tstat_sort.iloc[k,2] < -2.5 and k < n_pair and not found:
        #     e = float(epsilon[(epsilon[0] == tstat_sort.iloc[k,0]) & (epsilon[1] == tstat_sort.iloc[k,1])][2])
        #     s = float(sigma[(sigma[0] == tstat_sort.iloc[k,0]) & (sigma[1] == tstat_sort.iloc[k,1])][2])
            
        #     if 3.5*s > abs(e) > 2.5*s:    # subject to change
        #         ratio = float(betas[(betas[0] == tstat_sort.iloc[k,0]) & (betas[1] == tstat_sort.iloc[k,1])][2])
        #         if ratio > 0:
        #             if e > 0:
        #                 pair = pd.DataFrame([[tstat_sort.iloc[k,0], industry, 1],
        #                                     [tstat_sort.iloc[k,1], industry, -ratio]])
        #             else:
        #                 pair = pd.DataFrame([[tstat_sort.iloc[k,0], industry, -1],
        #                                     [tstat_sort.iloc[k,1], industry, ratio]])
        #             found = True
        #             print(tstat_sort.iloc[k,2])
        #     k += 1
        if found:
            print(e)
            self.startEpsilon[industry] = float(e)
            self.startDay[industry] = self.price.shape[0]-250
            return pair
        else:
            print("No pairs found!")
            return pd.DataFrame([[np.nan, industry, 0],
                                [np.nan, industry, 0]])

    def getUpdatedPort(self):
        return self.newPort

    def __linearReg__(self, B, x):
        return B[0] * x + B[1]

    def TLS(self, x, y):
        X = np.array(x).reshape(-1)
        Y = np.array(y).reshape(-1)
        mX = np.mean(X)
        mY = np.mean(Y)
        c0 = np.sum((X - mX) * (Y - mY))
        c1 = np.sum(np.square(X - mX) - np.square(Y - mY))
        beta1 = (- c1 + np.sqrt(c1 ** 2 + 4 * (c0 ** 2))) / (2 * c0)
        beta0 = mY - beta1 * mX
        eps = (Y - beta0 - beta1 * X) / np.sqrt(1 + beta1 ** 2)

        return ([beta0, beta1], eps)

