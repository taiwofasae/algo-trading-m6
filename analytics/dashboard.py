import argparse
import json
import os
import datetime
import yfinance as yf
import pandas as pd
from multiprocessing import Process
from livestream.kafka.consumers import topic
from data import market


DATE_FORMAT = '%Y-%m-%d'
THIRTYDAYS_FOLDER_PATH_FORMAT = './analytics/30days/{0}.csv'
STOCKS_LIST_PATH = './analytics/stocks_list.txt'


TODAY_LIVE_PRICES_FILEPATH = './analytics/live/today_live_prices.json'
ALL_DAY_PRICES_FILEPATH = './analytics/live/all_day_prices.json'
TODAY_LIVE_RETURNS_FILEPATH = './analytics/live/today_live_returns.json'
ALL_DAY_RETURNS_FILEPATH = './analytics/live/all_day_returns.json'

TODAY_LIVE_AND_30DAY_RETURNS_FILEPATH = './analytics/live/today_live_and_30d_returns.csv'
ALL_DAY_AND_30DAY_RETURNS_FILEPATH = './analytics/live/all_day_and_30d_returns.csv'


THIRTYDAYS_DF = None

# TODAY_LIVE_PRICES = {}
# ALL_DAY_PRICES = []
# TODAY_LIVE_RETURNS = {}
# ALL_DAY_RETURNS = []

# def prices():
#     return TODAY_LIVE_PRICES, ALL_DAY_PRICES

# def returns():
#     return TODAY_LIVE_RETURNS, ALL_DAY_RETURNS 

class STORAGE:
    class prices:
        def get():
            with open(TODAY_LIVE_PRICES_FILEPATH, 'r') as f:
                today_live_prices = json.load(f)
            
            with open(ALL_DAY_PRICES_FILEPATH, 'r') as f:
                all_day_prices = json.load(f)
                
            return today_live_prices, all_day_prices
        
        def set(today_live_prices, all_day_prices):
            with open(TODAY_LIVE_PRICES_FILEPATH, 'w') as f:
                json.dump(today_live_prices, f)
                
            with open(ALL_DAY_PRICES_FILEPATH, 'w') as f:
                json.dump(all_day_prices, f)
        
    class returns:
        def get():
            with open(TODAY_LIVE_RETURNS_FILEPATH, 'r') as f:
                today_live_returns = json.load(f)
            
            with open(ALL_DAY_RETURNS_FILEPATH, 'r') as f:
                all_day_returns = json.load(f)
                
            return today_live_returns, all_day_returns
        
        def set(today_live_returns, all_day_returns):
            with open(TODAY_LIVE_RETURNS_FILEPATH, 'w') as f:
                json.dump(today_live_returns, f)
                
            with open(ALL_DAY_RETURNS_FILEPATH, 'w') as f:
                json.dump(all_day_returns, f)
                
    class _30day_returns:
        def get():
            today_live_and_30d_returns = _load_df(TODAY_LIVE_AND_30DAY_RETURNS_FILEPATH)
            
            all_day_and_30d_returns = _load_df(ALL_DAY_RETURNS_FILEPATH)
                
            return today_live_and_30d_returns, all_day_and_30d_returns
        
        def set(today_live_and_30d_returns, all_day_and_30d_returns):
            today_live_and_30d_returns.to_csv(TODAY_LIVE_AND_30DAY_RETURNS_FILEPATH)
            
            all_day_and_30d_returns.to_csv(ALL_DAY_AND_30DAY_RETURNS_FILEPATH)

def initialize():
    STORAGE.prices.set(today_live_prices={}, all_day_prices=[])
    STORAGE.returns.set(today_live_returns={}, all_day_returns=[])
    STORAGE._30day_returns.set(today_live_and_30d_returns=pd.DataFrame({}), all_day_and_30d_returns=pd.DataFrame({}))

class RUN:
    def prices(price_topic, verbose=False):
        # consume price topic
        topic.consume_topic(price_topic, handler=SET_LIVE.prices, verbose=verbose)
        
    def returns(returns_topic, returns_symbols, stocks_list=None, verbose=False):
        # consume returns topic
        topic.consume_topic(returns_topic, handler=lambda x: SET_LIVE.returns(x, returns_symbols, stocks_list=stocks_list), verbose=verbose)
    
