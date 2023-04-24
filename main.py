# # IMPORTS
# OPERATING SYSTEM IMPORT
import os
# REQUESTS IMPORT (USED FOR CONTACTING API)
import requests
# FLASK IMPORT
from flask import Flask, render_template
# FLASK-BOOTSTRAP IMPORT
from flask_bootstrap import Bootstrap
# CURRENCY FORMATTING IMPORT
import babel.numbers
# CRYPTO GRAPH IMPORTS
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import plotly
import plotly.graph_objects as go

# INITIALIZE FLASK APPLICATION
app = Flask(__name__)
# INITIALIZE BOOTSTRAP
Bootstrap(app)

# # GLOBAL VARIABLES
# INITIALIZE ARRAY OF DESIRED CRYPTOCURRENCIES
crypto_currencies = ["BTC", "ETH", "LTC", "DOGE", "ETC"]
# INITIALIZE DICTIONARY
crypto_rates = {"BTC_USD": "",
                "BTC_EUR": "",
                "BTC_JPY": "",
                "BTC_GBP": "",
                "ETH_USD": "",
                "ETH_EUR": "",
                "ETH_JPY": "",
                "ETH_GBP": "",
                "LTC_USD": "",
                "LTC_EUR": "",
                "LTC_JPY": "",
                "LTC_GBP": "",
                "DOGE_USD": "",
                "DOGE_EUR": "",
                "DOGE_JPY": "",
                "DOGE_GBP": "",
                "ETC_USD": "",
                "ETC_EUR": "",
                "ETC_JPY": "",
                "ETC_GBP": ""
                }


# GET CRYPTO RATES
def get_crypto_rates():
    # REFERENCE GLOBAL VARIABLES
    global crypto_currencies, crypto_rates

    # FOR EACH CRYPTOCURRENCY
    for crypto in crypto_currencies:

        # # API REQUESTS
        # ENDPOINT FOR CRYPTOCURRENCY RATES
        crypto_rates_url = f'https://rest.coinapi.io/v1/exchangerate/{crypto}?invert=false'
        # COIN-API KEY
        headers = {'X-CoinAPI-Key': os.environ.get("CoinApiKey")}
        # SEND GET REQUEST TO COIN-API AND RECEIVE DATA IN JSON FORMAT
        response = requests.get(crypto_rates_url, headers=headers).json()

        # FOR EACH ENTRY IN COIN-API DATA
        for entry in response["rates"]:

            # IF CURRENCY IS USD
            if entry["asset_id_quote"] == "USD":
                # UPDATE RATE
                crypto_rates["{}_USD".format(crypto)] = entry["rate"]

            # IF CURRENCY IS EUR
            if entry["asset_id_quote"] == "EUR":
                # UPDATE RATE
                crypto_rates["{}_EUR".format(crypto)] = entry["rate"]

            # IF CURRENCY IS JPY
            if entry["asset_id_quote"] == "JPY":
                # UPDATE RATE
                crypto_rates["{}_JPY".format(crypto)] = entry["rate"]

            # IF CURRENCY IS GBP
            if entry["asset_id_quote"] == "GBP":
                # UPDATE RATE
                crypto_rates["{}_GBP".format(crypto)] = entry["rate"]

        # FORMAT CURRENCIES
        crypto_rates["{}_USD".format(crypto)] = babel.numbers.format_currency(crypto_rates["{}_USD".format(crypto)],
                                                                              'USD', locale="en_US")
        crypto_rates["{}_EUR".format(crypto)] = babel.numbers.format_currency(crypto_rates["{}_EUR".format(crypto)],
                                                                              'EUR', locale="en_US")
        crypto_rates["{}_JPY".format(crypto)] = babel.numbers.format_currency(crypto_rates["{}_JPY".format(crypto)],
                                                                              'JPY', locale="en_US")
        crypto_rates["{}_GBP".format(crypto)] = babel.numbers.format_currency(crypto_rates["{}_GBP".format(crypto)],
                                                                              'GBP', locale="en_US")

    # RETURN DESIRED CRYPTO CURRENCIES AND CRYPTO RATES
    return crypto_currencies, crypto_rates


