import os, sys, ctypes
import pyotp, json
import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

class login:
    
    __base_url = 'https://kite.zerodha.com'
    
    def __init__(self, user_id=None, password=None, totp_key=None, sleep_time=3, download_instrument=True, maximize_window=True):
        """
        Login Account and save Credential and Download Latest Intrument for Trade
        """
        ctypes.windll.kernel32.SetConsoleTitleW('Login ... ')
        
        # reading login credential
        credential = eval((open('login.cred', 'r')).read())
        user_id = credential['user_id'] if not user_id else user_id
        password = credential['password'] if not password else password
        totp_key = credential['totp_key'] if not totp_key else totp_key
        
        # syntax to not close active 
        opts = Options()
        opts.add_experimental_option("detach", True)
        opts.add_experimental_option('excludeSwitches', ['enable-logging'])
        os.environ['WDM_LOG'] = '0'
        
        # login start
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=opts)
        driver.implicitly_wait(3)
        driver.get(self.__base_url)

        if user_id is not None:
            driver.find_element(By.XPATH, "//input[@id='userid']").send_keys(user_id)

        if password is not None:
            driver.find_element(By.XPATH, "//input[@id='password']").send_keys(password)

        if user_id is not None and password is not None:
            driver.find_element(By.XPATH, "//button[normalize-space()='Login']").click()

            sleep(3)
                
            if totp_key is not None:
                totp = pyotp.TOTP(totp_key).now()
                driver.find_element(By.XPATH, "//input[@type='text']").send_keys(totp)
                
        sleep(3)
        login_success = False

        for _ in range(40):
            # get enctoken
            cookies_data = pd.DataFrame(driver.get_cookies()).set_index('name')
            if 'enctoken' in cookies_data.index:
                self.__enc_cookies = cookies_data.loc['enctoken', 'value']
                with open("enc_cookies.cred", "w") as cookies_file:
                    cookies_file.write(self.__enc_cookies)
                login_success = True
                break
            sleep(5)
        
        if login_success:
            sleep(2)
            print('Please use the broser which open For seeing Trade :) ')
            ctypes.windll.kernel32.SetConsoleTitleW("DON'T CLOSE TERMINAL")
            driver.maximize_window()

        if download_instrument:
            # Download Instruments
            instruments_data = pd.read_csv('https://api.kite.trade/instruments')
            instruments_data.to_csv('instrument_file.csv', index=False)

if __name__ == "__main__":
    initialize_object = login()