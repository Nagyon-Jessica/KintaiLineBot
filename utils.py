import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

SELENIUM_URL = os.environ.get("SELENIUM_URL")
ID_YAGAO = os.environ.get("ID_YAGAO")
PW_YAGAO = os.environ.get("PW_YAGAO")
ID_KONB = os.environ.get("ID_KONB")
PW_KONB = os.environ.get("PW_KONB")

def attend(hash):
    """
    出勤処理
    """
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    if hash['user'] == 'yagao':
        login(driver, True)
    else:
        login(driver, False)
    if hash['manual'] == 'true':
        register(driver)
    else:
        stamp(driver, True, location=hash['location'])
    driver.quit()
    return

def login(driver, is_yagao):
    """
    Salesforceにログイン
    """
    driver.get(SELENIUM_URL)
    if is_yagao:
        driver.find_element(by=By.ID, value='username').send_keys(ID_YAGAO)
        driver.find_element(by=By.ID, value='password').send_keys(PW_YAGAO)
    else:
        driver.find_element(by=By.ID, value='username').send_keys(ID_KONB)
        driver.find_element(by=By.ID, value='password').send_keys(PW_KONB)
    driver.find_element(by=By.ID, value='Login').submit()
    print("Submit!")

    # 操作可能になるまで待機
    wait = WebDriverWait(driver, 30)
    try:
        wait.until(
            EC.presence_of_element_located((By.ID, "workLocationButton1"))
        )
    except Exception as e:
        print(e)
    print("Login!")
    return

def stamp(driver, is_attend, location=None):
    """
    「ホーム」画面上で打刻

    :param bool is_attend: Trueなら出勤，Flaseなら退勤
    :param str location: 1=出社, 2=在宅勤務, 3=在宅勤務4h未満
    """
    if is_attend:
        driver.find_element(by=By.ID, value=f'workLocationButton{location}').click()
        driver.find_element(by=By.ID, value='btnStInput').click()
    return

def register(driver):
    """
    「勤務表」画面上で時刻，備考を登録
    """
    return
