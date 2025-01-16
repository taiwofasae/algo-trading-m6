from jupyter_dash import JupyterDash
from dash import Dash, dcc, html, Input, Output
import yfinance as yf  
import plotly.express as px
from analytics import dashboard
from datetime import datetime
import pandas as pd

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TIME_FORMAT = '%H:%M:%S'
DATE_FORMAT = '%Y-%m-%d'
DATE_UPDATE_FORMAT = 'refreshed at {0}, last updated at {1}'

def date_update_string(refresh : datetime, last_update : datetime):
    return DATE_UPDATE_FORMAT.format(refresh.strftime(TIME_FORMAT), last_update.strftime(DATETIME_FORMAT))

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Stock Price Analysis Dashboard'),
    html.H2(children='Live returns of stocks'),
    html.Label('Select Stock Symbol'),
    dcc.Checklist(
        id='live-stock-selector',
        options=['AAPL','GOOG','MSFT','2022-07-23','2022-08-21','2022-09-18'],
        value=['2022-07-23','2022-08-21','2022-09-18']
    ),
    
    dcc.Graph(id='today-live-returns-chart'),
    dcc.Graph(id='allday-live-returns-chart'),
    
    html.H2(children='30-day returns of stocks'),
    html.Label('Select Stock Symbol'),
    dcc.Checklist(
        id='30day-stock-selector',
        options=['AAPL','GOOG','MSFT','2022-07-23','2022-08-21','2022-09-18'],
        value=['2022-07-23','2022-08-21','2022-09-18']
    ),
    
    dcc.Graph(id='today-30day-live-returns-chart'),
    dcc.Graph(id='allday-30day-live-returns-chart'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),
])


@app.callback(
    Output('today-live-returns-chart', 'figure'),
    [Input('live-stock-selector', 'value')]
)
def update_today_live(selected_stocks):
    
    today_live_returns, all_day_returns = dashboard.STORAGE.returns.get()
    
    tickers = sorted([_ for _ in today_live_returns.keys() if _ in selected_stocks])
    live_returns = [today_live_returns[x] for x in tickers]

    df = pd.DataFrame(zip(tickers, live_returns), columns=['TICKER', 'Live returns'])
    df['direction'] = ['up' if x > 0 else 'down' for x in live_returns]

    timestamp = datetime.fromtimestamp(today_live_returns['timestamp'])
    df['labels'] = [timestamp.strftime(TIME_FORMAT) if timestamp.date() == datetime.today().date() else timestamp.strftime(DATE_FORMAT) for _ in tickers]


    fig = px.bar(df, x='TICKER', y='Live returns',
                color='direction',
                color_discrete_sequence =['red','green'],
                hover_data=['Live returns'],
                text='labels',
                title=f'Today live returns, {date_update_string(datetime.now(), timestamp)}',
                height=400)
    fig.update_layout(xaxis=dict(type='category')) # type update to category
    # Set the y-axis range
    fig.update_yaxes(range=[-0.1, 0.1])
    
    # fig = px.bar(df, x='year', y='pop',
    #          hover_data=['lifeExp', 'gdpPercap'], color='country',
    #          labels={'pop':'population of Canada'}, height=400)
    
    # fig = px.line(stock_data, x=stock_data.index, y='Close',
    #               title=f'{selected_stocks[0]} Stock Price Analysis')
    return fig

@app.callback(
    Output('allday-live-returns-chart', 'figure'),
    [Input('live-stock-selector', 'value')]
)
def update_allday_live(selected_stocks):
    
    today_live_returns, all_day_returns = dashboard.STORAGE.returns.get()

    df = pd.DataFrame(all_day_returns)
    df['Date'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df.drop('timestamp', axis=1).set_index('Date')[df.columns.intersection(selected_stocks)]
    
    latest_timestamp = df.index[-1]

    fig = px.line(df,title=f'All day live returns, {date_update_string(datetime.now(), latest_timestamp)}')
    fig.update_layout(legend_title_text='TICKER')
    # Set the y-axis range
    fig.update_yaxes(range=[-0.1, 0.1],title='Live returns')
    return fig

## 30-day returns

@app.callback(
    Output('today-30day-live-returns-chart', 'figure'),
    [Input('30day-stock-selector', 'value')]
)
def update_today_30day(selected_stocks):
    
    today_live_and_30d_returns, all_day_and_30d_returns = dashboard.STORAGE._30day_returns.get()
    
    df = today_live_and_30d_returns[today_live_and_30d_returns.columns.intersection(selected_stocks)]
    latest_timestamp = df.index[-1]

    fig = px.line(df,title=f'30-day live returns, {date_update_string(datetime.now(), latest_timestamp)}')
    fig.update_layout(legend_title_text='TICKER')
    # Set the y-axis range
    fig.update_yaxes(range=[-0.1, 0.1],title='Live returns')
    return fig

@app.callback(
    Output('allday-30day-live-returns-chart', 'figure'),
    [Input('30day-stock-selector', 'value')]
)
def update_allday_30day(selected_stocks):
    
    today_live_and_30d_returns, all_day_and_30d_returns = dashboard.STORAGE._30day_returns.get()
    
    df = all_day_and_30d_returns[all_day_and_30d_returns.columns.intersection(selected_stocks)]
    latest_timestamp = df.index[-1]


    fig = px.line(df,title=f'All day 30-day live returns, {date_update_string(datetime.now(), latest_timestamp)}')
    fig.update_layout(legend_title_text='TICKER')
    # Set the y-axis range
    fig.update_yaxes(range=[-0.1, 0.1],title='Live returns')
    return fig
    

if __name__ == '__main__':
    app.run_server(port=8050, debug=True)