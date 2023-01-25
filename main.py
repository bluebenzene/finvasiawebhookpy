from dotenv import load_dotenv
from flask import Flask, request, jsonify
from api_helper import ShoonyaApiPy
import os
import logging
import pyotp

# enable dbug to see request and responses
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

user = os.environ['userid']
password = os.environ['password']
twoFA = os.environ['twoFA']
twoFApin = pyotp.TOTP(twoFA).now()
vendor_code = os.environ['vendor_code']
imei = os.environ['imei']
api_secret = os.environ['api_secret']

app = Flask(__name__)


@app.route(f'/webhook/fin/{user}', methods=['POST'])
def handle_post_request():
    data = request.get_json()
    api = ShoonyaApiPy()
    cone = api.login(user, password, twoFApin, vendor_code, api_secret, imei)
    print("finvasia log:")
    print(cone)
    print("Tradingview log")
    d = data[0]
    print(d)

    # normal place order
    if d.get('simple') == 'true':
        norder = api.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'), d.get('tradingsymbol'),
                                 d.get('quantity'), 0, d.get('price_type'), float(d.get('price')), remarks="api place")
        print("finvasia log")
        print(norder)
    #

    return '200'


if __name__ == '__main__':
    print("hello")
    app.run(host='0.0.0.0', port=80)
