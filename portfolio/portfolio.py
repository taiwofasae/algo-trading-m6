import pandas as pd

def list_strategies():
    return ['2022-07-23', '2022-08-21', '2022-09-18']

def load_strategy_dict(model_key):
    model = pd.read_csv(f'./submissions/{model_key}/submission.csv', index_col=0)[['Decision']]
    
    return model.T.iloc[0].to_dict()



def compute_returns(returns, portfolio):
    
    if isinstance(portfolio, str):
        portfolio = load_strategy_dict(portfolio)
    
    result = {}
    total = 0
    for key, value in returns.items():
        if key in portfolio:
            s = portfolio[key] * value
            total += s
            result[key] = s
    
    result['total'] = total
    return result, total

if __name__ == '__main__':
    compute_returns("")