# GET CRYPTO GRAPH
def get_crypto_graph(crypto_currencies):
    # INITIALIZE EMPTY CRYPTO DATA DICTIONARY TO HOLD YAHOO FINANCE DATA
    crypto_data = {}
    # GET CURRENT DATE AND TIME
    now = datetime.now()
    # GET CURRENT DATE
    current_date = now.strftime("%Y-%m-%d")
    # GET LAST YEARS DATE
    last_year_date = (now - timedelta(days=365)).strftime("%Y-%m-%d")
    # CONVERT LAST YEARS DATE TO PANDAS START DATE
    start = pd.to_datetime(last_year_date)
    # CONVERT CURRENT DATE TO PANDAS END DATE
    end = pd.to_datetime(current_date)
    # FOR EACH CRYPTO
    for crypto in crypto_currencies:
        # GET DESIRED CRYPTO DATA
        data = yf.download(
            tickers=f"{crypto}-USD",  # DESIRED CRYPTO
            start=start,  # START TIME IS ONE YEAR PRIOR FROM TODAY'S DATE
            end=end,  # END TIME IS TODAY'S DATE
            interval='1h',  # DATA SPLIT INTO 1HR INTERVALS
            rounding=True  # ROUND DATA VALUES
        )
        # ADD ENTRY TO DICTIONARY WHERE KEY==CRYPTO, VALUE==DATA
        crypto_data[crypto] = data
    # INITIALIZE FIGURE
    fig = go.Figure()
    # GENERATE SCATTER PLOT
    # ENUMERATE: RETURNS A TUPLE (BENEFIT? INCLUDES AN AUTO-COUNTER)
    # FIRST ITEM IN TUPLE IS INDEX/COUNTER
    # SECOND ITEM IS VALUES
    # FOR EACH CRYPTO
    for idx, name in enumerate(crypto_data):
        # ADD TRACE TO FIGURE
        fig = fig.add_trace(
            # ADDED TRACE IS OF TYPE SCATTER
            go.Scatter(
                # X-VALUE: TIME (1HR INTERVALS FOR EACH DAY FOR THE PAST YEAR)
                x=crypto_data[name].index,
                # Y-VALUE: CLOSING PRICE AT EACH INTERVAL
                y=crypto_data[name].Close,
                # NAME OF THE CURRENT CRYPTO
                name=name
            )
        )
    # CONFIGURE THE FIGURE
    fig.update_layout(
        title="Historical Data of the Above Listed Cryptocurrencies",
        title_x=0.5,  # CENTER TITLE
        xaxis_title="Date",
        yaxis_title="Price",
        legend_title="Cryptocurrencies"
    )
    # APPLY LOG SCALE TO Y-AXIS VALUES (SMOOTH CURVES)
    fig.update_yaxes(type="log", tickprefix="$")
    # GENERATE OFFLINE GRAPH TO DISPLAY INTERACTIVE GRAPH ON HTML PAGE
    crypto_graph = plotly.offline.plot(fig,
                                       config={'displayModeBar': False},
                                       show_link=False,
                                       include_plotlyjs=False,
                                       output_type='div')
    # RETURN CRYPTO GRAPH
    return crypto_graph


# HOME PAGE
@app.route("/", methods=["GET"])
def home():
    # GET CRYPTO RATES (COIN-API)
    cryptocurrencies, cryptorates = get_crypto_rates()
    # GENERATE CRYPTO GRAPH (YAHOO FINANCE API)
    crypto_graph = get_crypto_graph(cryptocurrencies)
    # RENDER HOME PAGE
    return render_template("index.html", cryptocurrencies=cryptocurrencies, cryptorates=cryptorates,
                           crypto_graph=crypto_graph)


if __name__ == "__main__":
    # RUN APPLICATION IN DEBUG MODE
    app.run(debug=True)
