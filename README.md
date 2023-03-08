# Broker 
## order placement and webhook for finvasia

### make a server and wait for the incoming post request from trading view and post order in broker 

let's try flask first then we implement fastapi in future 

`pip install Flask`

will also need an ASGI server, for production
`pip install uvicorn[standard]`

i will use finvasia python wrapper

`https://github.com/Shoonya-Dev/ShoonyaApi-py`

First configure the endpoints in the api_helper constructor. Thereon provide your credentials and login as follows.

```python
from api_helper import ShoonyaApiPy
import logging

#enable dbug to see request and responses
logging.basicConfig(level=logging.DEBUG)

#start of our program
api = ShoonyaApiPy()

# store credentail in .env
user        = '< user id>'
u_pwd       = '< password >'
factor2     = 'second factor'
vc          = 'vendor code'
app_key     = 'API key'
imei        = 'uniq identifier'


ret = api.login(userid=user, password=pwd, twoFA=factor2, vendor_code=vc, api_secret=app_key, imei=imei)
print(ret)
```
for placing market order.

```python
api.place_order(buy_or_sell='B', product_type='C',
                        exchange='NSE', tradingsymbol='INFY-EQ', 
                        quantity=1, discloseqty=0,price_type='MKT', price=0, trigger_price=None,
                        retention='DAY', remarks='my_order_001')
```



## below features 
### 1. normal buy/sell , nse/nfo/mcx , quantity
extract the data received from the post request . one action should be check the parameter for buy or sell ,and quantity and exchange .

```python
[
	{
                "simple": true,
		"buy_or_sell" : "B",
		"product_type" : "I",
		"exchange" : "NSE",
		"tradingsymbol"  :  "HDFCBANK-EQ",
		"quantity" : "2",
		"discloseqty" : "0",
		"price_type" : "MKT",
		"price"	:"0"
	}
]
```

### 2. close position and place a new order 
if the exchange is passed as `NFO` then if the instrument name 
starts with `BANKNIFTY25JAN23` then close all the previous position of banknifty and place new order give quantity. 
if the instrument name starts with `NIFTY25JAN23` then do the same . 
``` python
[
	{
		"buy_or_sell" : "B",
		"product_type" : "I",
		"exchange" : "NFO",
		"tradingsymbol"  :  "BANKNIFTY25JAN23C44100",
		"quantity" : "25",
		"discloseqty" : "0",
		"price_type" : "MKT",
		"price"	:"0",
		"closeprevious": true
	}
]
```
if the exchange name contains `NSE || MCX` then only close all the position starting with name instrument passed on webhook . and place a new order on given quantity and side 
``` python
[
	{
		"buy_or_sell" : "B",
		"product_type" : "I",
		"exchange" : "NSE",
		"tradingsymbol"  :  "SBIN-EQ",
		"quantity" : "5",
		"discloseqty" : "0",
		"price_type" : "MKT",
		"price"	:"0",
		"closeprevious": true
	}
]
```

### 3. close all for close all position 
if webhook contains the message then close all position
``` python
[
	{
		"exitall":true
	}
]

```
### 4. set max profit and max loss 
monitor the  `daily m2m = current mtm + pnl ` from all the position . every sec.
if it cross these value then exit the program or close the webhook url for this day.
```python
[
  {
    "max_profit":3,
    "max_loss":-1
  }
]
```

### 5. multi instrument
```python
[
	{
    "simple": true,
		"buy_or_sell" : "B",
		"product_type" : "I",
		"exchange" : "NSE",
		"tradingsymbol"  :  "IDEA-EQ",
        "secondtradingsymbol": "SBI-EQ",
		"quantity" : "1",
		"discloseqty" : "0",
		"price_type" : "MKT",
		"price"	:"0"
	}
]

```