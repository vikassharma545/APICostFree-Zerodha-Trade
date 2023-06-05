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

        portfolio_positions = "/portfolio/positions"
        portfolio_holdings = "/portfolio/holdings"
        portfolio_holdings_auction = "/portfolio/holdings/auctions"
        portfolio_positions_convert = "/portfolio/positions"

        # market_instruments_all = "/instruments"
        # market_instruments = "/instruments/{exchange}"
        # market_margins = "/margins/{segment}"
        # market_historical = "/instruments/historical/{instrument_token}/{interval}"
        # market_trigger_range = "/instruments/trigger_range/{transaction_type}"

        # market_quote = "/quote"
        # market_quote_ohlc = "/quote/ohlc"
        # market_quote_ltp = "/quote/ltp"
        #
        # # Margin computation endpoints
        # order_margins = "/margins/orders"
        # order_margins.basket = "/margins/basket"

        # GTT endpoints
        # gtt = "/gtt/triggers"
        # gtt_place = "/gtt/triggers"
        # gtt_info = "/gtt/triggers/{trigger_id}"
        # gtt_modify = "/gtt/triggers/{trigger_id}"
        # gtt_delete = "/gtt/triggers/{trigger_id}"

        # mf_orders = "/mf/orders"
        # mf_order.info = "/mf/orders/{order_id}"
        # mf_order.place = "/mf/orders"
        # mf_order.cancel = "/mf/orders/{order_id}"

        # mf_sips = "/mf/sips"
        # mf_sip.info = "/mf/sips/{sip_id}"
        # mf_sip.place = "/mf/sips"
        # mf_sip.modify = "/mf/sips/{sip_id}"
        # mf_sip.cancel = "/mf/sips/{sip_id}"

        # mf_holdings = "/mf/holdings"
        # mf_instruments = "/mf/instruments"

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

        return self.session.post(f"{self.root_url}{self.urls.order_place.format(variety = variety)}", data=params, headers=self.header)

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

        """Modify an open order."""
        params = locals()
        del (params["self"])

        for k in list(params.keys()):
            if params[k] is None:
                del (params[k])

        return self.session.post(f"{self.root_url}{self.urls.order_modify.format(variety = variety, order_id=order_id)}", data=params, headers=self.header)

    def cancel_order(self, variety, order_id, parent_order_id=None):
        """Cancel an order."""
        params = {"parent_order_id": parent_order_id}
        return self.session.post(f"{self.root_url}{self.urls.order_cancel.format(variety = variety, order_id=order_id)}", data=params, headers=self.header)

    def exit_order(self, variety, order_id, parent_order_id=None):
        """Exit a CO order."""
        return self.cancel_order(variety, order_id, parent_order_id=parent_order_id)