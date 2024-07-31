import ccxt
import time
import csv
from datetime import datetime


class TradingClass:
    def __init__(self, api_key, secret, leverage, investment_balance, stop_loss_pct, take_profit_pct, sleep_time,
                 check_interval, symbol, timeframe):
        self.api_key = api_key
        self.secret = secret
        self.leverage = leverage
        self.investment_balance = investment_balance
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.sleep_time = sleep_time
        self.check_interval = check_interval
        self.symbol = symbol
        self.timeframe = timeframe
        self.exchange = None
        self.open_orders = []
        self.log_file = 'trade_log.csv'
        self.initialize_log_file()

    def initialize_log_file(self):
        """Initialize the CSV log file with headers."""
        with open(self.log_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'symbol', 'direction', 'order_size', 'entry_price', 'exit_price', 'stop_loss',
                             'take_profit'])

    def connect_to_binance(self):
        """Connect to Binance Futures using the provided API key and secret."""
        self.exchange = ccxt.binance({
            'apiKey': self.api_key,
            'secret': self.secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            },
        })
        print("Connected to Binance Futures")

    def fetch_account_balance(self):
        """Fetch the account balance and return only the available balances."""
        if self.exchange is None:
            raise Exception("You need to connect to the exchange first")
        balance = self.exchange.fetch_balance()
        available_balance = {symbol: balance['total'][symbol] for symbol in balance['total'] if
                             balance['total'][symbol] > 0}
        print("Fetched account balance:", available_balance)
        return available_balance

    def get_candlestick_data(self):
        """Get candlestick data for the specified symbol and timeframe."""
        if self.exchange is None:
            raise Exception("You need to connect to the exchange first")
        ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe)
        print(f"Fetched candlestick data for {self.symbol} - {self.timeframe}")
        return ohlcv

    def check_candlestick_pattern(self):
        """
        Check if the previous two candlesticks are the same color and have volume greater
        than the average of the previous five candlesticks.
        """
        ohlcv = self.get_candlestick_data()

        # Extract the last 5 candlesticks
        last_five = ohlcv[-5:]
        # Extract the last two candlesticks
        last_two = ohlcv[-2:]

        # Calculate the average volume of the previous five candlesticks
        avg_volume = sum([candle[5] for candle in last_five]) / 5

        # Determine the color of the last two candlesticks (green if close > open, red if close < open)
        last_two_colors = ['green' if candle[4] > candle[1] else 'red' for candle in last_two]

        # Check if both candlesticks are the same color and if their volume is greater than the average volume
        same_color = last_two_colors[0] == last_two_colors[1]
        high_volume = all(candle[5] > avg_volume for candle in last_two)

        print(f"Checked candlestick pattern: Same color: {same_color}, High volume: {high_volume}")
        return same_color and high_volume

    def place_order_based_on_pattern(self):
        """
        Place a market buy or sell order based on the candlestick pattern check.
        """
        pattern_check = self.check_candlestick_pattern()

        # If the pattern is valid, place a buy or sell order
        if pattern_check:
            ohlcv = self.get_candlestick_data()
            last_candle = ohlcv[-1]

            # Determine the direction of the trade
            direction = 'buy' if last_candle[4] > last_candle[1] else 'sell'

            # Calculate the order size based on the investment balance and leverage
            balance = self.fetch_account_balance()
            usdt_balance = balance.get('USDT', 0)
            order_size = (usdt_balance * self.leverage) / last_candle[4]

            # Place the market order
            order = self.exchange.create_market_order(self.symbol, direction, order_size)
            print(f"Placed a {direction} order for {order_size} {self.symbol} at price {last_candle[4]}")

            # Calculate stop loss and take profit prices
            stop_loss_price = last_candle[4] * (1 - self.stop_loss_pct / 100) if direction == 'buy' else last_candle[
                                                                                                             4] * (
                                                                                                                     1 + self.stop_loss_pct / 100)
            take_profit_price = last_candle[4] * (1 + self.take_profit_pct / 100) if direction == 'buy' else \
            last_candle[4] * (1 - self.take_profit_pct / 100)

            # Print TP and SL prices
            print(f"Stop Loss Price: {stop_loss_price}, Take Profit Price: {take_profit_price}")

            # Store the open order details for monitoring
            self.open_orders.append({
                'symbol': self.symbol,
                'direction': direction,
                'order_size': order_size,
                'entry_price': last_candle[4],
                'stop_loss_price': stop_loss_price,
                'take_profit_price': take_profit_price
            })

    def monitor_trades(self):
        """Monitor open trades and close them if stop loss or take profit levels are hit."""
        for order in self.open_orders:
            current_price = self.exchange.fetch_ticker(order['symbol'])['last']
            if order['direction'] == 'buy':
                if current_price <= order['stop_loss_price'] or current_price >= order['take_profit_price']:
                    self.close_order(order, current_price)
            else:
                if current_price >= order['stop_loss_price'] or current_price <= order['take_profit_price']:
                    self.close_order(order, current_price)

    def close_order(self, order, current_price):
        """Close an open order and sleep for the configured time."""
        direction = 'sell' if order['direction'] == 'buy' else 'buy'
        self.exchange.create_market_order(order['symbol'], direction, order['order_size'])
        print(f"Closed {order['direction']} order for {order['order_size']} {order['symbol']} at price {current_price}")
        self.log_trade(order, current_price)
        self.open_orders.remove(order)
        print(f"Sleeping for {self.sleep_time} minutes")
        self.sleep_with_details(self.sleep_time)

    def sleep_with_details(self, sleep_time):
        """Sleep for the given time in minutes, with detailed minute-by-minute updates."""
        for minute in range(sleep_time):
            print(f"Sleeping: {minute + 1} minute(s) out of {sleep_time}")
            time.sleep(60)  # Sleep for 1 minute

    def log_trade(self, order, exit_price):
        """Log the trade details to the CSV file."""
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                order['symbol'],
                order['direction'],
                order['order_size'],
                order['entry_price'],
                exit_price,
                order['stop_loss_price'],
                order['take_profit_price']
            ])
        print(f"Logged trade: {order['direction']} {order['order_size']} {order['symbol']} at price {exit_price}")

    def start_trading(self):
        self.fetch_account_balance()
        """Continuously check for candlestick patterns and place orders if patterns are found."""
        while True:
            try:
                self.place_order_based_on_pattern()
                self.monitor_trades()
            except Exception as e:
                print(f"An error occurred: {e}")
            print(f"Sleeing for {self.check_interval} seconds.")
            time.sleep(self.check_interval)


api_key = 'K0i6JGowF6h5VdxRDNiIZ2kKnXsKGo2lKvr2z8KQTQDmW8OqcBfHgynJCaItHWzR'
secret_key = 'zxMhTlAWqXUVmtSZK449YfeD3KKex0sHhhUbGpsuG1dtSPRTxRLxc6mOQNKNM309'

# Example usage:
trading_bot = TradingClass(
    api_key=api_key,
    secret=secret_key,
    leverage=20,
    investment_balance=10, #USDT
    stop_loss_pct=2, # percentage
    take_profit_pct=5, # percentage
    sleep_time=15,  # Sleep time in minutes
    check_interval=20,  # Check interval in seconds
    symbol='BTC/USDT',
    timeframe='1m' # Candlestick chart timeframe
)
trading_bot.connect_to_binance()
trading_bot.start_trading()
