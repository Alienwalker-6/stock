from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

app = Flask(__name__)

@app.route("/", methods=["GET","POST"])
def index():

    trend=""
    accuracy=""
    signal=""
    chart=""
    stock=""

    if request.method=="POST":

        stock=request.form["stock"]

        df=pd.read_csv("dataset.csv")

        df["Date"]=pd.to_datetime(df["Date"])

        price=df[stock]

        # Create OHLC values
        df["Close"]=price
        df["Open"]=price.shift(1).fillna(price)
        df["High"]=price+abs(price.diff()).fillna(0)
        df["Low"]=price-abs(price.diff()).fillna(0)

        # Moving Average
        df["MA20"]=price.rolling(20).mean()

        # RSI calculation
        delta=price.diff()

        gain=delta.clip(lower=0)
        loss=-delta.clip(upper=0)

        avg_gain=gain.rolling(14).mean()
        avg_loss=loss.rolling(14).mean()

        rs=avg_gain/avg_loss

        df["RSI"]=100-(100/(1+rs))

        # Volume approximation
        volume=price.diff().abs()*100000

        # Target variable
        df["Future"]=df["Close"].shift(-1)
        df["Target"]=np.where(df["Future"]>df["Close"],1,0)

        # Remove NaN values together (FIXED PART)
        df_model=df[["Close","MA20","RSI","Target"]].dropna()

        features=df_model[["Close","MA20","RSI"]]
        target=df_model["Target"]

        # Train test split
        X_train,X_test,y_train,y_test=train_test_split(
            features,target,test_size=0.2,random_state=42
        )

        # Random Forest Model
        model=RandomForestClassifier(n_estimators=100)

        model.fit(X_train,y_train)

        y_pred=model.predict(X_test)

        accuracy=round(accuracy_score(y_test,y_pred)*100,2)

        # Predict latest trend
        latest_data=features.iloc[-1:].values
        prediction=model.predict(latest_data)

        if prediction[0]==1:
            trend="UPTREND 📈"
            signal="BUY SIGNAL 🟢"
        else:
            trend="DOWNTREND 📉"
            signal="SELL SIGNAL 🔴"

        # Plot charts
        fig=make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            row_heights=[0.6,0.2,0.2]
        )

        fig.add_trace(
            go.Candlestick(
                x=df["Date"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"]
            ),
            row=1,col=1
        )

        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df["MA20"],
                line=dict(color="green"),
                name="MA20"
            ),
            row=1,col=1
        )

        fig.add_trace(
            go.Bar(
                x=df["Date"],
                y=volume,
                name="Volume"
            ),
            row=2,col=1
        )

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
            height=800,
            title=f"{stock} Stock Dashboard"
        )

        chart=fig.to_html(full_html=False)

    return render_template(
        "index.html",
        trend=trend,
        accuracy=accuracy,
        signal=signal,
        chart=chart,
        stock=stock
    )

if __name__=="__main__":
    app.run(debug=True)