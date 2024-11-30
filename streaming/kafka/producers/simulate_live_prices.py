import argparse
import json
from time import time

from kafka import KafkaProducer

from config.config import KAFKA_BROKERS


def live_prices(topic):

    kafka_client = KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS,
        key_serializer=str.encode,
        value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    )

    while True:
        # print a separator to improve readability between multiple records
        print("-" * 30)

        # collect some inputs
        symbol = input("Symbol (e.g. TSLA) > ")
        close_price = input("Price > ")

        if not symbol or not close_price:
            print("Both fields are required")
            continue

        article = {}
        article["symbol"] = symbol
        article["close"] = float(close_price)
        article["timestamp"] = int(time())
        article["data_provider"] = "price simulator"

        try:
            future = kafka_client.send(
                topic=topic,
                key=article["symbol"],
                value=article,
                timestamp_ms=article["timestamp"],
            )

            # Block until the message is sent (or timeout).
            _ = future.get(timeout=30)

            print("Produced price record")

        except Exception as e:
            print(e)

if __name__ == '__main__'   :

    parser = argparse.ArgumentParser(
                prog='Simulate live prices fetch',
                epilog='.')

    parser.add_argument('--topic','-t', required=True)           # positional argument

    args = parser.parse_args()
    
    live_prices(topic=args.topic)