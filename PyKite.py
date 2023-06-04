import os

try:
    import requests
except:
    os.system("pip install requests")

try:
    import pyotp
except:
    os.system("pip install pyotp")

try:
    import pandas as pd
except:
    os.system("pip install pandas")


def get_enctoken(userid, password, twofa, key_type):
    session = requests.session()

    # login
    data = {"user_id": userid, "password": password}
    response = session.post('https://kite.zerodha.com/api/login', data=data)
    if response.status_code != 200:
        raise Exception(response.json())

    # verify twofa
    if key_type == "totpkey":
        twofa = generate_totp(twofa)

    data = {
        "request_id": response.json()['data']['request_id'],
        "twofa_value": twofa,
        "user_id": response.json()['data']['user_id']
    }

    response = session.post('https://kite.zerodha.com/api/twofa', data=data)

    if response.status_code != 200:
        raise Exception(response.json())

    enctoken = response.cookies.get('enctoken')

    if enctoken:
        return enctoken
    else:
        raise Exception("Invalid detail. !!!")


def generate_totp(totp_key):
    return pyotp.TOTP(totp_key).now()


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

    # GTT order type
    GTT_TYPE_OCO = "two-leg"
    GTT_TYPE_SINGLE = "single"

    # GTT order status
    GTT_STATUS_ACTIVE = "active"
    GTT_STATUS_TRIGGERED = "triggered"
    GTT_STATUS_DISABLED = "disabled"
    GTT_STATUS_EXPIRED = "expired"
    GTT_STATUS_CANCELLED = "cancelled"
    GTT_STATUS_REJECTED = "rejected"
    GTT_STATUS_DELETED = "deleted"

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

    #     "portfolio.positions": "/portfolio/positions",
    #     "portfolio.holdings": "/portfolio/holdings",
    #     "portfolio.holdings.auction": "/portfolio/holdings/auctions",
    #     "portfolio.positions.convert": "/portfolio/positions",
    #
    #     # MF api endpoints
    #     "mf.orders": "/mf/orders",
    #     "mf.order.info": "/mf/orders/{order_id}",
    #     "mf.order.place": "/mf/orders",
    #     "mf.order.cancel": "/mf/orders/{order_id}",
    #
    #     "mf.sips": "/mf/sips",
    #     "mf.sip.info": "/mf/sips/{sip_id}",
    #     "mf.sip.place": "/mf/sips",
    #     "mf.sip.modify": "/mf/sips/{sip_id}",
    #     "mf.sip.cancel": "/mf/sips/{sip_id}",
    #
    #     "mf.holdings": "/mf/holdings",
    #     "mf.instruments": "/mf/instruments",
    #
    #     "market.instruments.all": "/instruments",
    #     "market.instruments": "/instruments/{exchange}",
    #     "market.margins": "/margins/{segment}",
    #     "market.historical": "/instruments/historical/{instrument_token}/{interval}",
    #     "market.trigger_range": "/instruments/trigger_range/{transaction_type}",
    #
    #     "market.quote": "/quote",
    #     "market.quote.ohlc": "/quote/ohlc",
    #     "market.quote.ltp": "/quote/ltp",
    #
    #     # GTT endpoints
    #     "gtt": "/gtt/triggers",
    #     "gtt.place": "/gtt/triggers",
    #     "gtt.info": "/gtt/triggers/{trigger_id}",
    #     "gtt.modify": "/gtt/triggers/{trigger_id}",
    #     "gtt.delete": "/gtt/triggers/{trigger_id}",
    #
    #     # Margin computation endpoints
    #     "order.margins": "/margins/orders",
    #     "order.margins.basket": "/margins/basket"
    # }

    def __init__(self, userid, password, twofa, key_type="totp"):
        """
        Initialise a new pykite client instance.

        :param userid: Kite userId
        :param password: kite password
        :param twofa: Totp/PIN/TotpKey
        :param key_type: {'totp','pin','totpkey'}, default 'totp'
        """

        self.enctoken = get_enctoken(userid, password, twofa, key_type)
        self.session = requests.session()
        self.login_url = "https://kite.zerodha.com/api"
        self.root_url = "https://api.kite.trade"
        self.header = {"Authorization": f"enctoken {self.enctoken}"}
        self.urls = self.__urls()

    def profile(self):
        response = self.session.get(f"{self.root_url}{self.urls.user_profile}", headers=self.header).json()
        return response

    def margin(self, segment=None):

        if segment:
            response = self.session.get(f"{self.root_url}{self.urls.user_margins_segment.format(segment=segment)}", headers=self.header).json()
        else:
            response = self.session.get(f"{self.root_url}{self.urls.user_margins}", headers=self.header).json()

        return response

    def instruments(self, exchange=None, download=False, download_path=""):
        instruments = pd.read_csv("https://api.kite.trade/instruments")

        if download:
            instruments.to_csv(download_path)

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

        response = self.session.get(f"{self.root_url}/quote", params={"i": ins}, headers=self.header).json()
        return response

    def ltp(self, instruments):

        ins = list(instruments)

        # If first element is a list then accept it as instruments list for legacy reason
        if len(instruments) > 0 and type(instruments[0]) == list:
            ins = instruments[0]

        response = self.session.get(f"{self.root_url}/quote/ltp", params={"i": ins}, headers=self.header).json()
        return response

    def ohlc(self, instruments):

        ins = list(instruments)

        # If first element is a list then accept it as instruments list for legacy reason
        if len(instruments) > 0 and type(instruments[0]) == list:
            ins = instruments[0]

        response = self.session.get(f"{self.root_url}/quote/ohlc", params={"i": ins}, headers=self.header).json()
        return response

    # orderbook and tradebook
    def orders(self):
        """Get list of orders."""
        response = self.session.get(f"{self.root_url}{self.urls.orders}", headers=self.header).json()
        return response

    def trades(self):
        """
        Retrieve the list of trades executed (all or ones under a particular order).

        An order can be executed in tranches based on market conditions.
        These trades are individually recorded under an order.
        """
        response = self.session.get(f"{self.root_url}{self.urls.trades}", headers=self.header).json()
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

        # orders
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
        """Place an order."""
        params = locals()
        del (params["self"])

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        return self._post("order.place",
                          url_args={"variety": variety},
                          params=params)["order_id"]
        #
        # def modify_order(self,
        #                  variety,
        #                  order_id,
        #                  parent_order_id=None,
        #                  quantity=None,
        #                  price=None,
        #                  order_type=None,
        #                  trigger_price=None,
        #                  validity=None,
        #                  disclosed_quantity=None):
        #     """Modify an open order."""
        #     params = locals()
        #     del (params["self"])
        #
        #     for k in list(params.keys()):
        #         if params[k] is None:
        #             del (params[k])
        #
        #     return self._put("order.modify",
        #                      url_args={"variety": variety, "order_id": order_id},
        #                      params=params)["order_id"]
        #
        # def cancel_order(self, variety, order_id, parent_order_id=None):
        #     """Cancel an order."""
        #     return self._delete("order.cancel",
        #                         url_args={"variety": variety, "order_id": order_id},
        #                         params={"parent_order_id": parent_order_id})["order_id"]
        #
        # def exit_order(self, variety, order_id, parent_order_id=None):
        #     """Exit a CO order."""
        #     return self.cancel_order(variety, order_id, parent_order_id=parent_order_id)
        #
        # def _format_response(self, data):
        #     """Parse and format responses."""
        #
        #     if type(data) == list:
        #         _list = data
        #     elif type(data) == dict:
        #         _list = [data]
        #
        #     for item in _list:
        #         # Convert date time string to datetime object
        #         for field in ["order_timestamp", "exchange_timestamp", "created", "last_instalment", "fill_timestamp",
        #                       "timestamp", "last_trade_time"]:
        #             if item.get(field) and len(item[field]) == 19:
        #                 item[field] = dateutil.parser.parse(item[field])
        #
        #     return _list[0] if type(data) == dict else _list



