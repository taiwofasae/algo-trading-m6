import helpers

def calculate_portfolio_returns(daily_returns, strategy):
    '''
    daily_returns: expects a dataframe with trading day as columns,
    and ticker as row index.
    strategy: expects a dataframe with 'Decision' as column, 
    and ticker as row index

    returns dataframe same size as daily_returns plus a 'total' row
    '''

    helpers.assert_dataframe_and_size(daily_returns, row_size=100)

    helpers.assert_dataframe_and_size(strategy, row_size=100)

    assert daily_returns.index[0] == 'ABBV', f"daily_returns dataframe, first ticker expected as ABBV, got {daily_returns.index[0]}"
    assert strategy.index[0] == 'ABBV', f"strategy dataframe, first ticker expected as ABBV, got {daily_returns.index[0]}"

    decision = strategy['Decision'].sort_index()
    portfolio_returns = daily_returns.copy().sort_index()
    for col in portfolio_returns.columns:
        portfolio_returns[col] = portfolio_returns[col] * decision

    portfolio_returns.loc['Total'] = portfolio_returns.sum()


    return portfolio_returns