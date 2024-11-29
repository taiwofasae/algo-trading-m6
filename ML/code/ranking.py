import pandas as pd
import numpy as np
import helpers

# extract total ranks
def generate_rank(df):
    '''
    df: expect pandas dataframe with dates as column names,
    and ticker names as row index
    '''

    helpers.assert_dataframe_and_size(df, row_size = 100)

    ranks = pd.DataFrame(index=df.index, columns=df.columns)
    vector_ranks = pd.DataFrame(index=df.index, columns=df.columns)
    
    for col in df.columns:
        if df[col].isnull().all():
            continue
        ranks[col], vector_ranks[col] = generate_rank_from_values(df[col].values)
        
    return ranks, vector_ranks

def generate_rank_from_values(value_list):
    if len(value_list) != 100:
        raise Exception('Values list not 100 in number')
        
    df = pd.DataFrame(value_list, columns=['data'])
    orig_index = df.index
    #df[241] = [random.randint(1,20) for i in range(100)]
    df = df.sort_values('data',ascending=False)
    df['my100rank'] = range(100,0,-1)
    df['my5rank'] = [5]*20 + [4]*20 + [3]*20 + [2]*20 + [1]*20
    df['pyrank'] = df['data'].rank()
    df['5rank'] = pd.qcut(df['data'], 5, labels=False, precision=1) + 1
    df['diff'] = df['my5rank'] != df['5rank']
    uniq_ranks = df[df['diff'] == True]['pyrank'].unique()
    df['adjusted5rank'] = df['my5rank']
    df['rankvector'] = np.nan
    
    df = df.join(pd.get_dummies(df['my5rank']))
    
    
    # ties on the margins of the classes
    for rank in uniq_ranks:
        rank_index = df[df['pyrank']==rank].index
        population = df['my5rank'][rank_index]
        df.loc[rank_index,'adjusted5rank'] = round(population.mean(),2)
        for p in population:
            df.loc[rank_index, p] = round(sum(population == p) / len(population),2)
            
    
    
    #print(df.to_string())
    ranks = df['adjusted5rank'][orig_index].values.tolist()
    vector_ranks = []
    for index, row in df.loc[orig_index].iterrows():
        vector_ranks.append([row[1],row[2],row[3],row[4],row[5]])
    
    # clean house
    for p in [1,2,3,4,5]:
        df[f'Rank {p}'] = df[p]
    df = df.drop(columns=[1,2,3,4,5])
    return ranks, vector_ranks

def RPS(df, predictions):
    '''
    df: expect pandas dataframe with dates as column names (time T),
    and ticker names as row index (i)
    predictions: expect enumerable of 5-element list

    return: dataframe of same size as df but with RPS (rank 
    performance score) values by time T and ticker i
    '''

    helpers.assert_dataframe_and_size(df, row_size = 100)

    result = pd.DataFrame(index=df.index, columns=df.columns)
    
    for col in df.columns:
        if df[col].isnull().all():
            continue
        result[col] = RPS_T(df[col].values, predictions)
        
    return result

def RPS_T(actual, predictions):
    '''
    actual, predictions: expect an enumerable of 5-element list
    return: list of RPS values for each enumerable
    '''
    result = []
    for x,y in zip(actual, predictions):
        result.append(RPS_i_T(x,y))
        
    return result

def RPS_i_T(actual, predictions):
    '''
    actual, predictions: each expect a 5-element list representing the
    rank vector
    '''
    actual, predictions = np.array(actual), np.array(predictions)
    return np.mean((predictions - actual) ** 2)

def convert_single_rankset_to_submission(df):
    '''
    df: expects dataframe with dates as single column name (time T),
    and ticker names as row index (i)
    return: dataframe with same row size as df, but 6 columns (ranks 1-5)
    '''
    pass

def load_submission_from_file(filename):
    '''
    filename: expect string
    return: dataframe with 100 rows
    '''

    file = pd.read_csv(filename)
    file['Symbols'] = file[file.columns[0]]
    file.index = file['Symbols']

    return file


def convert_submission_to_singlerankset(df):
    '''
    df: expects dataframe with at least 5 columns (ranks 1-5),
    and ticker names as row index (i)
    return: dataframe with same row size as df, but single column
    '''

    #helpers.assert_dataframe_and_size(df, row_size=5)

    forecast_vranks = df.copy().filter(df.index)
    forecast_vranks['ranks'] = np.nan
    forecast_vranks = forecast_vranks.T

    for index,row in df.iterrows():
        ticker = row['Symbols']
        ranks = [row['Rank 1'], row['Rank 2'], row['Rank 3'], row['Rank 4'], row['Rank 5']]
        forecast_vranks[ticker] = [ranks]

    forecast_vranks = forecast_vranks.T
    return forecast_vranks

