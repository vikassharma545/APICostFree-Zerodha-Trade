import os
import sys
import ctypes
import json
import pyotp
import pwinput
import pandas as pd
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

ctypes.windll.kernel32.SetConsoleTitleW('INITIALING ... ')

class ztrade:

    def __init__(self):
        """
        Login Account and save Credential and Download Latest Intrument for Trade
        """

        if not os.path.exists('login_credential.json'):
            credential = {
                "user_id":"",
                "password":"",
                "pin":"",
                "totp_key":""
            }
        else:
            credential = json.load(open('login_credential.json', 'r'))

        user_id = credential['user_id']
        password = credential['password']
        pin = credential['pin']
        totp_key = credential['totp_key']

        opts = Options()
        opts.add_experimental_option("detach", True)
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), chrome_options=opts)
        driver.implicitly_wait(2)
        driver.minimize_window()

        if not os.path.exists('login_credential.json'):
            sleep(5)
        
        for _ in range(3):

            os.system('cls')
            ctypes.windll.kernel32.SetConsoleTitleW('LOGIN ACCOUNT')
            print("    LOGIN ACCOUNT   \n")

            driver.get("https://kite.zerodha.com")

            if user_id == "":
                user_id = input('USER ID : ')
            driver.find_element(By.XPATH, "//input[@id='userid']").send_keys(user_id)

            if password == "":
                password = pwinput.pwinput(prompt='PASSWORD : ', mask='*')
            driver.find_element(By.XPATH, "//input[@id='password']").send_keys(password)

            driver.find_element(By.XPATH, "//button[normalize-space()='Login']").click()

            try:
                try:
                    pin_element = driver.find_element(By.XPATH, "//input[@id='pin']")

                    if pin == "":
                        pin = pwinput.pwinput(prompt='PIN : ', mask='X')
                    pin_element.send_keys(pin)

                except:
                    totp_element = driver.find_element(By.XPATH, "//input[@id='totp']")

                    if totp_key == "":
                        totp = input('Enter TOTP : ')
                    else:
                        totp = pyotp.TOTP(totp_key).now()

                    totp_element.send_keys(totp)
            except:
                user_id, password, pin = "", "", "", ""
                print('Wrong USER ID AND PASSWORD Try AGAIN !!!')
                sleep(3)
                continue

            driver.find_element(By.XPATH, "//button[normalize-space()='Continue']").click()
            sleep(1)

            print('Login Successfull :)')
            login_success = True
            break

        if not login_success:
            sys.exit()

        credential = {
            "user_id":user_id,
            "password":password,
            "pin":pin,
            "totp_key":totp_key
        }

        login_cred = open("login_credential.json", 'w')
        login_cred.write(json.dumps(credential))
        login_cred.close()
        
        # get enctoken
        self.__enc_cookies = driver.get_cookie('enctoken')['value']
        f = open("enc_cookies.text", "w")
        f.write(self.__enc_cookies)
        f.close()

        print('Please use the broser which open For seeing Trade :) ')
        ctypes.windll.kernel32.SetConsoleTitleW("DON'T CLOSE TERMINAL")
        
        sleep(1)
        driver.maximize_window()

        # Download Instruments
        instruments_data = pd.read_csv('https://api.kite.trade/instruments')
        instruments_data.to_csv('instrument_file.csv', index=False)

if __name__ == "__main__":
    initialize_object = ztrade()