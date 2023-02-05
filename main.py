import time

from dotenv import load_dotenv
# from flask import Flask, request, jsonify
from api_helper import ShoonyaApiPy
import pyotp
import threading
import os
import logging
from fastapi import FastAPI, Request, Response
import json

logging.basicConfig(level=logging.DEBUG)
import configparser

config = configparser.ConfigParser()
config.read('credentials.ini')
# cred
# import credentail init


swastikapi = ShoonyaApiPy()
first = swastikapi.login(config['swastik']['username'], config['swastik']['password'],
                         pyotp.TOTP(config['swastik']['twoFA']).now(), config['swastik']['vendor_code'],
                         config['swastik']['api_secret'], config['swastik']['imei'])
swastikwebhook = config['swastik']['username']

jayapi = ShoonyaApiPy()
sec = jayapi.login(config['jay']['username'], config['jay']['password'], pyotp.TOTP(config['jay']['twoFA']).now(),
                   config['jay']['vendor_code'], config['jay']['api_secret'], config['jay']['imei'])
jaywebhook = config['jay']['username']

# enable dbug to see request and responses


# app = Flask(__name__
app = FastAPI()


@app.post(f'/webhook/fin/{swastikwebhook}')
async def swastikhandle(request: Request):
    data = await request.json()

    print("Tradingview log")
    d = data[0]
    print(d)

    # pnl calculate multithreading function
    def swastikpnl():
        maxpnl = float(d.get("max_profit"))
        maxloss = float(d.get("max_loss"))

        while True:
            try:
                ret = swastikapi.get_positions()
                mtm = 0
                pnl = 0
                for i in ret:
                    mtm += float(i['urmtom'])
                    pnl += float(i['rpnl'])
                    day_m2m = mtm + pnl
                mtm = float(day_m2m)
                if (mtm >= maxpnl) or (mtm <= maxloss):
                    print("closing all position")
                    netpos = swastikapi.get_positions()
                    for o in netpos:
                        if int(o['netqty']) != 0:
                            transactiontype = "S" if int(o['netqty']) > 0 else "B"
                            po = swastikapi.place_order(buy_or_sell=transactiontype, product_type=o['prd'],
                                                        exchange=o['exch'], tradingsymbol=o['tsym'],
                                                        quantity=abs(int(o['netqty'])), discloseqty=0, price_type='MKT',
                                                        trigger_price=None,
                                                        retention='DAY', )
                            print("finvasia log:")
                            print(po)

                    break
            except TypeError:
                time.sleep(1)

            time.sleep(1)

    # Create a new thread and run my_function in it
    swastikthread = threading.Thread(target=swastikpnl)

    # Start the thread
    swastikthread.start()

    # 1. normal place order
    if d.get('simple') is True:
        norder = swastikapi.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
                                        d.get('tradingsymbol'),
                                        d.get('quantity'), 0, d.get('price_type'), float(d.get('price')),
                                        remarks="api place")
        print("finvasia log")
        print(norder)
    # 3.exit all position
    if d.get('exitall') is True:
        netpos = swastikapi.get_positions()
        for o in netpos:
            if int(o['netqty']) != 0:
                transactiontype = "S" if int(o['netqty']) > 0 else "B"
                eo = swastikapi.place_order(buy_or_sell=transactiontype, product_type=o['prd'],
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
        netpos = swastikapi.get_positions()
        print(netpos)
        if netpos is None:
            print("send normal")
            norder = swastikapi.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
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

                    netpos = swastikapi.get_positions()
                    print(netpos)

                    for item in netpos:
                        if item["tsym"].startswith("BANKNIFTY"):
                            bnnetqty = int(item["netqty"])
                            if int(bnnetqty) != 0:
                                transactiontype = "S" if int(bnnetqty) > 0 else "B"
                                ca = swastikapi.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
                                                            exchange=item['exch'], tradingsymbol=item['tsym'],
                                                            quantity=abs(int(bnnetqty)), discloseqty=0,
                                                            price_type='MKT',
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
                    netpos = swastikapi.get_positions()
                    print(netpos)
                    for item in netpos:
                        if item["tsym"].startswith("NIFTY"):
                            nnetqty = int(item["netqty"])
                            if int(nnetqty) != 0:
                                transactiontype = "S" if int(nnetqty) > 0 else "B"
                                cn = swastikapi.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
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
                    netpos = swastikapi.get_positions()
                    for item in netpos:
                        if item["tsym"].startswith(d.get('tradingsymbol')):
                            nnetqty = int(item["netqty"])
                            if int(nnetqty) != 0:
                                transactiontype = "S" if int(nnetqty) > 0 else "B"
                                eq = swastikapi.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
                                                            exchange=item['exch'], tradingsymbol=item['tsym'],
                                                            quantity=abs(int(nnetqty)), discloseqty=0, price_type='MKT',
                                                            trigger_price=None,
                                                            retention='DAY', )
                                print("finvasia log:")
                                print(eq)
                except Exception as e:
                    print(e)

                # place a new order
                norder = swastikapi.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
                                                d.get('tradingsymbol'),
                                                d.get('quantity'), 0, d.get('price_type'), float(d.get('price')),
                                                remarks="api place")
                print("finvasia log")
                print(norder)

    return Response(status_code=200, content={"message": "Success"})


