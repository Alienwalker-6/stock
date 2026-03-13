from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():

    stock = request.args.get("stock", "AAPL")

    df = pd.read_csv("dataset.csv")

    df["Date"] = pd.to_datetime(df["Date"])

    price = df[stock]

    # Create synthetic OHLC for candlestick
    df["Close"] = price
    df["Open"] = price.shift(1).fillna(price)
    df["High"] = price + abs(price.diff()).fillna(0)
    df["Low"] = price - abs(price.diff()).fillna(0)

    # Moving average
    df["MA20"] = price.rolling(20).mean()

    # RSI
    delta = price.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100/(1+rs))

    # Volume approximation
    volume = price.diff().abs()*100000

    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.6,0.2,0.2],
        vertical_spacing=0.02
    )

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            increasing_line_color="green",
            decreasing_line_color="red",
            name="Price"
        ),
        row=1,col=1
    )

    # Moving average
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["MA20"],
            line=dict(color="lightgreen"),
            name="MA20"
        ),
        row=1,col=1
    )

    # Volume bars
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=volume,
            marker_color="lightblue",
            name="Volume"
        ),
        row=2,col=1
    )

    # RSI
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["RSI"],
            line=dict(color="purple"),
            name="RSI"
        ),
        row=3,col=1
    )

    fig.update_layout(
        template="plotly_dark",
        title=f"{stock} Stock Analysis Dashboard",
        height=800,
        xaxis_rangeslider_visible=False
    )

    chart = fig.to_html(full_html=False)

    stocks = ["MSFT","IBM","SBUX","AAPL","GSPC"]

    return render_template("index.html", chart=chart, stocks=stocks, selected=stock)

if __name__ == "__main__":
    app.run(debug=True)