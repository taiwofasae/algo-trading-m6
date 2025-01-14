import argparse
import json
from time import time

from kafka import KafkaProducer

from src.config.config import KAFKA_BROKERS


def send_message(topic):

    kafka_client = KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS,
        key_serializer=str.encode,
        value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    )

    while True:
        # print a separator to improve readability between multiple records
        print("-" * 30)

        # collect some inputs
        message = input("Message: > ")

        if not message:
            print("Enter something")
            continue

        
        # Produce the simulated news article to Redpanda
        try:
            future = kafka_client.send(
                topic=topic,
                key="TEST",
                value=message
            )

            # Block until the message is sent (or timeout).
            _ = future.get(timeout=60)

            print("Produced message")

        except Exception as e:
            print(e)

if __name__ == '__main__'   :

    parser = argparse.ArgumentParser(
                prog='Send message topic',
                epilog='.')

    parser.add_argument('--topic','-t', required=True)           # positional argument

    args = parser.parse_args()
    
    send_message(topic=args.topic)