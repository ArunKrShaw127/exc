from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from datetime import datetime
import requests
import threading
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)

# Get the absolute path of the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Set the template folder path based on the current system
template_folder = os.path.join(current_dir, 'templates')
app.template_folder = template_folder

@app.route('/')
def index():
    return render_template('index.html')

def fetch_exchange_data():
    pairs = [
        "ADAUSDT",
        "PAXGINR",
        "SCRTUSDT",
        "ETCUSDT",
        "DEGOUSDT",
        "CTSIUSDT",
        "ACHUSDT",
        "ADABTC",
        "SANDINR",
        "ALCXUSDT",
        "LEVERUSDT",
        "KNCUSDT",
        "NKNUSDT",
        "OPUSDT",
        "HIGHUSDT",
        "MDXUSDT",
        "SUSHIINR",
        "XNOUSDT",
        "MBOXINR",
        "DASHINR",
        "CELRINR",
        "BICOINR",
        "CITYUSDT",
        "OGNINR",
        "QUICKINR",
        "CKBINR",
        "DARUSDT",
        "REQUSDT",
        "ENJINR",
        "BURGERUSDT",
        "DASHUSDT",
        "AXSINR",
        "ATOMINR",
        "FETUSDT",
        "THETAUSDT",
        "RUNEINR",
        "COMPUSDT",
        "DUSKUSDT",
        "QNTUSDT",
        "1INCHINR",
        "BTCINR",
        "USDTINR",
        "ETHINR",
        "SHIBINR",
        "BTCUSDT",
        "ETHUSDT",
        "SHIBUSDT",
        "ETHBTC",
        "LTCUSDT",
        "LTCINR",
        "LTCBTC",
        "XRPUSDT",
        "XRPINR",
        "XRPBTC",
        "BCHUSDT",
        "BCHINR",
        "BCHBTC",
        "LINKUSDT",
        "LINKINR",
        "LINKBTC",

        "BCHBTC",
        "BCHINR",
        "BCHUSDT",

        "TRXUSDT",
        "TRXINR",
        "TRXBTC",

        "DOGEUSDT",
        "DOGEINR",
        "DOGEBTC",

        "EOSUSDT",
        "EOSINR",
        "EOSBTC",

        "UNIUSDT",
        "UNIBTC",
        "UNIINR",

        "TRXBTC",
        "TRXINR",
        "TRXUSDT",

        "EOSBTC",
        "EOSINR",
        "EOSUSDT",

        "LINKBTC",
        "LINKINR",
        "LINKUSDT",

        "XLMUSDT",
        "XLMINR",
        "XLMBTC",
        "DOGEBTC"
    ]

    exchanges = [
        {"name": "CoinDCX", "url": "https://api.coindcx.com/exchange/ticker"},
        {"name": "Giottus", "url": "https://www.giottus.com/api/v2/ticker"},
        {"name": "WazirX", "url": "https://api.wazirx.com/sapi/v1/tickers/24hr"},
        {"name": "Unocoin", "url": "https://api.unocoin.com/api/v1/exchange/tickers"}
    ]

    while True:
        exchange_data = []
        for exchange in exchanges:
            response = requests.get(exchange["url"])
            data = response.json()

            for pair in pairs:
                if exchange["name"] == "CoinDCX":
                    usdt_inr_data = next((item for item in data if item["market"].lower() == pair.lower()), None)
                    if usdt_inr_data:
                        value = usdt_inr_data["last_price"]
                        timestamp = usdt_inr_data["timestamp"]
                        exchange_data.append({
                            'pair': pair,
                            'exchange_name': exchange["name"],
                            'value': str(value),
                            'timestamp': str(datetime.fromtimestamp(timestamp))
                        })
                elif exchange["name"] == "Giottus":
                    pair_key = pair.lower()
                    if pair_key in data:
                        pair_data = data[pair_key]
                        value = pair_data["last"]
                        timestamp = pair_data["at"]
                        exchange_data.append({
                            'pair': pair,
                            'exchange_name': exchange["name"],
                            'value': str(value),
                            'timestamp': str(datetime.fromtimestamp(timestamp))
                        })
                elif exchange["name"] == "WazirX":
                    usdt_inr_data = next((item for item in data if item["symbol"].lower() == pair.lower()), None)
                    if usdt_inr_data:
                        value = usdt_inr_data["lastPrice"]
                        timestamp = usdt_inr_data["at"] / 1000  # Convert milliseconds to seconds
                        exchange_data.append({
                            'pair': pair,
                            'exchange_name': exchange["name"],
                            'value': str(value),
                            'timestamp': str(datetime.fromtimestamp(timestamp))
                        })
                elif exchange["name"] == 'Unocoin':
                    for item in data:
                        item["ticker_id"] = item["ticker_id"].replace("_", "")

                    usdt_inr_data = next((item for item in data if item["ticker_id"] == pair), None)
                    if usdt_inr_data:
                        value = usdt_inr_data["last_price"]
                        timestamp = int(datetime.now().timestamp())  # Convert to integer EPOCH Time
                        exchange_data.append({
                            'pair': pair,
                            'exchange_name': exchange["name"],
                            'value': str(value),
                            'timestamp': str(datetime.fromtimestamp(timestamp))
                        })

        socketio.emit('exchange_data', {'current_data': exchange_data}, namespace='/current_data')
        socketio.sleep(0)

@socketio.on('connect', namespace='/current_data')
def on_connect():
    thread = threading.Thread(target=fetch_exchange_data)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5005)
