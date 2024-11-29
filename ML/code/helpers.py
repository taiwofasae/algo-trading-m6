import datetime
import os
import pandas as pd
from pandas_datareader.data import DataReader

def istoday(current_date):
    return current_date.date() == datetime.datetime.today().date()

def load_stocks_data(current_date, use_buffer=True):
    date_string = current_date.strftime('%Y-%m-%d.csv')
    filename = f'stocks_data/{date_string}'

    if not istoday(current_date) and use_buffer and os.path.isfile(filename):
        # load stocks data from buffer
        print(f'buffer for {date_string} data exists!. Using buffer.')
        stocks_data = pd.read_csv(filename, index_col=0)
        stocks_data.index = pd.to_datetime(stocks_data.index)
        return stocks_data

    end = current_date
    start = datetime.datetime(end.year - 3, end.month, end.day)

    stocks_list = pd.read_csv('M6_Universe.csv')['symbol'].values.tolist()
    
    print(f'Downloading stocks from yahoo...')
    stocks_data = DataReader(stocks_list, 'yahoo', start, end)['Adj Close']

    try:
        if not os.path.exists('stocks_data/'):
            os.makedirs('stocks_data/')
        stocks_data.to_csv(filename)
    except:
        print(f'Could not store stocks data at {filename}')


    return stocks_data

def assert_dataframe_and_size(df, col_size = None, row_size = None):
    if not isinstance(df, pd.DataFrame):
        raise Exception("data not a pandas dataframe")

    if col_size and len(df.columns) != col_size:
        raise Exception("pandas dataframe not the right column size")

    if row_size and len(df.index) != row_size:
        raise Exception("pandas dataframe not the right row size")

    return True


def get_previous_trading_day(current_date, stocks_data):
    '''
    stocks data: expects a pandas dataframe with tickers as column names
    and dates as row index

    returns previous trading day
    '''

    assert_dataframe_and_size(stocks_data, 100, None)

    past_date_limit = current_date - datetime.timedelta(days=6)
    
    current_col = current_date.strftime('%Y-%m-%d')
    while current_col not in stocks_data.T.columns: # checks if current date is trading day (ie exist in stocks time stamp)
        #print(f'past date limit: {past_date_limit}; current date: {current_date}')
        current_date = current_date - datetime.timedelta(days=1)
        current_col = current_date.strftime('%Y-%m-%d')
        if current_date < past_date_limit:
            return None

    #print(f'returning {current_date}')
    return current_date

def get_trading_day_window(start_date, stocks_data, end_date = None):
    '''
    stocks data: expects a pandas dataframe with tickers as column names
    and dates as row index

    returns trading day window (previous day, last day)
    '''

    assert_dataframe_and_size(stocks_data, 100, None)
    

    previous_day = get_previous_trading_day(start_date, stocks_data)

    if not previous_day:
        raise Exception("Can't find trading window previous day")

    if end_date:
        stocks_data = stocks_data.copy()[stocks_data.index <= end_date]
        
    last_day = stocks_data.dropna(axis=0, thresh=50).T.columns[-1]

    return (previous_day, last_day)