@app.post(f'/webhook/fin/{jaywebhook}')
async def jayhandle(request: Request):
    data = await request.json()
    print("Tradingview log")
    d = data[0]
    print(d)

    # pnl calculate multithreading function
    def jaypnl():
        maxpnl = float(d.get("max_profit"))
        maxloss = float(d.get("max_loss"))

        while True:
            try:
                ret = jayapi.get_positions()
                mtm = 0
                pnl = 0
                for i in ret:
                    mtm += float(i['urmtom'])
                    pnl += float(i['rpnl'])
                    day_m2m = mtm + pnl
                mtm = float(day_m2m)
                if (mtm >= maxpnl) or (mtm <= maxloss):
                    print("closing all position")
                    netpos = jayapi.get_positions()
                    for o in netpos:
                        if int(o['netqty']) != 0:
                            transactiontype = "S" if int(o['netqty']) > 0 else "B"
                            po = jayapi.place_order(buy_or_sell=transactiontype, product_type=o['prd'],
                                                    exchange=o['exch'], tradingsymbol=o['tsym'],
                                                    quantity=abs(int(o['netqty'])), discloseqty=0, price_type='MKT',
                                                    trigger_price=None,
                                                    retention='DAY', )
                            print("finvasia log:")
                            print(po)

                    break
            except TypeError:
                time.sleep(1)

            time.sleep(1)

    # Create a new thread and run my_function in it
    jaythread = threading.Thread(target=jaypnl)

    # Start the thread
    jaythread.start()

    # 1. normal place order
    if d.get('simple') is True:
        norder = jayapi.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
                                    d.get('tradingsymbol'),
                                    d.get('quantity'), 0, d.get('price_type'), float(d.get('price')),
                                    remarks="api place")
        print("finvasia log")
        print(norder)
    # 3.exit all position
    if d.get('exitall') is True:
        netpos = jayapi.get_positions()
        for o in netpos:
            if int(o['netqty']) != 0:
                transactiontype = "S" if int(o['netqty']) > 0 else "B"
                eo = jayapi.place_order(buy_or_sell=transactiontype, product_type=o['prd'],
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
        netpos = jayapi.get_positions()
        print(netpos)
        if netpos is None:
            print("send normal")
            norder = jayapi.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
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

                    netpos = jayapi.get_positions()
                    print(netpos)

                    for item in netpos:
                        if item["tsym"].startswith("BANKNIFTY"):
                            bnnetqty = int(item["netqty"])
                            if int(bnnetqty) != 0:
                                transactiontype = "S" if int(bnnetqty) > 0 else "B"
                                ca = jayapi.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
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
                    netpos = jayapi.get_positions()
                    print(netpos)
                    for item in netpos:
                        if item["tsym"].startswith("NIFTY"):
                            nnetqty = int(item["netqty"])
                            if int(nnetqty) != 0:
                                transactiontype = "S" if int(nnetqty) > 0 else "B"
                                cn = jayapi.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
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
                    netpos = jayapi.get_positions()
                    for item in netpos:
                        if item["tsym"].startswith(d.get('tradingsymbol')):
                            nnetqty = int(item["netqty"])
                            if int(nnetqty) != 0:
                                transactiontype = "S" if int(nnetqty) > 0 else "B"
                                eq = jayapi.place_order(buy_or_sell=transactiontype, product_type=item['prd'],
                                                        exchange=item['exch'], tradingsymbol=item['tsym'],
                                                        quantity=abs(int(nnetqty)), discloseqty=0, price_type='MKT',
                                                        trigger_price=None,
                                                        retention='DAY', )
                                print("finvasia log:")
                                print(eq)
                except Exception as e:
                    print(e)

                # place a new order
                norder = jayapi.place_order(d.get('buy_or_sell'), d.get('product_type'), d.get('exchange'),
                                            d.get('tradingsymbol'),
                                            d.get('quantity'), 0, d.get('price_type'), float(d.get('price')),
                                            remarks="api place")
                print("finvasia log")
                print(norder)

    return Response(status_code=200, content={"message": "Success"})


if __name__ == '__main__':
    print("hello from fast api")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=80)
    # app.run(host='0.0.0.0', port=80)
