# create Portfolio() only once in main.py

import pandas as pd
import numpy as np

class Portfolio:
    def __init__(self, tickers, iniNAV, iniprice, portweight: pd.DataFrame, inidate, leverage):
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

        self.NAV = iniNAV    # update everyday
        self.date = inidate    # update everyday
        self.groupNAV = pd.Series([iniNAV/24]*24, index=self.portweight.size().index)    # update everyday
        
        self.price = iniprice.T    # append everyday
        self.NAVlog = pd.DataFrame([iniNAV], index=[inidate])    # append everyday
        
        self.portweight = portweight    # check whether update everyday
        self.cash = 0    # update if change in portweight
        self.shares = pd.DataFrame()    # update if change in portweight
        for industry, group in self.portweight.groupby([1]):
            share = self.__calShare__(industry)
            shareFrame = pd.DataFrame(np.vstack(([group.iloc[0,0], group.iloc[0,1]], [industry]*2, share)).T)
            self.shares = self.shares.append(shareFrame, ignore_index=True)
        
        self.values = pd.DataFrame()    # update everyday
        for industry, group in self.portweight.groupby([1]):
            self.values = self.values.append(np.vstack((group.iloc[0], [industry]*2, self.__calValue__(industry))).T, ignore_index=True)
        
        self.margin = self.values[self.values[2] < 0].to_numpy()[:,2] / self.lev    # update if change in portweight
        self.borrCash = self.values[self.values[2] > 0].to_numpy()[:2] / self.lev    # update if change in portweight
        self.cash = self.NAV + self.borrCash.sum() + self.values[self.values[2] < 0] - self.values[self.values[2] > 0][2].sum() - self.margin.sum()    # cash remained after long-short due to integer number of shares


        
    def __calShare__(self, industry):
        """
        Calculate the numbers of shares to open the position of specific industry based on current weight, current groupNAV, and lastest share price.
        """
        nav = self.groupNAV[industry] + self.cash
        total = nav * self.lev
        weight = self.portweight.groupby([1]).get_group(industry)
        wA = weight.iloc[0,2]
        wB = weight.iloc[1,2]
        PA = self.price[weight.iloc[0,0]].iloc[-1]
        PB = self.price[weight.iloc[1,0]].iloc[-1]
        k = total / PA * wA + PB * wB
        shares = np.array([int(wA*k), int(wB*k)])
        # shareFrame = pd.DataFrame(np.vstack(([weight.iloc[0,0], weight.iloc[0,1]], [industry]*2, shares)).T)
        return shares

    
    def __calValue__(self, industry) -> np.ndarray:
        """
        Calculate market values of stocks in specific industry of current portfolio based on lastest price
        """
        indusshare = self.shares.groupby([1]).get_group(industry)
        PA = self.price[indusshare.iloc[0,0]].iloc[-1]
        PB = self.price[indusshare.iloc[1,0]].iloc[-1]
        values = np.multiply([PA, PB], indusshare.iloc[:,2])
        return values


    def updatePortfolio(self, newprice: pd.DataFrame, newPort: pd.DataFrame):    # planned to be executed everyday
        self.price = self.price.append(newprice)
        self.date = newprice.index
        newPortGroup = newPort.groupby([1])
        k = 0
        for industry, group in self.portweight.groupby([1]):
            newPort_ind = newPortGroup.get_group(industry)
            oldShare = self.shares.groupby([1]).get_group(industry)
            if group[0].equal(newPort_ind[0]):    # if no change in industry
                self.groupNAV[industry] = newprice[oldShare.iloc[0,0]] * oldShare.iloc[0,2] + newprice[oldShare.iloc[1,0]] * oldShare.iloc[1,2] + self.margin[k] - self.borrCash[k]
                self.values.iloc[(2*k):(2*k+2),2] = self.__calValue__(industry)    # update market value of stocks in industry
            else:
                closingValue = self.__calValue__(industry)    # value of 2 stocks when closing position
                self.groupNAV[industry] = closingValue[0] * group.iloc[0,2] + closingValue[1] * group.iloc[1,2] + self.margin - self.borrCash[k,2]   # NAV (Cash) of the group after closing position
                oldnav = self.groupNAV[industry]

                self.portweight.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0]    # update stock symbol
                self.portweight.iloc[(2*k):(2*k+2),2] = newPort_ind.iloc[:,2]    # update current portweight

                self.shares.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0]    # update stock symbol
                newShare = self.__calShare__(industry)
                self.shares.iloc[(2*k):(2*k+2),2] = newShare    # update share

                self.values.iloc[(2*k):(2*k+2),0] = newPort_ind.iloc[:,0]    # update stock symbol
                newValue = self.__calValue__(industry)
                self.values.iloc[(2*k):(2*k+2),2] = newValue    # update market value of stocks in industry

                self.margin[k] = newValue[newValue < 0].item() / self.lev    # update if change in portweight
                self.borrCash[k] = newValue[newValue > 0].item() / self.lev    # update if change in portweight
                newnav = newprice[newPort_ind.iloc[0,0]] * newShare[0] + newprice[newPort_ind.iloc[1,0]] * newShare[1] + self.margin[k] - self.borrCash[k]
                self.groupNAV[industry] = newnav
                self.cash = oldnav + self.cash - newnav    # cash remained after long-short due to integer number of shares
            
            k += 1
                
        self.NAV = self.groupNAV + self.cash
        self.NAVlog = self.NAVlog.append(pd.DataFrame([self.NAV], index=[self.date]))

