import argparse
import json
import sys

from kafka import KafkaProducer

from src.data.alpaca import live_prices as alpaca_live_prices
from src.config.config import (KAFKA_BROKERS)

CRYPTO = False

DATA_PROVIDER_KEY = "data_provider"
ALPACA = "alpaca"


def live_prices(topic, symbols):
    # Pull live data from Alpaca
    print(f"Pulling live data for symbols: {symbols}")

    
    kafka_client = KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS,
        key_serializer=str.encode,
        value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    )

    # An async handler that gets called whenever new data is seen
    def data_handler(data):
        
        # Produce the record to Redpanda
        _ = kafka_client.send(
            topic,
            key=data["symbol"],
            value=data,
            timestamp_ms=data["timestamp"],
        )

        print(f"Produced record to topic: '{topic}'. Record: {data}")

    
    alpaca_live_prices.live_prices(symbols=symbols, handler=data_handler)

if __name__ == '__main__'   :

    parser = argparse.ArgumentParser(
                prog='Live prices fetch',
                description='Fetch live prices from alpaca and publishes to kafka topic',
                epilog='.')

    parser.add_argument('--topic','-t', required=True)           # positional argument
    parser.add_argument('--symbols', '-s', required=True)      # option that takes a value

    args = parser.parse_args()
    
    symbols = args.symbols.split(',')
    try:
        with open(symbols, 'r') as file:
            symbols = [line.rstrip('\n') for line in file]
    except:
        pass
    
    live_prices(topic=args.topic, symbols=symbols)