# FINA4380 Group Project
###  Strategy Design
- Statistical Arbitrage
- Measured in absolute return
- long-short
- US$ 1 million initial investment equally divided into 25 shares to allocate in each pair.
- Any publicly listed US company and cryptocurrency
###### Motivation

###### Hypothesis
We find two assets in each of the 25 industry groups that are highly correlated with each other. We run an cointegration test on the historical data, and set the tragger condition fo rboth stocks. Theoretically these two stocks cannot drift too far from each other. When one stock is getting overvalued, we short the bullish one and long the bearish one, vice versa.
###### Sample
Daily stock price from past ten years.
###### Step 1
Divide stocks by 24 industry groups by GICS. With cryptocurrencies, we have 24 + 1 = 25 industry groups.
###### Step 2
In each group, find a pair of assets that are highly positively correlated. Use a two-step test to test for cointegration. First using log prices to run a regression to find the cointegration ratio between two asseets. Secondly run an ADF test to test if the assets are non-stationary.
###### Step 3
Trade if spread >= 5%. Clear position when gain = 2% || loss = 1%. (to be modified)
###### Step 4
Look for next best opportunity as soon as transaction is completed.

###Back testing
