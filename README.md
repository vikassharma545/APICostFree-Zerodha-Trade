# APICostFree Zerodha Trade
### _An unofficial python library for zerodha trade_

## Prerequisites
* Python >= 3.7

## Requirments
* requests >= 2.28.1  ``` pip install requests```
* pyotp >= 2.8.0      ```pip install pyotp```
* pandas >= 1.5.0     ```pip install pandas```

How to use
```python
from PyKite import pykite
```

Login Method - 1
```python

# using Userid password and totp/pin/totpkey
# condition not use zerodha on browser

kite = pykite(userid="userid", password="password", twofa="twofa", key_type="totp")
```

Login Method - 2
```python
# login directly using entoken copy from browser after login zerodha 
# condition not use zerodha web on different pc
# after login don't logout from current session

enctoken = "E0zW+0684kAxZJPbSSIRv1lKIIqM8Iyw2tQ5WVxwg/oDbmclZrakC/poFPpg=="

kite = pykite(enctoken=enctoken)
```

### Notes - You can use zerodha on kite App Mobile 

## Usages


### Accounts and trades details
```python
# Get user profile details.
print(kite.profile())

# Get account balance and cash margin.
print(kite.margins())

# Fetch all orders
print(kite.orders())

# Fetch all trades
print(kite.trades())

# Fetch all position
print(kite.positions())

# Get order history for particular order
print(kite.order_history('order_id'))

# Get trades history particular order
print(kite.order_trades('order_id'))
```

### Order placing and modify
```python
# Place an order
print(kite.place_order(variety=kite.VARIETY_REGULAR, 
                       exchange=kite.EXCHANGE_NSE, 
                       tradingsymbol="SBIN", 
                       transaction_type=kite.TRANSACTION_TYPE_BUY, 
                       quantity=10, 
                       product=kite.PRODUCT_CNC, 
                       order_type=kite.ORDER_TYPE_LIMIT, 
                       price=500))


# Modify an order
print(kite.modify_order(variety=kite.VARIETY_REGULAR, 
                        order_id='order_id', 
                        quantity="10", 
                        price=550, 
                        order_type=kite.ORDER_TYPE_LIMIT))

# Cancel an order
print(kite.cancel_order(variety=kite.VARIETY_REGULAR, 
                        order_id='order_id', 
                        parent_order_id='parent_order_id'))


# Convert position
print(kite.convert_position(exchange=kite.EXCHANGE_NSE,
                            tradingsymbol="SBIN",
                            transaction_type=kite.TRANSACTION_TYPE_BUY,
                            position_type=kite.POSITION_TYPE_DAY,
                            quantity=10,
                            old_product=kite.PRODUCT_CNC,
                            new_product=kite.PRODUCT_NRML))

```

### Calculate margin required of orders

```python
list_of_order = [{'exchange': 'NFO',
                  'tradingsymbol': 'BANKNIFTY2361544000CE',
                  'transaction_type': 'SELL',
                  'variety': 'regular',
                  'product': 'MIS',
                  'order_type': 'MARKET',
                  'quantity': 25,
                  'price': 0,
                  'trigger_price': 0,
                  'squareoff': 0,
                  'stoploss': 0},
                 {'exchange': 'NFO',
                  'tradingsymbol': 'BANKNIFTY2361544000PE',
                  'transaction_type': 'SELL',
                  'variety': 'regular',
                  'product': 'MIS',
                  'order_type': 'MARKET',
                  'quantity': 25,
                  'price': 0,
                  'trigger_price': 0,
                  'squareoff': 0,
                  'stoploss': 0}]

# Calculate margins considering the existing positions and open orders
print(kite.order_margins(list_of_order).json()['data'])

# Calculate total margins required including margin benefits
print(kite.basket_order_margins(list_of_order).json()['data'])
```
### Market Quotes

```python
instrument_list = ["NSE:SBIN", "NSE:HDFC", "NSE:RELIANCE"]

# Retrieve quote for list of instruments.
print(kite.quotes(instrument_list))

# Retrieve OHLC for list of instruments for current day.
print(kite.ohlc(instrument_list))

# Retrieve Last trade price for list of instruments.
print(kite.ltp(instrument_list))
```

### Instruments data

```python
# fetch all instruments
instrument_all = kite.instruments()
print(instrument_all)

# Fetch instrument for particular exchange
instrument_nse = kite.instruments("NSE")
print(instrument_nse)


# fetch and download instrument file to disk
instrument_nfo = kite.instruments("NFO", download=True, download_path="./instrument_nfo.csv")
print(instrument_nfo)
```

### Historical data

```python
instrument_nse = kite.instruments("NSE")
sbin_instrument_token = instrument_nse[instrument_nse['tradingsymbol']=="SBIN"]['instrument_token'].iloc[0]

json_data = kite.historical_data(sbin_instrument_token, 
                                 from_date="2021-01-01 00:00:00", 
                                 to_date="2023-01-01 00:00:00", 
                                 interval='day')

print(json_data['data']['candles'])
```
