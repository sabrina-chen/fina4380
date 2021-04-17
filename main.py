import pandas as pd
import numpy as np
from DailyUpdate import DailyUpdate
from Portfolio import Portfolio
import datetime
from matplotlib import pyplot as plt
from Performance import Performance


startyear = 2019
nindustry = 20

tradeTickers = pd.read_csv(f"./tradeTickers_filtered_{nindustry}industries.csv", index_col=0)
# tradeTickers
priceClose = pd.read_csv("./PriceUse_filtered.csv", index_col=0)
priceOpen = pd.read_csv("./PriceUse_Open.csv", index_col=0)
priceClose.index = pd.to_datetime(priceClose.index)
priceOpen.index = pd.to_datetime(priceOpen.index)


start = priceClose.index.searchsorted(datetime.datetime(startyear, 1, 1))

indusList = pd.read_csv(f"./industryList_{nindustry}.csv", index_col=0)
indusList.columns = [0]

portlog = pd.DataFrame(np.array([[i]*2 for i in indusList[0]]).reshape(-1))

gNAVlog = pd.DataFrame([], index=indusList[0])
gNAVlog.index.name = None


k = 0
for day in range(250):    # 250 for 1 year
    print(f"day {k}")
    # cumret = (np.log(priceClose.iloc[start+day-250:start+day,:]) - np.log(priceClose.iloc[start-250,:]))
    
    if day == 0:
        todayPortUpdate = DailyUpdate(priceClose.iloc[start-250:start+day,:], tradeTickers)
    else:
        todayPortUpdate = DailyUpdate(priceClose.iloc[start-250:start+day,:], tradeTickers, newport, startEpsilon, startDay)
    todayPortUpdate.rebalancing()
    newport = todayPortUpdate.getUpdatedPort().copy()
    newport.columns = [0, 1, 2]
    startEpsilon = todayPortUpdate.startEpsilon.copy()
    startDay = todayPortUpdate.startDay.copy()
    portlog = portlog.join(pd.DataFrame(newport.drop([1], axis=1).to_numpy(), columns=[2*k+1, 2*k+2]))
    portlog.to_csv("./portlog.csv")
    if k == 0:
        tradePortfolio = Portfolio(tradeTickers, 10000000, priceOpen.iloc[start,:].to_frame(), newport.copy(), priceOpen.index[start], 1)
    else:
        tradePortfolio.updatePortfolio(priceOpen.iloc[start+day,:].to_frame().T, newport.copy())
    tradePortfolio.NAVlog.to_csv("./NAVlog.csv")
    gNAVlog = gNAVlog.join(pd.DataFrame(tradePortfolio.groupNAV.to_numpy(), columns=[k], index=gNAVlog.index))
    gNAVlog.to_csv("./groupNAVlog.csv")
    k += 1


print(tradePortfolio.NAVlog)
NAVlog = pd.read_csv("./NAVlog.csv", index_col=0)
NAVlog.index = pd.to_datetime(NAVlog.index)
portfolio = Performance(NAV=NAVlog)
Performance.analyze(self=portfolio, rf=0.017)
Performance.plotting(self=portfolio)

