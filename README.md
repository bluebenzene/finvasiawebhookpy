# webhook generate for finvasia 

## make a server and wait for the incoming post request from trading view and post order in broker 

## below features 
### 1. normal buy/sell , nse/nfo/mcx , quantity
extract the data received from the post request . one action should be check the parameter for buy or sell ,and quantity and exchange .

```[
	{
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
if the exchange is passed as `NFO` then if the instrument name starts with `BANKNIFTY` then close all the previous position of banknifty and place new order give quantity. if the instrument name starts with `NIFTY` then do the same . 
```
[
	{
		"buy_or_sell" : "B",
		"product_type" : "I",
		"exchange" : "NFO",
		"tradingsymbol"  :  "BANKNIFTY23JAN23C44100",
		"quantity" : "25",
		"discloseqty" : "0",
		"price_type" : "MKT",
		"price"	:"0",
		"closeprevious": true
	}
]
```
if the exchange name contains `NSE` then only close all the position starting with name instrument passed on webhook . and place a new order on given quantity and side 
```
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
### 3. exit all position on given instrument 
the given instrument/trading symbole passed on webhook only close these instruments if there's any previous position . do not place new order 

### 4. close all for close all position 
if webhook contains the message then close all position
```
[
	{
		"exitall":true
	}
]

```
### 5. set max profit and max loss 
monitor the daily m2m if it cross these value then exit the program or close the webhook url for this day.
```commandline
[
  {
    "max_profit":3,
    "max_loss":-1
  }
]
```