class SET_LIVE:
    def prices(data):
        
        if 'symbol' in data:
            print(f"Price event!")
            record = json.loads(data)
            
            TODAY_LIVE_PRICES, ALL_DAY_PRICES = STORAGE.prices.get()
        
            TODAY_LIVE_PRICES['timestamp'] = record['timestamp']
            TODAY_LIVE_PRICES[record['symbol']] = record['close']
            ALL_DAY_PRICES.append({'symbol': record['symbol'],
                                    'value': record['close'],
                                    'timestamp': record['timestamp']})
        
            sort_by_timestamp(ALL_DAY_PRICES)
            STORAGE.prices.set(TODAY_LIVE_PRICES, ALL_DAY_PRICES)
            
            
    def returns(data, returns_symbols, stocks_list=None):
        
        if 'symbol' in data:
            record = json.loads(data)
        
            if record.get('symbol', None) == 'RETURNS':
                print("Returns event!")
                
                
                TODAY_LIVE_RETURNS, ALL_DAY_RETURNS = STORAGE.returns.get()
                
                
                TODAY_LIVE_RETURNS['timestamp'] = record['timestamp']
                for symbol in returns_symbols:
                    if symbol in record:
                        TODAY_LIVE_RETURNS[symbol] = record.get(symbol)
                ALL_DAY_RETURNS.append(TODAY_LIVE_RETURNS)
            
                sort_by_timestamp(ALL_DAY_RETURNS)
                STORAGE.returns.set(TODAY_LIVE_RETURNS, ALL_DAY_RETURNS)
                
                
                # append today live returns to 30day
                THIRTYDAY_RETURNS = _get_thirtydays(stocks_list=stocks_list)
                TODAY_LIVE_AND_30DAY_RETURNS = append_dict_to_dataframe(THIRTYDAY_RETURNS, TODAY_LIVE_RETURNS)
                ALL_DAY_AND_30DAY_RETURNS = append_list_to_dataframe(THIRTYDAY_RETURNS, ALL_DAY_RETURNS)
                STORAGE._30day_returns.set(today_live_and_30d_returns=TODAY_LIVE_AND_30DAY_RETURNS,
                                        all_day_and_30d_returns=ALL_DAY_AND_30DAY_RETURNS)
            
        
def sort_by_timestamp(f):
    f.sort(key=lambda p: p['timestamp'], reverse=True)
    
def resample_timestamp(f, interval='15min'):
    df = pd.DataFrame(f)
    df.index = pd.to_datetime(df['timestamp'], unit='s')
    # TODO: get last in previous interval instead
    return df.resample(interval).last()

def _get_stocks_list():
    
    with open(STOCKS_LIST_PATH, 'r') as file:
        stocks_list = [line.rstrip('\n') for line in file]
    return stocks_list

def _get_date_str(today=None):
    if not today:
        today = datetime.datetime.now()
    
    if isinstance(today, str):
        today = datetime.datetime.strptime(today, DATE_FORMAT)
        
    today_str = today.strftime(DATE_FORMAT)
        
    return today, today_str

def _load_df(filepath):
    df = pd.read_csv(filepath, index_col=0)
    df['date_str'] = df.index
    df['Date'] = pd.to_datetime(df.index, format=DATE_FORMAT)
    df.set_index('Date', inplace=True)
    return df

def _get_thirtydays(today=None, stocks_list=None):
    global THIRTYDAYS_DF
    if THIRTYDAYS_DF is not None:
        return THIRTYDAYS_DF
    
    today, today_str = _get_date_str(today)
    
    stocks_list = stocks_list or _get_stocks_list()
    
    # get past 30 days
    if not os.path.exists(THIRTYDAYS_FOLDER_PATH_FORMAT.format(today_str)):
        returns = market.get_30day_returns(symbols=stocks_list, today=today)
        returns.to_csv(THIRTYDAYS_FOLDER_PATH_FORMAT.format(today_str))
    
    THIRTYDAYS_DF = _load_df(THIRTYDAYS_FOLDER_PATH_FORMAT.format(today_str))
    return THIRTYDAYS_DF

def _get_live():
    # connect to database
    pass

def _get_today_events():
    # connect to streams
    pass

def append_dict_to_dataframe(df, d):
    df['Date'] = df.index
    d['Date']=pd.to_datetime(d['timestamp'], unit='s')
    df = pd.concat([df, pd.DataFrame([d])])
    return df.set_index('Date').drop('timestamp', axis=1)

def append_list_to_dataframe(df, dl):
    df['Date'] = df.index
    for item in dl:
        item['Date']=pd.to_datetime(item['timestamp'], unit='s')
    df = pd.concat([df, pd.DataFrame(dl)])
    return df.set_index('Date').drop('timestamp', axis=1)

def thirtydays():
    
    # get 30-day data
    returns = _get_thirtydays()
    
    # get today live data, compute returns
    today_live_returns, all_day_returns = STORAGE.returns.get()
    
    # append on live data to 30-day data
    
    # plot
    pass

def thirtydays_and_today(today=None):
    
    # get 30-day data
    returns = _get_thirtydays(datetime.datetime.now())
    
    # get all live events today, compute returns
    today_live_returns, all_day_returns = STORAGE.returns.get()
    
    # append all live events to 30-day data
    
    # plot 
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog='Live dashboard console agent',
                description='Fetch live prices, compute returns, and store for dashboard live fetch',
                epilog='.')

    parser.add_argument('--returns_topic','-t', required=True)           
    parser.add_argument('--stock_tickers', '-s', required=False)     
    parser.add_argument('--returns_symbols','-rs', required=False)          
    parser.add_argument('--reset','-r', action="store_true")           
    parser.add_argument('--verbose','-v', action="store_true")           

    args = parser.parse_args()
    
    if args.reset:
        print(f"initializing storage...")
        initialize()
    
    stock_tickers = market.get_symbols(args.stock_tickers)
    returns_symbols = market.get_symbols(args.returns_symbols)
    
    RUN.returns(returns_topic=args.returns_topic, returns_symbols=returns_symbols or ['2022-07-23','2022-08-21','2022-09-18'],
                stocks_list=stock_tickers,
                verbose=True)