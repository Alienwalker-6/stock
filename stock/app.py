from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go

app = Flask(__name__)

@app.route("/")
def index():

    df = pd.read_csv("dataset.csv")

    # Convert date column
    df["Date"] = pd.to_datetime(df["Date"])

    fig = go.Figure()

    # Add each stock as a line
    fig.add_trace(go.Scatter(x=df["Date"], y=df["MSFT"], mode='lines', name="MSFT"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["IBM"], mode='lines', name="IBM"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["SBUX"], mode='lines', name="SBUX"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["AAPL"], mode='lines', name="AAPL"))
    fig.add_trace(go.Scatter(x=df["Date"], y=df["GSPC"], mode='lines', name="S&P 500"))

    fig.update_layout(
        title="Stock Market Trend Comparison",
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Stock Price"
    )

    chart = fig.to_html(full_html=False)

    return render_template("index.html", chart=chart)

if __name__ == "__main__":
    app.run(debug=True)