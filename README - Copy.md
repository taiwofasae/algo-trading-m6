# M6

### Setup .env file and add keys
Copy env sample file to .env  
`cp env .env`  

Provide values for:
```
ALPACA_API_KEY=  
ALPACA_SECRET_KEY=  
KAFKA_BROKERS=
```

### Install packages
`pip install -r requirements.txt`

### Test Kafka topic streams
Produce message to stream:
`python livestream\kafka\producers\topic.py -t test_topic`  
Listen on topic:
`python livestream\kafka\consumers\topic.py -t test_topic`

### Returns computation console agent (using alpaca live)
On shell,  
`python livestream\kafka\consumers\live_returns --price_topic prices --symbols "TSLA,GOOG" --returns_topic returns`

### Dashboard
### Run dashboard console agent
Either  
1. 
On a new python shell, run
```python
from analytics import dashboard
dashboard.initialize()
dashboard.RUN.returns(returns_symbols=['2022-07-23','2022-08-21','2022-09-18'],verbose=True)
```
OR  
2.  
`python analytics\dashboard.py --returns_topic returns --stock_tickers "./analytics/stocks_list.txt" --returns_symbols "2022-07-23,2022-08-21,2022-09-18" --verbose`

### Dashboard live data fetch:

On a new python shell,
```python
from analytics import dashboard
today_live_prices, all_day_prices = dashboard.STORAGE.prices.get()
today_live_returns, all_day_returns = dashboard.STORAGE.returns.get()
```
returns the live values of today's reported prices (`all_day_prices`) and most recent prices (`today_live_prices`). Similarly, Today's reported returns (`today_live_returns`) and most recent returns (`all_day_returns`).