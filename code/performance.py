import pandas as pd
import datetime
import numpy as np
import sys

import helpers
import ranking
import portfolio

# constants
date_format = '%Y-%m-%d'
m6_file = 'M6_Universe.csv'

print('Performance measure routine for M6......')

# parse input directions
submission_file = 'submission.csv'

if len(sys.argv) > 1:
    submission_file = sys.argv[1]

end = datetime.datetime.now() - datetime.timedelta(days=1)

if len(sys.argv) > 3:
    end_date = sys.argv[3]
    end = datetime.datetime.strptime(end_date, date_format)

start = end - datetime.timedelta(days=30)

if len(sys.argv) > 2:
    start_date = sys.argv[2]
    start = datetime.datetime.strptime(start_date, date_format)


# set manually
#start = datetime.datetime(2022,9,18)
#end = datetime.datetime(2022,10,9)


print(f'start date: {start.strftime(date_format)}')
print(f'end date: {end.strftime(date_format)}')



# get stocks list from M6 metadata file
file = pd.read_csv(m6_file)
stocks_list = file['symbol'].values.tolist()



# download stocks data for period
all_stocks = helpers.load_stocks_data(end, use_buffer=True)



# get previous day closing price
(previous_day, last_day) = helpers.get_trading_day_window(start, all_stocks, end)


start_col = previous_day.strftime(date_format)
end_col = last_day.strftime(date_format)

print(f'Trading window. {start_col} to {end_col}')

# extract total returns
total_returns = all_stocks.T[[start_col,end_col]].T.pct_change().round(4).T[[end_col]]

# extract ranks on total returns during period
ranks, vector_ranks = ranking.generate_rank(total_returns)

print(f'submission file:{submission_file}')

# load forecast ranks from file
file = ranking.load_submission_from_file(submission_file)

forecast_vranks = ranking.convert_submission_to_singlerankset(file)

rps = np.mean(ranking.RPS_T(vector_ranks[end_col].values.tolist(), forecast_vranks["ranks"].values.tolist()))
print(f'RPS:{rps}')


# load portfolio strategy
strategy = file[['Decision']]

daily_returns = all_stocks[all_stocks.index >= previous_day].copy()
daily_returns = daily_returns[daily_returns.index <= last_day].dropna(axis=0, how='all').pct_change().round(4).T
portfolio_returns = portfolio.calculate_portfolio_returns(daily_returns, strategy)
RET = portfolio_returns.loc[['Total'],:]

ret = np.log(1 + RET).T
total_ret = np.sum(ret.values)
print(f'total return:{total_ret}')

sdp = np.std(ret.values)
print(f'sdp:{sdp}')

ir = total_ret / sdp
print(f'IR:{ir}')