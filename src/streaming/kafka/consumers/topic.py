import argparse
import json

from kafka import KafkaProducer, KafkaConsumer
from src.config.config import KAFKA_BROKERS, KAFKA_CONSUMER_GROUP


def consume_topic(topic, handler=None, verbose=False):
    
    
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKERS,
        # group_id=KAFKA_CONSUMER_GROUP,
        auto_offset_reset="latest",
        #value_deserializer=lambda value: json.loads(value.decode("utf-8"))
        # add more configs here if you'd like
    )

    for msg in consumer:
        
        if verbose:
            print("Event!")
            print(f"message:{msg}")
        
        try:
            # get the JSON deserialized value
            record = msg.value.decode("utf-8")
            
            # "{'symbol': 'TSLA', 'timestamp': 1732567140000, 'open': 346.535, 'high': 346.72, 'low': 346.53, 'close': 346.61, 'volume': 1960.0, 'trade_count': 35.0, 'vwap': 346.596584, 'data_provider': 'alpaca'}"
            # see if too much time has elapsed between the trade signal and the current time.
            # we don't want to trade with old signals
            #record = value.dict() if isinstance(value, dict) else value
            
            if handler:
                handler(record)
        except Exception as e:
            if verbose:
                print(e)
        


if __name__ == '__main__'   :

    parser = argparse.ArgumentParser(
                prog='Live topic consumer',
                description='consume topic events',
                epilog='.')

    parser.add_argument('--topic','-t', required=True)           # positional argument

    args = parser.parse_args()
    
    consume_topic(args.topic, handler=print)