###### FINA4380 Group Project
###  Strategy Design
- Statistical Arbitrage
- Measured in absolute return
- long-short
- US$ 1 million initial investment
#Motivation
#Hypothesis
#sample
Daily stock price from past ten years.
#Step 1
Divide stocks by 24 industry groups by GICS. With cryptocurrencies, we have 24 + 1 = 25 industry groups.
#Step 2
In each group, find a pair of assets that are highly positively correlated.
#Step 3

#Step 4

#Step 5

#Step 6


2. 在numda由小到大排列  找寻numda小 且spread>5%的组合作为投资标的 
3. 将基础资金1million 等分25份 
4. 每次止盈设在 2%   止损设在1% （数据需要optimization一下  不知道多少为最合适） 
5. 每次transaction close之后 自动寻找下一个机会 
