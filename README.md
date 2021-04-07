# FINA4380 Group Project
###  Strategy Design
- Statistical Arbitrage
- Measured in absolute return
- long-short
- US$ 10 million initial investment equally divided into 11 shares to allocate in each pair.
- All publicly traded U.S. Equity large- and mid- cap. (market cap >= US$2billion as of 05/04/2021)
###### Motivation

###### Hypothesis
We find two assets in each of the 11 sector groups (according to MSCI) that are highly correlated with each other. We run an cointegration test on the historical data, and set the tragger condition fo rboth stocks. Theoretically these two stocks cannot drift too far from each other. When one stock is getting overvalued, we short the bullish one and long the bearish one, vice versa.
In order to take advantage of such small mispricings, we may have to be heavily leveraged.
We trade large- and mid- cap stocks because very likely small caps simply can't offer the volume. A multi hundred thousand dollar trade could move the market price hence render the back testing results unreliable.
Built-in security measures: liquidate upon a move downward. liquidation orders may trigger more sell orders and cause a horrible loop.
###### Sample
Daily stock price from past ten years. (Tentative. When actually running the program we can parse in arguments such as data frequency and time frame to see how the model performs under different settings.)
###### Step 1
Divide stocks to 11 sector groups by GICS.
###### Step 2
In each group, find a pair of assets that are highly positively correlated. Use a two-step test to test for cointegration. First using log prices to run a regression to find the cointegration ratio between two asseets. Secondly run an ADF test to test if the assets are non-stationary.
###### Step 3
Trade if spread >= 5%. Clear position when gain = 2% || loss = 1%. (to be modified)
###### Step 4
Look for next best opportunity as soon as transaction is completed.

### Back testing
