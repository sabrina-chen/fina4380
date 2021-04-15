# create Portfolio() only once in main.py

import pandas as pd
import numpy as np
import datetime

class Portfolio:
    def __init__(self, tickers: pd.DataFrame, iniNAV: float, iniprice: pd.DataFrame, portweight: pd.DataFrame, inidate: datetime.datetime, leverage: int):
        """
        ## Parameter

        iniNAV: initial NAV
        tickers: pd.DataFrame of tickers and industries
        iniprice: stocks prices of initial trading day
        portweight: initial portfolio weight

        """
        # example of portfolio (and newPort): (in pd.DataFrame() form?)
        #         0                                               1         2
        # 0     ROP                                   Capital Goods  1.000000
        # 1     IEX                                   Capital Goods -1.156573

        self.lev = leverage    # no change                
        self.tickers = tickers    # no change

        nindustry = len(tickers.groupby("Industry Group").size())
        self.NAV = iniNAV    # update everyday
        self.date = inidate    # update everyday
        self.groupNAV = pd.Series([iniNAV/nindustry]*nindustry, index=[n for n in tickers.groupby("Industry Group").groups])    # update everyday
        
        self.price = iniprice.T    # append everyday
        self.NAVlog = pd.DataFrame([iniNAV], index=[inidate])    # append everyday
        
        self.portweight = portweight.copy()    # check whether update everyday
        # self.cash = 0    # update if change in portweight
        self.proceed = np.array([0.0]*nindustry)    # update if change in portweight
        self.shares = pd.DataFrame()    # update if change in portweight
        self.values = pd.DataFrame()    # update everyday
        self.margin = np.array([])    # update if change in portweight
        self.borrCash = np.array([])    # update if change in portweight

        for industry, group in self.portweight.groupby([1]):
            if pd.isna(group.iloc[0,0]):
                share = [0.0]*2
                shareFrame = pd.DataFrame(np.vstack(([group.iloc[0,0], group.iloc[1,0]], [industry]*2, share)).T)
                self.shares = self.shares.append(shareFrame, ignore_index=True)
                self.values = self.values.append(pd.DataFrame(np.vstack((group[0], [industry]*2, [0.0]*2)).T), ignore_index=True)
                self.margin = np.hstack((self.margin, np.array([0.0])))
                self.borrCash = np.hstack((self.borrCash, np.array([0.0])))

            else:
                share = self.__calShare__(industry)
                shareFrame = pd.DataFrame(np.vstack(([group.iloc[0,0], group.iloc[1,0]], [industry]*2, share)).T)
                self.shares = self.shares.append(shareFrame, ignore_index=True)
                # self.shares[2] = self.shares[2].astype(float)
                newvalue = self.__calValue__(industry, True)
                self.borrCash = np.hstack((self.borrCash, np.array([newvalue[newvalue>0].item() * (1 - 1/self.lev)])))
                self.margin = np.hstack((self.margin, np.array([abs(newvalue[newvalue<0].item()) / self.lev])))
                self.values = self.values.append(pd.DataFrame(np.vstack((group[0], [industry]*2, newvalue)).T), ignore_index=True)
        
        
        # self.cash = self.NAV + self.borrCash.sum() + abs(self.values[self.values[2] < 0][2].sum()) - self.values[self.values[2] > 0][2].sum() - self.margin.sum() - self.proceed.sum()    # cash remained after long-short due to integer number of shares
        # self.cash = self.NAV + abs(self.values[self.values[2] < 0][2].sum()) - self.values[self.values[2] > 0][2].sum() - self.margin.sum()    # cash remained after long-short due to integer number of shares
        # self.cash = self.NAV + abs(self.values[self.values[2] < 0][2].sum()) - self.margin.sum()


    def __calShare__(self, industry) -> np.ndarray:
        """
        Calculate the numbers of shares to open the position of specific industry based on current weight, current groupNAV, and lastest share price.
        """
        nav = self.groupNAV[industry]#  + self.cash
        total = nav * self.lev
        weight = self.portweight.groupby([1]).get_group(industry)
        wA = weight.iloc[0,2]
        wB = weight.iloc[1,2]
        PA = self.price[weight.iloc[0,0]].iloc[-1]
        PB = self.price[weight.iloc[1,0]].iloc[-1]
        
        k = total / (abs(wA) + abs(wB))
        # if (wA + wB) < 0:
        #     k = total / (abs(wA) + abs(wB))
        # else:
        #     k = total / (abs(wA) + abs(wB))
        shares = np.array([(wA*k/PA), (wB*k/PB)])
        # shareFrame = pd.DataFrame(np.vstack(([weight.iloc[0,0], weight.iloc[0,1]], [industry]*2, shares)).T)
        
        return shares

    
    def __calValue__(self, industry, update: bool) -> np.ndarray:
        """
        Calculate market values of stocks in specific industry of current portfolio based on lastest price
        """
        indusshare = self.shares.groupby([1]).get_group(industry)
        PA = float(self.price[indusshare.iloc[0,0]][-1])
        PB = float(self.price[indusshare.iloc[1,0]][-1])
        share = indusshare.iloc[:,2].to_numpy()
        values = np.array([PA*float(share[0]), PB*float(share[1])])
        
        short = abs(values[values<0].item())
        long = values[values>0].item()
        if update:
            if values.sum() < 0:
                self.proceed[int(self.portweight[self.portweight[1]==industry].index[0]/2)] = self.groupNAV[industry] - long/self.lev + short * (1 - 1/self.lev)
            else:
                self.proceed[int(self.portweight[self.portweight[1]==industry].index[0]/2)] = self.groupNAV[industry] - long/self.lev + short * (1 - 1/self.lev)
        return values


    def updatePortfolio(self, newprice: pd.DataFrame, newPort: pd.DataFrame):    # planned to be executed everyday
        self.price = self.price.append(newprice)
        self.date = newprice.index[0]
        newPortGroup = newPort.groupby([1])
        k = 0
        for industry, group in self.portweight.groupby([1]):
            newPort_ind = newPortGroup.get_group(industry)
            oldShare = self.shares.groupby([1]).get_group(industry)
            if pd.isna(newPort_ind.iloc[0, 0]) and (not pd.isna(group.iloc[0, 0])):    # Pair -> no Pair
                closingValue = self.__calValue__(industry, False)
                self.groupNAV[industry] = closingValue[0] + closingValue[1] + self.margin[k] - self.borrCash[k] + self.proceed[k]
                
                self.margin[k] = 0
                self.borrCash[k] = 0
                self.proceed[k] = 0

                self.shares.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0].to_numpy()
                self.shares.iloc[(2*k):(2*k+2),2] = [0, 0]
                self.values.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0].to_numpy()
                self.values.iloc[(2*k):(2*k+2),2] = [0, 0]
                self.portweight.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0].to_numpy()    # update stock symbol
                self.portweight.iloc[(2*k):(2*k+2),2] = newPort_ind.iloc[:,2].to_numpy()    # update current portweight

            elif pd.isna(group.iloc[0, 0]) and (not pd.isna(newPort_ind.iloc[0, 0])):    # no Pair -> Pair
                self.portweight.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0].to_numpy()    # update stock symbol
                self.portweight.iloc[(2*k):(2*k+2),2] = newPort_ind.iloc[:,2].to_numpy()    # update current portweight

                self.shares.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0].to_numpy()    # update stock symbol
                newShare = self.__calShare__(industry)
                self.shares.iloc[(2*k):(2*k+2),2] = newShare.copy()    # update share

                self.values.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0].to_numpy()    # update stock symbol
                newValue = self.__calValue__(industry, True)
                self.values.iloc[(2*k):(2*k+2),2] = newValue.copy()    # update market value of stocks in industry

                self.margin[k] = abs(newValue[newValue < 0].item()) / self.lev    # update if change in portweight
                self.borrCash[k] = newValue[newValue > 0].item() * (1 - 1/self.lev)    # update if change in portweight

            elif not pd.isna(group.iloc[0, 0]) and not pd.isna(newPort_ind.iloc[0, 0]) and group[0].equals(newPort_ind[0]):    # if no change in industry
                newValue = self.__calValue__(industry, False)
                self.groupNAV[industry] = newValue.sum() + self.margin[k] - self.borrCash[k] + self.proceed[k]
                self.values.iloc[(2*k):(2*k+2),2] = newValue.copy()    # update market value of stocks in industry
            
            elif not pd.isna(group.iloc[0, 0]) and not pd.isna(newPort_ind.iloc[0, 0]):
                closingValue = self.__calValue__(industry, False)    # value of 2 stocks when closing position
                self.groupNAV[industry] = closingValue.sum() + self.margin[k] - self.borrCash[k] + self.proceed[k]   # NAV (Cash) of the group after closing position

                self.portweight.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0].to_numpy()    # update stock symbol
                self.portweight.iloc[(2*k):(2*k+2),2] = newPort_ind.iloc[:,2].to_numpy()    # update current portweight

                self.shares.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0].to_numpy()    # update stock symbol
                newShare = self.__calShare__(industry)
                self.shares.iloc[(2*k):(2*k+2),2] = newShare.copy()    # update share

                self.values.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0].to_numpy()    # update stock symbol
                newValue = self.__calValue__(industry, True)
                self.values.iloc[(2*k):(2*k+2),2] = newValue.copy()    # update market value of stocks in industry

                self.margin[k] = abs(newValue[newValue < 0].item()) / self.lev    # update if change in portweight
                self.borrCash[k] = newValue[newValue > 0].item() * (1 - 1 / self.lev)    # update if change in portweight
                # newnav = newprice[newPort_ind.iloc[0,0]][0] * newShare[0] + newprice[newPort_ind.iloc[1,0]][0] * newShare[1] + self.margin[k] - self.borrCash[k] + self.proceed[k]
                # self.groupNAV[industry] = newnav
                # self.cash = oldnav + self.cash - newnav    # cash remained after long-short due to integer number of shares

            k += 1
        
        self.NAV = self.groupNAV.sum() #  + self.cash
        self.NAVlog = self.NAVlog.append(pd.DataFrame([self.NAV], index=[self.date]))

