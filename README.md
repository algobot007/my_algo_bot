Trading Bot for Binance Futures
This repository contains a Python-based algorithmic trading bot designed for Binance Futures using the CCXT library. The bot is capable of executing trades based on predefined parameters and managing positions with stop-loss and take-profit mechanisms.

Features
Connect to Binance Futures: Securely connect to Binance Futures using API keys.
Fetch Account Balance: Retrieve and display the account balance.
Trading Strategy Implementation: Execute trades based on custom strategies.
Stop-Loss and Take-Profit: Manage trades with stop-loss and take-profit settings.
Logging: Log trading activities to a CSV file for analysis and record-keeping.
Requirements
Python 3.6+
CCXT Library
Binance API Keys
Installation
Clone the repository:


git clone https://github.com/yourusername/trading-bot-binance-futures.git
cd trading-bot-binance-futures
Install the required libraries:


pip install ccxt
Usage
Configure your API keys and parameters in the script:


api_key = 'YOUR_API_KEY'
secret = 'YOUR_API_SECRET'
leverage = 10
investment_balance = 1000  # Example balance in USDT
stop_loss_pct = 0.05  # 5%
take_profit_pct = 0.1  # 10%
sleep_time = 60  # Time in seconds
check_interval = 5  # Interval to check price in seconds
symbol = 'BTC/USDT'
timeframe = '1m'
Run the script:


python Bot_1_futures_final_script.py
Class Methods
__init__
Initialize the trading class with the following parameters:

api_key: Binance API key.
secret: Binance API secret.
leverage: Leverage for trading.
investment_balance: Amount to be used for trading.
stop_loss_pct: Stop-loss percentage.
take_profit_pct: Take-profit percentage.
sleep_time: Time to sleep between checks.
check_interval: Interval to check the price.
symbol: Trading pair symbol.
timeframe: Timeframe for candlestick data.
initialize_log_file
Initialize the CSV log file with headers.

connect_to_binance
Connect to Binance Futures using the provided API key and secret.

fetch_account_balance
Fetch and display the account balance.


from trading_bot import TradingClass

# Initialize the bot with your configuration
bot = TradingClass(api_key, secret, leverage, investment_balance, stop_loss_pct, take_profit_pct, sleep_time, check_interval, symbol, timeframe)

# Connect to Binance Futures
bot.connect_to_binance()

# Fetch account balance
bot.fetch_account_balance()
Logging
The bot logs all trades in trade_log.csv with the following columns:

timestamp: Time of the trade.
symbol: Trading pair.
direction: Buy or Sell.
order_size: Size of the order.
entry_price: Price at which the trade was executed.
exit_price: Price at which the trade was closed.
stop_loss: Stop-loss price.
take_profit: Take-profit price.
Disclaimer
This bot is intended for educational purposes only. Trading cryptocurrencies carries a high level of risk, and you should only trade with money you can afford to lose. The author is not responsible for any financial losses you may incur.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
For any inquiries or support, please open an issue on this repository.

