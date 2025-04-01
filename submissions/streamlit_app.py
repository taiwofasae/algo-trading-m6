import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set Streamlit to use wide layout
st.set_page_config(layout="wide")

@st.cache_data
def load_data(date_key):

    df = pd.read_csv(f'{date_key}/submission.csv')

    # return tickers, ranks, weights
    return df[df.columns[0]].values, df[['Rank 1', 'Rank 2', 'Rank 3', 'Rank 4', 'Rank 5']], df['Decision'].values

def plot_portfolio_strategy(tickers, weights):
    # Sample time-based data (hourly bins)
    data = {
        "Ticker": tickers,
        "Weights": weights
    }
    df = pd.DataFrame(data)

    # Ensure Timestamp is in datetime format
    df["Ticker"] = pd.Categorical(df["Ticker"])

    # Create bar chart with red bars
    fig = px.bar(df, x="Ticker", y="Weights", title="Portfolio weights",
                color_discrete_sequence=["red"])  # Red bars

    # Format the x-axis to ensure evenly spaced bins from 12 AM to 11:59 PM
    fig.update_layout(
        # xaxis=dict(
        #     tickformat="%I %p",  # Display time as 12-hour format (AM/PM)
        #     dtick=3600 * 1000  # One-hour bins
        # ),
        bargap=0.0  # Adjust bar spacing
    )

    # Add a grid to the chart
    fig.update_layout(
        xaxis_showgrid=True,
        yaxis_showgrid=True
    )

    fig.update_layout(
        height=300  # Set the height of the plot
    )

    # Display in Streamlit
    st.plotly_chart(fig)

def plot_rank_predictions(tickers, df):
    
    df = df[['Rank 1', 'Rank 2', 'Rank 3', 'Rank 4', 'Rank 5'][::-1]]

    # st.dataframe(df.T)
    # Create a heatmap using imshow()
    fig = px.imshow(df.T,  # Transpose to align categories correctly
                    labels={"x": "Ticker", "y": "Rank (1-5)", "color": "Weight"},
                    color_continuous_scale="viridis")  # Choose a colormap (e.g., 'viridis', 'plasma')

    # Adjust layout for better visualization
    fig.update_layout(
        title="Rank prediction",
        xaxis=dict(tickmode="array", tickvals=list(range(100)), ticktext=tickers),  
        yaxis=dict(tickmode="array", tickvals=list(range(5)), ticktext=df.columns),  # Label rows
        coloraxis_colorbar=dict(title="P{rank}")  # Color legend
    )

    fig.update_layout(
        height=300  # Set the height of the plot
    )

    # Set the colormap range
    fig.update_coloraxes(cmin=0, cmax=1)  # Adjust the range as needed

    # Display in Streamlit
    st.plotly_chart(fig)

def plot_month(date_key):

    # Parse the date string to ensure it's in the correct format
    try:
        date_time = pd.to_datetime(date_key, format='%Y-%m-%d')
    except ValueError:
        st.error("Invalid date format.")
        return
    
    # Format the date into "Month Year" format
    st.subheader(date_time.strftime("%B %Y"))
    tickers, df, weights = load_data(date_key=date_key)
    plot_portfolio_strategy(tickers=tickers, weights=weights)

    plot_rank_predictions(tickers=tickers, df=df)


def plot_summary(dates):

    st.subheader('Summary: Portfolio Weights across months')

    df_all = None
    for date_key in dates:
        tickers, df, weights = load_data(date_key=date_key)
        df = pd.DataFrame({'Ticker': tickers, date_key: weights}).set_index('Ticker')
        df_all = df if df_all is None else pd.concat([df_all, df], axis=1)

    df_all = df_all.reset_index()
    tickers = df_all['Ticker'].values
    df_all = df_all[dates]


    # Format the column names as month names
    col_names = [pd.to_datetime(col, format='%Y-%m-%d').strftime("%b %Y") for col in df_all.columns]
    df_all.columns = col_names


    # Create a heatmap using imshow()
    fig = px.imshow(df_all.T,  # Transpose to align categories correctly
                    labels={"x": "Ticker", "y": "Month", "color": "Intensity"},
                    color_continuous_scale="plasma")  # Choose a colormap (e.g., 'viridis', 'plasma')

    

    # Adjust layout for better visualization
    fig.update_layout(
        title="Portfolio Weights",
        xaxis=dict(tickmode="array", tickvals=list(range(len(tickers))), ticktext=tickers),  
        yaxis=dict(tickmode="array", tickvals=list(range(len(col_names))), ticktext=col_names),  # Use formatted month names
        coloraxis_colorbar=dict(title="Weight")  # Color legend
    )

    fig.update_layout(
        title="Portfolio Weights over Months",  # Set the plot title
        # title={
        #     "text": "Portfolio Weights over Months",  # Set the plot title
        #     "x": 0.5,  # Center the title
        #     "xanchor": "center"  # Anchor the title at the center
        # },
        height=300  # Set the height of the plot
    )

    # Display in Streamlit
    st.plotly_chart(fig)

st.markdown(
    """
    [GitHub](https://github.com/taiwofasae/algo-trading-m6)
    """
)

plot_summary(['2022-11-13','2022-10-16','2022-09-18','2022-08-21','2022-07-23'])

plot_month('2022-11-13')
plot_month('2022-10-16')
plot_month('2022-09-18')
plot_month('2022-08-21')
plot_month('2022-07-23')
