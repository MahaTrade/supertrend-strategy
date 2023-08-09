import os
import sys
import backtrader as bt
from indicators.supertrend import SuperTrend

class SuperTrend_TrailingSL(bt.Strategy):
    params = (
        ('multiplier', 2),
        ('period', 14),
    )

    def __init__(self):
        self.target_price = 0
        self.stop_loss = 0
        self.superTrend = SuperTrend(period=self.params.period, multiplier=self.params.multiplier)
        self.atr = bt.indicators.AverageTrueRange(period=self.params.period)
        self.positionStatus = 0
        self.prev_trend = 0
        self.win = 0
        self.loss = 0
        self.no_of_trades = 0
        self.open_price = 0

    def next(self):
        current_price = self.data.close[0]
        if not self.position:
            if self.superTrend < self.data.close[-1] and self.prev_trend != 1 and current_price + self.atr[0] > current_price * 1.003:
                print("buy")
                self.open_price = current_price
                self.target_price = current_price + self.atr[0]
                self.stop_loss = current_price - (3 * self.atr[0])
                self.positionStatus = 1
                self.no_of_trades += 1
                self.buy()
            # if self.superTrend > self.data.close[-1] and self.prev_trend != -1 and current_price - self.atr[0] < current_price * 0.997:
            #     print("sell")
            #     self.open_price = current_price
            #     self.target_price = current_price - self.atr[0]
            #     self.stop_loss = current_price + (3 * self.atr[0])
            #     self.positionStatus = -1
            #     self.no_of_trades += 1
            #     self.sell()
        else:
            if self.positionStatus == 1:
                perc = ((current_price - self.open_price) / self.open_price) * 100
                if self.target_price < current_price:
                    print("sl changed")
                    self.stop_loss = current_price * 0.999
                    self.target_price = current_price * 1.003
                    # self.close()
                    # self.positionStatus = 0
                elif self.stop_loss > current_price:
                    print("** sl hit % ->", round(perc, 2))
                    self.close()
                    self.positionStatus = 0
                elif self.superTrend > self.data.close:
                    print("** trend change % ->", round(perc, 2))
                    self.close()
                    self.positionStatus = 0
            # if self.positionStatus == -1:
            #     if self.target_price > current_price:
            #         print("sl changed")
            #         self.stop_loss = current_price * 1.003
            #         self.target_price = current_price * 0.999
            #     elif self.stop_loss < current_price:
            #         print("** sl hit", self.open_price - current_price)
            #         self.close()
            #         self.positionStatus = 0
            #     elif self.superTrend < self.data.close:
            #         print("trend change close", self.open_price - current_price)
            #         self.close()
            #         self.positionStatus = 0
        if self.superTrend < self.data.close[-1]:
            self.prev_trend = 1
        elif self.superTrend > self.data.close[-1]:
            self.prev_trend = -1

cerebro = bt.Cerebro()
cerebro.addstrategy(SuperTrend_TrailingSL)

modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
datapath = os.path.join(modpath, './data/LTCUSDT-5m-2023-01-formatted.csv')

# Load the data
data = bt.feeds.GenericCSVData(
    dataname=datapath,
    nullvalue=0.0,
    dtformat=('%m/%d/%Y %M:%S:%H'),
    datetime=1,
    open=2,
    high=3,
    low=4,
    close=5,
    volume=6,
    openinterest=-1,
    timeframe=bt.TimeFrame.Minutes,
    compression=1
)
cerebro.adddata(data)

# Set initial capital
cerebro.broker.setcash(100000)

# Set commission and slippage assumptions
cerebro.broker.setcommission(commission=0.001, leverage=2)  # Assuming 0.1% commission per trade
cerebro.broker.set_slippage_fixed(0.001)  # Assuming 0.1% slippage per trade

# Set position sizing
cerebro.addsizer(bt.sizers.PercentSizer, percents=20)  # Allocate 90% of available cash per trade

# Set desired risk-to-reward ratio
cerebro.addanalyzer(bt.analyzers.Returns, timeframe=bt.TimeFrame.Minutes)
cerebro.addanalyzer(bt.analyzers.DrawDown)

# Run the backtest
results = cerebro.run()
# Retrieve performance metrics
strategy = results[0]

drawdown = strategy.analyzers.drawdown.get_analysis()
# Calculate performance statistics
total_return = (strategy.broker.getvalue() - 100000) / 1000  # Assuming starting capital of 100,000
max_drawdown = drawdown.max.drawdown

print(f"Total Return: {total_return}%")
print(f"Max Drawdown: {max_drawdown}%")
print(f"Portfolio Value: {strategy.broker.getvalue()}")

# cerebro.plot()

