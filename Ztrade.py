import os
import requests
import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class ztrade:

    # Private Variable
    ___user_id = ''
    __password = ''
    __totp = ''
    __pin = ''
    __enc_cookies = ''
    __base_url = 'https://kite.zerodha.com'

    def __init__(self, user_id, password, totp=None, pin=None):
        """
        Login Account and save Credential and Download Latest Intrument for Trade
        """
        self.___user_id = user_id
        self.__password = password
        self.__totp = totp
        self.__pin = pin

        opts = Options()
        opts.add_experimental_option("detach", True)
        os.environ['WDM_LOG'] = '0'
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=opts)
        del os.environ['WDM_LOG']
        driver.implicitly_wait(3)
        driver.maximize_window()
        driver.get(ztrade.__base_url)
        driver.find_element(By.XPATH, "//input[@id='userid']").send_keys(self.___user_id)
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys(self.__password)
        driver.find_element(By.XPATH, "//button[normalize-space()='Login']").click()

        try:
            if self.__pin != None:
                driver.find_element(By.XPATH, "//input[@id='pin']").send_keys(self.__pin)
            else:
                driver.find_element(By.XPATH, "//input[@id='totp']").send_keys(self.__totp)
        
            driver.find_element(By.XPATH, "//button[normalize-space()='Continue']").click()
            sleep(1)

            # get enctoken
            self.__enc_cookies = [ck['value'] for ck in driver.get_cookies() if ck['name'] == 'enctoken'][0]
            f = open("enc_cookies.json", "w")
            f.write(self.__enc_cookies)
            f.close()

        except:
            print('Check User ID And Password :( ')

        # Download Instruments
        data = pd.read_csv('https://api.kite.trade/instruments')
        data.to_csv('instrument_file.csv', index=False)

        print('Login Successfull Please use the broser which open :) ')
        

    class Trade:

        def Placed_order(exchange, tradingsymbol, transaction_type, order_type, quantity, product, price=0, trigger_price=0):
            """
            exchange = NSE/NFO/MCX
            tradingsymbol = NIFTY2290817500CE/HDFC/NIFTY22SEPFUT/CRUDEOIL22SEPFUT
            transaction_type = BUY/SELL
            order_type = MARKET/LIMIT/SL/SL-M
            quantity = float(number)
            price = float(number)
            product = MIS/NRML/CNC
            trigger_price = float(number)
            """

            f = open("enc_cookies.json", "r")
            cookies = f.read()
            f.close()

            headers = { 'authorization': 'enctoken ' + cookies, 'content-type': 'application/x-www-form-urlencoded' }

            data = f'variety=regular&exchange={exchange}&tradingsymbol={tradingsymbol}&transaction_type={transaction_type}&order_type={order_type}&quantity={quantity}&price={price}&product={product}&validity=DAY&disclosed_quantity=0&trigger_price={trigger_price}&squareoff=0&stoploss=0&trailing_stoploss=0&user_id=newuser&'

            return requests.post(f'{ztrade.__base_url}/oms/orders/regular', headers=headers, data=data)
                


