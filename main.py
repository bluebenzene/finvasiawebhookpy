import time

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from api_helper import ShoonyaApiPy
import os
import logging
import pyotp
import threading

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

api = ShoonyaApiPy()
cone = api.login(user, password, twoFApin, vendor_code, api_secret, imei)

app = Flask(__name__)


@app.route(f'/webhook/fin/{user}', methods=['POST'])
def handle_post_request():
    data = request.get_json()
    print("finvasia log:")
    print("Tradingview log")
    d = data[0]
    print(d)

    # pnl calculate multithreading function
    def pnl():
        maxpnl = float(d.get("max_profit"))
        maxloss = float(d.get("max_loss"))

        while True:
            ret = api.get_positions()
            mtm = 0
            pnl = 0
            for i in ret:
                mtm += float(i['urmtom'])
                pnl += float(i['rpnl'])
                day_m2m = mtm + pnl
            mtm = float(day_m2m)
            if (mtm >= maxpnl) or (mtm <= maxloss):
                print("closing all position")
                netpos = api.get_positions()
                for o in netpos:
                    if int(o['netqty']) != 0:
                        transactiontype = "S" if int(o['netqty']) > 0 else "B"
                        api.place_order(buy_or_sell=transactiontype, product_type=o['prd'],
                                        exchange=o['exch'], tradingsymbol=o['tsym'],
                                        quantity=abs(int(o['netqty'])), discloseqty=0, price_type='MKT',
                                        trigger_price=None,
                                        retention='DAY', )
                break
            time.sleep(1)



    # Create a new thread and run my_function in it
    thread = threading.Thread(target=pnl)

    # Start the thread
    thread.start()


    # 1. normal place order
    if d.get('simple') is True:
        norder = api.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'), d.get('tradingsymbol'),
                                 d.get('quantity'), 0, d.get('price_type'), float(d.get('price')), remarks="api place")
        print("finvasia log")
        print(norder)
    # 3.exit all position
    if d.get('exitall') is True:
        netpos = api.get_positions()
        for o in netpos:
            if int(o['netqty']) != 0:
                transactiontype = "S" if int(o['netqty']) > 0 else "B"
                api.place_order(buy_or_sell=transactiontype, product_type=o['prd'],
                                exchange=o['exch'], tradingsymbol=o['tsym'],
                                quantity=abs(int(o['netqty'])), discloseqty=0, price_type='MKT', trigger_price=None,
                                retention='DAY', )
    # 2. close same instrument and place new order , if instrument starting with banknifty then close all instrument
    # contains banknfifty if nifty then close all instrument contains nifty, if exchange is nse then close the current
    if d.get('closeprevious') is True:
        if d.get('exchange') == "NFO" and d.get('tradingsymbol').startswith("BANKNIFTY"):
            print("close all banknifty")
            #  Iterate through the position book and filter the ones that start with "BANKNIFTY" and get the netqty

            netpos = api.get_positions()
            print(netpos)
            for item in netpos:
                if item["tsym"].startswith("BANKNIFTY"):
                    bnnetqty = int(item["netqty"])
                    if int(bnnetqty) != 0:
                        transactiontype = "S" if int(bnnetqty) > 0 else "B"
                        api.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
                                        exchange=item['exch'], tradingsymbol=item['tsym'],
                                        quantity=abs(int(bnnetqty)), discloseqty=0, price_type='MKT',
                                        trigger_price=None,
                                        retention='DAY', )

        if d.get('exchange') == "NFO" and d.get('tradingsymbol').startswith("NIFTY"):
            print("close all nifty")
            #  Iterate through the position book and filter the ones that start with "BANKNIFTY" and get the netqty
            netpos = api.get_positions()
            print(netpos)
            for item in netpos:
                if item["tsym"].startswith("NIFTY"):
                    nnetqty = int(item["netqty"])
                    if int(nnetqty) != 0:
                        transactiontype = "S" if int(nnetqty) > 0 else "B"
                        api.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
                                        exchange=item['exch'], tradingsymbol=item['tsym'],
                                        quantity=abs(int(nnetqty)), discloseqty=0, price_type='MKT',
                                        trigger_price=None,
                                        retention='DAY', )

        if d.get('exchange') == "NSE" or "MCX":
            print("close all nse")
            #  Iterate through the position book and filter the ones that start with tradingsymbol and get the netqty
            netpos = api.get_positions()
            print(netpos)
            for item in netpos:
                if item["tsym"].startswith(d.get('tradingsymbol')):
                    nnetqty = int(item["netqty"])
                    if int(nnetqty) != 0:
                        transactiontype = "S" if int(nnetqty) > 0 else "B"
                        api.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
                                        exchange=item['exch'], tradingsymbol=item['tsym'],
                                        quantity=abs(int(nnetqty)), discloseqty=0, price_type='MKT',
                                        trigger_price=None,
                                        retention='DAY', )
            # place a new order
            norder = api.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
                                     d.get('tradingsymbol'),
                                     d.get('quantity'), 0, d.get('price_type'), float(d.get('price')),
                                     remarks="api place")
            print("finvasia log")
            print(norder)



    return '200'


if __name__ == '__main__':
    print("hello")
    app.run(host='0.0.0.0', port=80)
