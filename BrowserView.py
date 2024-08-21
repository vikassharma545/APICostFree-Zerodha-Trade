import pyotp
from time import sleep
from selenium import webdriver
from configparser import ConfigParser
from selenium.webdriver.common.by import By

config_object = ConfigParser()
config_object.read("config.ini")
userinfo = config_object["USERINFO"]

driver = webdriver.Chrome()
driver.implicitly_wait(3)
driver.get('https://kite.zerodha.com/')
driver.find_element(By.XPATH, "//input[@id='userid']").send_keys(userinfo.get("userid"))
driver.find_element(By.XPATH, "//input[@id='password']").send_keys(userinfo.get("password"))
driver.find_element(By.XPATH, "//button[normalize-space()='Login']").click()
sleep(3)
driver.find_element(By.XPATH, "//input[@type='number']").send_keys(pyotp.TOTP(userinfo.get("totpkey")).now())
sleep(2)

enctoken = driver.get_cookie("enctoken")['value']

tokeninfo = config_object["ENCTOKEN"]
tokeninfo["enctoken"] = enctoken

#Write changes back to file
with open('config.ini', 'w') as conf:
    config_object.write(conf)

print("\nEnjoy :)")
print("!!! Dont Close the terminal !!!")
while True:
    sleep(10)
