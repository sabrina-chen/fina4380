import requests
import pandas as pd
import time


# URL = "https://eresearch.fidelity.com/eresearch/evaluate/snapshot.jhtml?symbols=SLG"
# res = requests.get(URL)
# print(res.status_code)
# print(res.text)
# p = res.text.find("http://eresearch.fidelity.com/eresearch/markets_sectors/sectors/industries.jhtml?tab=learn&industry=")
# p += len("http://eresearch.fidelity.com/eresearch/markets_sectors/sectors/industries.jhtml?tab=learn&industry=")
# res.text[p:p+6]

crsplist = pd.read_csv("./CRSPTM1_list.csv")
ticker = crsplist["Ticker"]
ticker_adj = ticker.apply(lambda x: x.replace(".", "%2F"))


failed_list = []
industry_list=[]

for stock in ticker_adj:
    try:
        print("Processing: "+stock)
        URL = "https://eresearch.fidelity.com/eresearch/evaluate/snapshot.jhtml?symbols="+stock
        res = requests.get(URL)
        p = res.text.find("http://eresearch.fidelity.com/eresearch/markets_sectors/sectors/industries.jhtml?tab=learn&industry=")
        p += len("http://eresearch.fidelity.com/eresearch/markets_sectors/sectors/industries.jhtml?tab=learn&industry=")
        industry_list.append([stock.replace("%2F", "-"), res.text[p:p+6]])
        time.sleep(0.5)
    except:
        failed_list.append(stock)
        continue


failed_list
ticker_adj[3001]

pd.DataFrame(industry_list).to_csv("./industry.csv")
