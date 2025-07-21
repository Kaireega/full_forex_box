from flask import Flask, jsonify 
from flask_cors import CORS 
from api.oanda_api import OandaApi
from api.web_options import get_options
import http

from scraping.bloomberg_com import bloomberg_com
from scraping.forexfactory_calendar import get_monthly_data
from scraping.tradingeconomics_calendar import fx_calendar
from scraping.investing_com import get_pair

app = Flask(__name__)
CORS(app) 

def get_response(data):
    if data is None:
        return jsonify(dict(message='error getting data')), http.HTTPStatus.NOT_FOUND
    else:
        return jsonify(data)

@app.route('/')
def home():
    return jsonify(message="Welcome to the Flask app!")

@app.route("/api/test")
def test():
    return jsonify(dict(message='hello'))


@app.route("/api/headlines")
def headlines():
    return get_response(bloomberg_com())


@app.route("/api/account")
def account():
    return get_response(OandaApi().get_account_summary())


@app.route("/api/options")
def options():
    return get_response(get_options())


@app.route("/api/technicals/<pair>/<tf>")
def technicals(pair, tf):
    return get_response(get_pair(pair, tf))


@app.route("/api/prices/<pair>/<granularity>/<count>")
def prices(pair, granularity, count):
    return get_response(OandaApi().web_api_candles(pair, granularity, count))

@app.route("/api/te/calendar/<start>/<end>")
def te_calendar(start, end):
    try:
        # Get the data from fx_calendar
        data = fx_calendar(start, end)
        # Return the data as a JSON response
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/ff/calendar/<start>")
def ff_calendar(start):
    try:
        # Get the data from fx_calendar
        data = get_monthly_data(start)
        # Return the data as a JSON response
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500





if __name__ == "__main__":
    app.run(debug=True)

