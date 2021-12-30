import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

SELENIUM_URL = os.environ.get("SELENIUM_URL")

def attend(hash):
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(SELENIUM_URL)
    error_text = driver.find_element(by=By.ID, value='error').text
    driver.quit()
    return error_text
