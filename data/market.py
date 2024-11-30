import datetime
import os
import sys
import yfinance as yf
import pandas as pd

DATE_FORMAT = '%Y-%m-%d'


def _get_date_str(today=None):
    if not today:
        today = datetime.datetime.now()
    
    if isinstance(today, str):
        today = datetime.datetime.strptime(today, DATE_FORMAT)
        
    today_str = today.strftime(DATE_FORMAT)
        
    return today, today_str

def get_30day_prices(symbols : list[str], today=None):
    
    # all_stocks = dashboard._get_thirtydays(today-datetime.timedelta(1))
    # all_stocks['Date'] = pd.to_datetime(all_stocks.index, format=DATE_FORMAT) 
    # all_stocks.set_index('Date',inplace=True)
    # return all_stocks
    today, today_str = _get_date_str(today)
    
    print(f"downloading 30-day data for '{today_str}'")
    
    end = today.date() # strip of current time
    start = end - datetime.timedelta(days=31)

    
    all_stocks = yf.download(symbols, start=start, end=end)

    return all_stocks['Adj Close']
  
def get_30day_returns(symbols : list[str], today=None):
    
    today, today_str = _get_date_str(today)
    
    prices = get_30day_prices(symbols=symbols, today=today)
    
    return prices.pct_change().round(3)

def get_previous_day_prices(symbols):
    
    if len(symbols) < 2:
        print(f"provide more than one ticker")
        sys.exit()
    
    # TODO: if market closed, then use today
    
    prices = get_30day_prices(symbols=symbols, today=datetime.datetime.now())
    prices['date_str'] = prices.index.strftime(DATE_FORMAT)
    
    return prices.loc[prices.index[-1]]

def compute_returns(previous_day, current_day):
    
    returns = {}
    
    for key, value in current_day.items():
        if key in previous_day:
            returns[key] = (value - previous_day[key]) / previous_day[key]
            
    return returns

def get_symbols(symbols):
    
    if isinstance(symbols, str):
        symbols = symbols.split(',')
        
    if len(symbols) == 1:
        symbols = symbols[0]
        try:
            with open(symbols, 'r') as file:
                symbols = [line.rstrip('\n') for line in file]
        except:
            pass
        
    return symbols

if __name__ == '__main__':
    print(get_previous_day_prices(['TSLA','GOOG']))