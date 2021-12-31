import os
from datetime import date

from linebot import LineBotApi
from linebot.models import TextSendMessage
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from templates import CHECKOUT_TEMPLATE

HOME_URL = os.environ.get("HOME_URL")
AWTVIEW_URL = os.environ.get("AWTVIEW_URL")
ID_YAGAO = os.environ.get("ID_YAGAO")
PW_YAGAO = os.environ.get("PW_YAGAO")
ID_KONB = os.environ.get("ID_KONB")
PW_KONB = os.environ.get("PW_KONB")

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
ALLOWED_USERS = os.environ['ALLOWED_USER'].split(';')

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

# 今日の日付を取得
today = date.today()

def attend(hash):
    """
    出勤処理
    """
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    user_id = hash['user_id']
    if hash['manual'] == 'true':
        driver.get(AWTVIEW_URL)
        login(driver, user_id)
        register(driver, True, hash['time'], hash['location'])
    else:
        driver.get(HOME_URL)
        login(driver, user_id)
        stamp(driver, True, hash['location'])
    driver.quit()
    line_bot_api.push_message(
        to=user_id,
        messages=[CHECKOUT_TEMPLATE])
    return

def checkout(hash):
    """
    退勤処理
    """
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    user_id = hash['user_id']
    if 'note' in hash:
        driver.get(AWTVIEW_URL)
        login(driver, user_id)
        register(driver, False, hash['time'], note=hash['note'])
    else:
        if hash['manual'] == 'true':
            driver.get(AWTVIEW_URL)
            login(driver, user_id)
            register(driver, False, hash['time'])
        else:
            driver.get(HOME_URL)
            login(driver, user_id)
            stamp(driver, False)
    driver.quit()
    message = TextSendMessage(text='打刻が完了しました！\nお疲れさまでした！')
    line_bot_api.push_message(
        to=user_id,
        messages=[message])
    return

def login(driver, user_id):
    """
    Salesforceにログイン
    """
    if "U9" in user_id:
        driver.find_element(by=By.ID, value='username').send_keys(ID_YAGAO)
        driver.find_element(by=By.ID, value='password').send_keys(PW_YAGAO)
    else:
        driver.find_element(by=By.ID, value='username').send_keys(ID_KONB)
        driver.find_element(by=By.ID, value='password').send_keys(PW_KONB)
    driver.find_element(by=By.ID, value='Login').submit()
    print("Submit!")
    return

def stamp(driver, is_attend, location=None):
    """
    「ホーム」画面上で打刻

    :param bool is_attend: Trueなら出勤，Flaseなら退勤
    :param str location: 1=出社, 2=在宅勤務, 3=在宅勤務4h未満
    """
    # iframeが表示されるまで待機
    wait = WebDriverWait(driver, 30)
    wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
    )
    iframe = driver.find_element(by=By.TAG_NAME, value='iframe')
    driver.switch_to.frame(iframe)

    if is_attend:
        wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//label[@for='workLocationButton{location}']"))
        )
        driver.find_element(by=By.XPATH, value=f"//label[@for='workLocationButton{location}']").click()
        wait.until(
            EC.element_to_be_clickable((By.ID, "btnStInput"))
        )
        driver.find_element(by=By.ID, value='btnStInput').click()
    else:
        wait.until(
            EC.element_to_be_clickable((By.ID, "btnEtInput"))
        )
        driver.find_element(by=By.ID, value='btnEtInput').click()

    return

def register(driver, is_attend, time, location=None, note=None):
    """
    「勤務表」画面上で時刻，備考を登録

    :param bool is_attend: Trueなら出勤，Flaseなら退勤
    :param str time: 出退勤時刻
    :param str location: 1=出社, 2=在宅勤務, 3=在宅勤務4h未満
    :param str note: 備考
    """
    # クリックできるように成るまで待機
    wait = WebDriverWait(driver, 30)
    wait.until(
        EC.element_to_be_clickable((By.ID, f"ttvTimeSt{today}"))
    )

    # 該当日のtr要素を取得
    today_row = driver.find_element(by=By.ID, value=f"dateRow{today}")
    driver.find_element(by=By.ID, value=f"ttvTimeSt{today}").click()

    # モーダルが表示されるまで待機
    wait = WebDriverWait(driver, 30)
    wait.until(
        EC.presence_of_element_located((By.ID, "dialogInputTime"))
    )

    if is_attend:
        input_id = 'startTime'
    else:
        input_id = 'endTime'

    # 出退勤時刻を入力
    driver.find_element(by=By.ID, value=input_id).send_keys(time)

    if is_attend:
        # 勤務地を選択
        select_element = driver.find_element(by=By.ID, value='workLocationId')
        Select(select_element).select_by_index(int(location))

    # 「登録」ボタン押下
    driver.find_element(by=By.ID, value="dlgInpTimeOk").click()

    # 退勤かつ備考がある時，備考を入力
    if not is_attend and note:
        # 退勤時刻登録のロードが終わるまで待機
        wait.until(
            EC.invisibility_of_element_located((By.ID, "BusyWait_underlay"))
        )
        driver.find_element(by=By.ID, value=f"dailyNoteIcon{today}").click()
        wait.until(
            EC.presence_of_element_located((By.ID, "dialogNoteText2"))
        )
        driver.find_element(by=By.ID, value='dialogNoteText2').send_keys(note)

        # 「登録」ボタン押下
        driver.find_element(by=By.ID, value="dialogNoteOk").click()
    return
