import time

from flask import Flask, request, jsonify
from api_helper import ShoonyaApiPy
import pyotp
import threading
import logging
import configparser

logging.basicConfig(level=logging.DEBUG)

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('credentials.ini')


# enable dbug to see request and responses


# cone = api.login(user, password, twoFApin, vendor_code, api_secret, imei)

def login():
    global api
    global user
    api = ShoonyaApiPy()
    user = config['jay']['username']
    password = config['jay']['password']
    twoFA = config['jay']['twoFA']
    twoFApin = pyotp.TOTP(twoFA).now()
    vendor_code = config['jay']['vendor_code']
    imei = config['jay']['imei']
    api_secret = config['jay']['api_secret']
    ret = api.login(user, password, twoFApin, vendor_code, api_secret, imei)
    print("login successfull")
    print(ret)

def relogin():
    while True:
        login()
        time.sleep(12 * 60 * 60)


login_thread = threading.Thread(target=relogin)
login_thread.start()

app = Flask(__name__)


@app.route(f'/webhook/fin/{user}', methods=['POST'])
def handle_post_request():
    data = request.get_json()
    print("Tradingview log")
    d = data[0]
    print(d)

    # pnl calculate multithreading function
    def pnl():
        maxpnl = float(d.get("max_profit"))
        maxloss = float(d.get("max_loss"))

        while True:
            try:
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
                            po = api.place_order(buy_or_sell=transactiontype, product_type=o['prd'],
                                                 exchange=o['exch'], tradingsymbol=o['tsym'],
                                                 quantity=abs(int(o['netqty'])), discloseqty=0, price_type='MKT',
                                                 trigger_price=None,
                                                 retention='DAY', )
                            print("finvasia log:")
                            print(po)

                    break
            except TypeError:
                time.sleep(1)

            time.sleep(2)

    # Create a new thread and run my_function in it
    pnl_thread = threading.Thread(target=pnl)

    # Start the thread
    pnl_thread.start()

    # 1. normal place order
    if d.get('simple') is True:
        norder = api.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'), d.get('tradingsymbol'),
                                 d.get('quantity'), 0, d.get('price_type'), float(d.get('price')), remarks="api place")
        print("finvasia log")
        print(norder)

    if d.get('second') is True:
        norder = api.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'), d.get('tradingsymbol'),
                                 d.get('quantity'), 0, d.get('price_type'), float(d.get('price')), remarks="api place")
        nordertwo = api.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
                                    d.get('secondtradingsymbol'),
                                    d.get('quantity'), 0, d.get('price_type'), float(d.get('price')),
                                    remarks="api place")
        print("finvasia log")
        print(norder)
        print(nordertwo)
    # 3.exit all position
    if d.get('exitall') is True:
        netpos = api.get_positions()
        for o in netpos:
            if int(o['netqty']) != 0:
                transactiontype = "S" if int(o['netqty']) > 0 else "B"
                eo = api.place_order(buy_or_sell=transactiontype, product_type=o['prd'],
                                     exchange=o['exch'], tradingsymbol=o['tsym'],
                                     quantity=abs(int(o['netqty'])), discloseqty=0, price_type='MKT',
                                     trigger_price=None,
                                     retention='DAY', )
                print("finvasia log:")
                print(eo)
    # 2. close same instrument and place new order , if instrument starting with banknifty then close all instrument
    # contains banknfifty if nifty then close all instrument contains nifty, if exchange is nse then close the current
    # if close true , then check position book, of it return none, then place a order
    if d.get('closeprevious') is True:
        netpos = api.get_positions()
        print(netpos)
        if netpos is None:
            print("send normal")
            norder = api.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
                                     d.get('tradingsymbol'),
                                     d.get('quantity'), 0, d.get('price_type'), float(d.get('price')),
                                     remarks="api place")
            print("finvasia log")
            print(norder)
        else:
            if d.get('exchange') == "NFO" and d.get('tradingsymbol').startswith("BANKNIFTY"):
                print("close all banknifty")
                #  Iterate through the position book and filter the ones that start with "BANKNIFTY" and get the netqty
                try:

                    netpos = api.get_positions()
                    print(netpos)

                    for item in netpos:
                        if item["tsym"].startswith("BANKNIFTY"):
                            bnnetqty = int(item["netqty"])
                            if int(bnnetqty) != 0:
                                transactiontype = "S" if int(bnnetqty) > 0 else "B"
                                ca = api.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
                                                     exchange=item['exch'], tradingsymbol=item['tsym'],
                                                     quantity=abs(int(bnnetqty)), discloseqty=0, price_type='MKT',
                                                     trigger_price=None,
                                                     retention='DAY', )
                                print("finvasia log:")
                                print(ca)
                except Exception as e:
                    print(e)
            if d.get('exchange') == "NFO" and d.get('tradingsymbol').startswith("NIFTY"):
                print("close all nifty")
                #  Iterate through the position book and filter the ones that start with "BANKNIFTY" and get the netqty
                try:
                    netpos = api.get_positions()
                    print(netpos)
                    for item in netpos:
                        if item["tsym"].startswith("NIFTY"):
                            nnetqty = int(item["netqty"])
                            if int(nnetqty) != 0:
                                transactiontype = "S" if int(nnetqty) > 0 else "B"
                                cn = api.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
                                                     exchange=item['exch'], tradingsymbol=item['tsym'],
                                                     quantity=abs(int(nnetqty)), discloseqty=0, price_type='MKT',
                                                     trigger_price=None,
                                                     retention='DAY', )
                                print("finvasia log:")
                                print(cn)
                except Exception as e:
                    print(e)

            if d.get('exchange') == "NSE" or "MCX":
                #  Iterate through the position book and filter the ones that start with tradingsymbol and get the netqty
                try:
                    netpos = api.get_positions()
                    for item in netpos:
                        if item["tsym"].startswith(d.get('tradingsymbol')):
                            nnetqty = int(item["netqty"])
                            if int(nnetqty) != 0:
                                transactiontype = "S" if int(nnetqty) > 0 else "B"
                                eq = api.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
                                                     exchange=item['exch'], tradingsymbol=item['tsym'],
                                                     quantity=abs(int(nnetqty)), discloseqty=0, price_type='MKT',
                                                     trigger_price=None,
                                                     retention='DAY', )
                                print("finvasia log:")
                                print(eq)
                except Exception as e:
                    print(e)

                # place a new order
                norder = api.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
                                         d.get('tradingsymbol'),
                                         d.get('quantity'), 0, d.get('price_type'), float(d.get('price')),
                                         remarks="api place")
                print("finvasia log")
                print(norder)

    return '200'


if __name__ == '__main__':

    print("Starting Flask app...")
    try:
        app.run(host='0.0.0.0', port=80)
    except Exception as e:
        print("Error occurred during Flask app startup:", e)
