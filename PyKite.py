import json
import pyotp
import requests
import pandas as pd

class pykite:
    """
    The Pykite wrapper class.
    In production, you may initialise a single instance of this class per `id and password`.
    """

    # Constants
    # Products
    PRODUCT_MIS = "MIS"
    PRODUCT_CNC = "CNC"
    PRODUCT_NRML = "NRML"
    PRODUCT_CO = "CO"

    # Order types
    ORDER_TYPE_MARKET = "MARKET"
    ORDER_TYPE_LIMIT = "LIMIT"
    ORDER_TYPE_SLM = "SL-M"
    ORDER_TYPE_SL = "SL"

    # Varities
    VARIETY_REGULAR = "regular"
    VARIETY_CO = "co"
    VARIETY_AMO = "amo"
    VARIETY_ICEBERG = "iceberg"
    VARIETY_AUCTION = "auction"

    # Transaction type
    TRANSACTION_TYPE_BUY = "BUY"
    TRANSACTION_TYPE_SELL = "SELL"

    # Validity
    VALIDITY_DAY = "DAY"
    VALIDITY_IOC = "IOC"
    VALIDITY_TTL = "TTL"

    # Position Type
    POSITION_TYPE_DAY = "day"
    POSITION_TYPE_OVERNIGHT = "overnight"

    # Exchanges
    EXCHANGE_NSE = "NSE"
    EXCHANGE_BSE = "BSE"
    EXCHANGE_NFO = "NFO"
    EXCHANGE_CDS = "CDS"
    EXCHANGE_BFO = "BFO"
    EXCHANGE_MCX = "MCX"
    EXCHANGE_BCD = "BCD"

    # Margins segments
    MARGIN_EQUITY = "equity"
    MARGIN_COMMODITY = "commodity"

    # Status constants
    STATUS_COMPLETE = "COMPLETE"
    STATUS_REJECTED = "REJECTED"
    STATUS_CANCELLED = "CANCELLED"

    class __urls:

        user_profile = "/user/profile"
        user_margins = "/user/margins"
        user_margins_segment = "/user/margins/{segment}"

        orders = "/orders"
        trades = "/trades"

        order_info = "/orders/{order_id}"
        order_trades = "/orders/{order_id}/trades"

        order_place = "/orders/{variety}"
        order_modify = "/orders/{variety}/{order_id}"
        order_cancel = "/orders/{variety}/{order_id}"

        portfolio_positions = "/portfolio/positions"
        portfolio_holdings = "/portfolio/holdings"
        portfolio_positions_convert = "/portfolio/positions"    # not working

        market_quote = "/quote"
        market_quote_ohlc = "/quote/ohlc"
        market_quote_ltp = "/quote/ltp"

        # Margin computation endpoints
        order_margins = "/margins/orders"
        order_margins_basket = "/margins/basket"

        # Historical data
        class interval:
            pass

        market_historical = "/instruments/historical/{instrument_token}/{interval}"

    def __init__(self, userid='', password='', twofa='', key_type="totp", enctoken=None):
        """
        Initialise a new pykite client instance.

        :param userid: Kite userId
        :param password: kite password
        :param twofa: Totp/PIN/TotpKey
        :param key_type: {'totp','pin','totpkey'}, default 'totp'

        or

        :param enctoken: you can directly pass enctoken from browser

        """

        self.session = requests.session()
        self._login_url = "https://kite.zerodha.com/api"

        if enctoken is None:

            # login
            data = {"user_id": userid, "password": password}
            response = self.session.post(f"{self._login_url}/login", data=data)
            if response.status_code != 200:
                raise Exception(response.json())

            # verify twofa
            if key_type == "totpkey":
                twofa = pyotp.TOTP(twofa).now()

            data = {
                "request_id": response.json()['data']['request_id'],
                "twofa_value": twofa,
                "user_id": response.json()['data']['user_id']
            }

            response = self.session.post(f"{self._login_url}/twofa", data=data)

            if response.status_code != 200:
                raise Exception(response.json())

            self.enctoken = response.cookies.get('enctoken')

            if self.enctoken is None:
                raise Exception("Invalid detail. !!!")

        else:
            self.enctoken = enctoken

        self.root_url = "https://api.kite.trade"
        self.header = {"Authorization": f"enctoken {self.enctoken}"}
        self.urls = self.__urls()

    def profile(self):
        """
        Get user profile details.
        """
        response = self.session.get(f"{self.root_url}{self.urls.user_profile}", headers=self.header).json()
        return response

    def margins(self, segment=None):
        """
        Get account balance and cash margin details for a particular segment.
            - `segment` is the trading segment (eg: equity or commodity)
        """

        if segment:
            response = self.session.get(f"{self.root_url}{self.urls.user_margins_segment.format(segment=segment)}", headers=self.header).json()
        else:
            response = self.session.get(f"{self.root_url}{self.urls.user_margins}", headers=self.header).json()
        return response

    # orderbook and tradebook
    def orders(self):
        """
        Get list of orders.
        """
        response = self.session.get(f"{self.root_url}{self.urls.orders}", headers=self.header).json()
        return response

    def trades(self):
        """
        Retrieve the list of trades executed (all or ones under a particular order).
        """
        response = self.session.get(f"{self.root_url}{self.urls.trades}", headers=self.header).json()
        return response

    def positions(self):
        """
        Retrieve the list of positions.
        """
        response = self.session.get(f"{self.root_url}{self.urls.portfolio_positions}", headers=self.header).json()
        return response

    def holdings(self):
        """
        Retrieve the list of equity holdings.
        """
        response = self.session.get(f"{self.root_url}{self.urls.portfolio_holdings}", headers=self.header).json()
        return response

    def order_history(self, order_id):
        """
        Get history of individual order.
        """
        response = self.session.get(f"{self.root_url}{self.urls.order_info.format(order_id=order_id)}", headers=self.header).json()
        return response

    def order_trades(self, order_id):
        """
        Retrieve the list of trades executed for a particular order.
        """
        response = self.session.get(f"{self.root_url}{self.urls.order_trades.format(order_id=order_id)}", headers=self.header).json()
        return response

    def place_order(self,
                    variety,
                    exchange,
                    tradingsymbol,
                    transaction_type,
                    quantity,
                    product,
                    order_type,
                    price=None,
                    validity=None,
                    validity_ttl=None,
                    disclosed_quantity=None,
                    trigger_price=None,
                    iceberg_legs=None,
                    iceberg_quantity=None,
                    auction_number=None,
                    tag=None):
        """
        Place an order.
        """
        params = locals()
        del (params["self"])

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        response = self.session.post(f"{self.root_url}{self.urls.order_place.format(variety = variety)}", data=params, headers=self.header).json()
        return response['message']

    def modify_order(self,
                     variety,
                     order_id,
                     parent_order_id=None,
                     quantity=None,
                     price=None,
                     order_type=None,
                     trigger_price=None,
                     validity=None,
                     disclosed_quantity=None):
        """
        Modify an open order.
        """
        params = locals()
        del (params["self"])

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        response = self.session.put(f"{self.root_url}{self.urls.order_modify.format(variety = variety, order_id=order_id)}", data=params, headers=self.header).json()
        return response['message']

    def cancel_order(self, variety, order_id, parent_order_id=None):
        """
        Cancel an order.
        """
        params = {"parent_order_id": parent_order_id}
        response = self.session.delete(f"{self.root_url}{self.urls.order_cancel.format(variety = variety, order_id=order_id)}", data=params, headers=self.header).json()
        return response['message']

    def convert_position(self,
                         exchange,
                         tradingsymbol,
                         transaction_type,
                         position_type,
                         quantity,
                         old_product,
                         new_product):
        """
        Modify an open position's product type.
        """
        params = locals()
        del (params["self"])

        """Modify an open position's product type."""
        response = self.session.put(f"{self.root_url}{self.urls.portfolio_positions_convert}", params=params, headers=self.header).json()
        return response['message']

    def instruments(self, exchange=None, download=False, download_path=""):
        """
        Fetch Instruments data
            - `exchange` is the trading exchange (eg: 'BCD', 'BFO', 'BSE', 'CDS', 'MCX', 'NSE', 'NFO')
        """
        instruments = pd.read_csv("https://api.kite.trade/instruments")

        if download:
            instruments.to_csv(download_path, index=False)

        if exchange:
            instruments = instruments[instruments['exchange'] == exchange].reset_index(drop=True)

        return instruments

    def quotes(self, instruments):
        """
        Retrieve quote for list of instruments.

        - `instruments` is a list of instruments, Instrument are in the format of `exchange:tradingsymbol`. For example NSE:INFY
        """
        ins = list(instruments)

        # If first element is a list then accept it as instruments list for legacy reason
        if len(instruments) > 0 and type(instruments[0]) == list:
            ins = instruments[0]

        response = self.session.get(f"{self.root_url}{self.urls.market_quote}", params={"i": ins}, headers=self.header).json()
        return response['data']

    def ohlc(self, instruments):
        '''
        Retrieve OHLC and market depth for list of instruments.
        '''

        ins = list(instruments)

        if len(instruments) > 0 and type(instruments[0]) == list:
            ins = instruments[0]

        response = self.session.get(f"{self.root_url}{self.urls.market_quote_ohlc}", params={"i": ins}, headers=self.header).json()
        return response['data']

    def ltp(self, instruments):
        '''
        Retrieve last price for list of instruments.
        '''

        ins = list(instruments)

        if len(instruments) > 0 and type(instruments[0]) == list:
            ins = instruments[0]

        response = self.session.get(f"{self.root_url}{self.urls.market_quote_ltp}", params={"i": ins}, headers=self.header).json()
        return response['data']

    def order_margins(self, list_of_orders):
        """
        Calculate margins for requested order list considering the existing positions and open orders

        - `params` is list of orders to retrive margins detail
        """
        response = self.session.post(f"{self.root_url}{self.urls.order_margins}", data=json.dumps(list_of_orders), headers=self.header)
        return response

    def basket_order_margins(self, list_of_orders, consider_positions=True, mode=None):
        """
        Calculate total margins required for basket of orders including margin benefits

        - `params` is list of orders to fetch basket margin
        - `consider_positions` is a boolean to consider users positions
        - `mode` is margin response mode type. compact - Compact mode will only give the total margins
        """
        params = {'consider_positions': consider_positions, 'mode': mode}
        response = self.session.post(f"{self.root_url}{self.urls.order_margins_basket}", data=json.dumps(list_of_orders), params=params, headers=self.header).json()
        return response
