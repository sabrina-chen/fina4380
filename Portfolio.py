# A recommendation for class portfolio
# Please feel free to change anything

# I personally expect to create Portfolio() only once in main.py

class Portfolio:
    def __init__(self, initial, tickers, logreturns):
        self.NAV = initial
        self.tickers = tickers
        self.logreturns = logreturns
        self.port = {}
    
    def updatePortfolio(self, newPort):    # planned to be executed everyday
        # update portfolio by comparing newPort with self.port
        # update NAV
        pass
