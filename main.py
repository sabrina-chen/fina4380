import pandas as pd
import numpy as np
from DailyUpdate import DailyUpdate
from Portfolio import Portfolio
from Performance import Performance
import datetime


tradeTickers = pd.read_csv("./tradeTickers_filtered.csv", index_col=0)
tradeTickers
priceUse = pd.read_csv("./PriceUse_filtered.csv", index_col=0)
priceUse
priceUse.index = pd.to_datetime(priceUse.index)

# cumret = (np.log(priceUse.iloc[:250,:]) - np.log(priceUse.iloc[0,:]))
# cumret

# todaytrade = DailyUpdate(cumret, tradeTickers)
# todaytrade.rebalancing()
# newport = todaytrade.getUpdatedPort()
# newport.to_csv("./testport.csv")
# todaytrade.newPort = pd.read_csv("./testport.csv", index_col=0)

start = priceUse.index.searchsorted(datetime.datetime(2016, 1, 1))
k = 0
tmp = pd.read_csv("./newport.csv", index_col=0)
portlog = tmp["1"].to_frame()
portlog.columns = [0]

k = 0
for day in range(30):
    cumret = (np.log(priceUse.iloc[start+day-250:start+day,:]) - np.log(priceUse.iloc[start+day-250,:]))
    if day == 0:
        todayPortUpdate = DailyUpdate(cumret, tradeTickers)
    else:
        todayPortUpdate = DailyUpdate(cumret, tradeTickers, newport, startEpsilon)
    todayPortUpdate.rebalancing()
    newport = todayPortUpdate.getUpdatedPort().copy()
    newport.columns = [0, 1, 2]
    startEpsilon = todayPortUpdate.startEpsilon.copy()
    portlog = portlog.join(pd.DataFrame(newport.drop([1], axis=1).to_numpy(), columns=[2*k+1, 2*k+2]))
    portlog.to_csv("./portlog.csv")
    if k == 0:
        tradePortfolio = Portfolio(tradeTickers, 10000000, priceUse.iloc[start+day,:].to_frame(), newport.copy(), priceUse.index[start], 2)
    else:
        tradePortfolio.updatePortfolio(priceUse.iloc[start+day,:].to_frame().T, newport.copy())
    tradePortfolio.NAVlog.to_csv("./NAVlog.csv")
    k += 1


print(tradePortfolio.NAVlog)
NAVlog = pd.read_csv("./NAVlog.csv", index_col=True)
portfolio = Performance(NAV=NAVlog)
Performance.analyze(self=portfolio, rf=0.017)
Performance.plotting(self=portfolio, symbol='sp500')


##### for debug
# todayPort = todaytrade.getUpdatedPort()
# todayPort.columns = [0, 1, 2]

# port = Portfolio(tradeTickers, 10000000, priceUse.iloc[start,:].to_frame(), todayPort, priceUse.index[start], 2)
# port.updatePortfolio(priceUse.iloc[start+1,:].to_frame().T, todayPort)
# port.NAVlog
# port.cash
# port.proceed
# port.portweight.head()
# port.shares.head()
# port.NAV

# port.lev
# port.margin
# port.borrCash*2
# port.values[port.values[2] < 0][2]
# port.values[port.values[2] > 0][2]
# port.values[2].sum() + port.margin.sum() + port.cash #+ port.proceed.sum() - port.borrCash.sum()
# port.values[port.values[2] > 0][2].sum() + port.margin.sum() + port.proceed.sum() - abs(port.values[port.values[2] < 0][2].sum()) - port.borrCash.sum()


# newport = todayPort.copy()
# newport.iloc[0,0] = "F"
# newport.iloc[1,0] = "THO"
# newport.iloc[1,2] = 1.5

# port.updatePortfolio(priceUse.iloc[start+3,:].to_frame().T, newport)


# tvalue, epsilon = todaytrade.findPair("Banks")    
# epsilon.sort_values([2])
# tvalue.to_csv("./tvalue.csv")
# todaytrade.getUpdatedPort()
#####




