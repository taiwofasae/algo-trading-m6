import argparse
import json
import sys

from kafka import KafkaProducer, KafkaConsumer
from src.config.config import KAFKA_BROKERS, KAFKA_CONSUMER_GROUP
from src.portfolio import portfolio
from src.data import market

DATA_PROVIDER_KEY = "data_provider"



def run_live_returns(symbols, price_topic, returns_topic):
    
    
    consumer = KafkaConsumer(
        price_topic,
        bootstrap_servers=KAFKA_BROKERS,
        # group_id=KAFKA_CONSUMER_GROUP,
        auto_offset_reset="latest",
        # value_deserializer=lambda value: json.loads(value.decode("utf-8"))
        # add more configs here if you'd like
    )
    
    # Get a Redpanda client instance
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKERS,
        key_serializer=str.encode,
        value_serializer=lambda m: json.dumps(m).encode("utf-8"),
    )
    
    portfolio_strategies = portfolio.list_strategies()
    portfolios = [portfolio.load_strategy_dict(key) for key in portfolio_strategies]
    previous_day_prices = market.get_previous_day_prices(symbols=symbols)
    today_live_prices = {} # symbol : price
    today_live_returns = {} # strategy : return
    all_day_returns = [] # item: (timestamp, symbol, returns)

    for msg in consumer:
        
        try:
            # get the JSON deserialized value
            record = json.loads(msg.value.decode("utf-8"))
            
            # "{'symbol': 'TSLA', 'timestamp': 1732567140000, 'open': 346.535, 'high': 346.72, 'low': 346.53, 'close': 346.61, 'volume': 1960.0, 'trade_count': 35.0, 'vwap': 346.596584, 'data_provider': 'alpaca'}"
            # see if too much time has elapsed between the trade signal and the current time.
            # we don't want to trade with old signals
            
            if 'symbol' not in record:
                print(f'No symbol found in message. Skipping')
                continue
        
        
            symbol, live_price = record['symbol'], record['close']
            
            # update live prices
            today_live_prices[symbol] = live_price
            # print(f"today_live_prices:{today_live_prices}")
            # print(f"previous_day_prices:{previous_day_prices}")
            
            # compute live returns
            live_returns = market.compute_returns(previous_day=previous_day_prices, current_day=today_live_prices)
            
            print(f"live_returns:{live_returns}")
            # Format the timestamp to milliseconds
            timestamp_ms = int(record["timestamp"])
            record = {"timestamp" : timestamp_ms, "symbol": "RETURNS"}
            
            # one event for all strategies (can consider one event per strategy)
            for strategy, p in zip(portfolio_strategies, portfolios):
                # compute and update live returns
                _, strategy_return = portfolio.compute_returns(returns=live_returns, portfolio=p)
                #today_live_returns[strategy] = strategy_return
                record[strategy] = strategy_return


            # Produce the record to different topic
            _ = producer.send(
                returns_topic,
                key=record["symbol"],
                value=record,
                timestamp_ms=record["timestamp"],
            )

            print(f"Produced record to topic: {returns_topic}. Record: {record}")
            
        except Exception as e:
            print(e)
            print("Returns computation failed.")



if __name__ == '__main__'   :

    parser = argparse.ArgumentParser(
                prog='Live returns computer',
                description='Fetch live prices from kafka topic and publishes to another kafka topic',
                epilog='.')

    parser.add_argument('--price_topic','-p', required=True)           # positional argument
    parser.add_argument('--symbols', '-s', required=True)      # option that takes a value
    parser.add_argument('--returns_topic','-r', required=True)           # positional argument

    args = parser.parse_args()
    
    symbols = market.get_symbols(args.symbols)
    
    run_live_returns(symbols=symbols, price_topic=args.price_topic, returns_topic=args.returns_topic)