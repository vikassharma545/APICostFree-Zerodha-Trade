import pandas as pd
from time import sleep
from selenium import webdriver
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

    def __init__(self, user_id, password, totp=None, pin=None):
        """
        Login Account and save Credential and Download Latest Intrument for Trade
        """
        self.___user_id = user_id
        self.__password = password
        self.__totp = totp
        self.__pin = pin

        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
        driver.implicitly_wait(3)
        driver.get('https://kite.zerodha.com/')
        driver.find_element(By.XPATH, "//input[@id='userid']").send_keys(self.___user_id)
        driver.find_element(By.XPATH, "//input[@id='password']").send_keys(self.__password)
        driver.find_element(By.XPATH, "//button[normalize-space()='Login']").click()

        if self.__pin != None:
            driver.find_element(By.XPATH, "//input[@id='pin']").send_keys(self.__pin)
        else:
            driver.find_element(By.XPATH, "//input[@id='totp']").send_keys(self.__totp)

        driver.find_element(By.XPATH, "//button[normalize-space()='Continue']").click()
        sleep(1)

        # get enctoken
        raw_cookies = driver.get_cookies()
        for cookie in raw_cookies:
            if cookie['name'] == 'enctoken':
                cookies = cookie['value']
                f = open("enc_cookies.json", "w")
                f.write(cookies)
                f.close()
                break

        # Download Instruments
        data = pd.read_csv('https://api.kite.trade/instruments')
        data.to_csv('instrument_file.csv', index=False)
