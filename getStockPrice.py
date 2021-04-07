import pandas as pd
import yfinance as yf
import time

def getStockPrice(tickers, whichprice):
    if whichprice not in ["Open", "High", "Low", "Close", "Avg"]:
        print("Error: please choose whichprice in [Open, High, Low, Close, Avg]")
        return
    
    failed_list = []
    update_list = []
    price = {}
    for stock in tickers:
        try:
            print(f"Processing: {stock}...")
            price_i = pd.read_csv(f"./../Data/SP500/price_{stock}.csv", index_col=0)
            if whichprice != "Avg":
                price_i = price_i[whichprice]
            else:
                price_i = (price_i["High"] + price_i["Low"]) / 2
            price[stock] = price_i
        except:
            try:
                print(f"Downloading: {stock}...")
                time.sleep(1)
                data = yf.Ticker(stock)
                price_i = data.history(period = 'max')
                price_i.to_csv(f'./../Data/SP500/price_{stock}.csv')
                update_list.append(stock)
                if whichprice != "Avg":
                    price_i = price_i[whichprice]
                else:
                    price_i = (price_i["High"] + price_i["Low"]) / 2
                price[stock] = price_i
            except:
                failed_list.append(stock)
    
    price_all = pd.DataFrame.from_dict(price)
    price_all.dropna(how='all')
    return (price_all, failed_list)


