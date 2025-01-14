import argparse
import json
import sys
import os

from src.data.alpaca import alpaca_utils


CRYPTO = False

DATA_PROVIDER_KEY = "data_provider"
ALPACA = "alpaca"


def live_prices(symbols, handler):
    # Pull live data from Alpaca
    print(f"Pulling live data for symbols: {symbols}")

    # Make sure the market is open. Otherwise, we can't pull live data
    market_clock = alpaca_utils.get_clock()
    if not market_clock.is_open:
        print(
            "Can't pull live data because the market is not open. Please try again when the market is open."
        )
        sys.exit(0)

    # Get a Alpaca client instance
    alpaca_client = alpaca_utils.get_live_client(crypto=CRYPTO)

    # An async handler that gets called whenever new data is seen
    async def data_handler(data):
        record = data.dict()

        # Format the timestamp to milliseconds
        timestamp_ms = int(record["timestamp"].timestamp())
        record["timestamp"] = timestamp_ms

        # Add an identifier for the data provider
        record[DATA_PROVIDER_KEY] = ALPACA

        handler(record)

    alpaca_client.subscribe_bars(data_handler, *symbols)
    # subscribe_bars, subscribe_updated_bars, subscribe_daily_bars, subscribe_trades, subscribe_quotes

    alpaca_client.run()

if __name__ == '__main__'   :

    parser = argparse.ArgumentParser(
                prog='Live prices fetch',
                description='Fetch live prices from alpaca',
                epilog='.')

    parser.add_argument('--symbols', '-s', required=True)      # option that takes a value

    args = parser.parse_args()
    
    symbols = args.symbols
    symbols = symbols.split(',')
    if len(symbols) == 1:
        filepath = symbols[0]
        try:
            with open(filepath, 'r') as file:
                symbols = [line.rstrip('\n') for line in file]
        except Exception as e:
            print(e)
            print(f"failure opening file: {filepath}")
            
    symbols = [s for s in symbols if s]
        
    live_prices(symbols=symbols, handler= lambda x: print(x))