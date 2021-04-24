import os
import re
import objects
from time import sleep
from GDrive import Drive
from chrome import chrome
from datetime import datetime
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
# ==================================================================================================================


def db_creation():
    data = {}
    folder_id = None
    client = Drive(json_path)
    for folder in client.files(only_folders=True):
        if folder['name'] == os.environ.get('folder'):
            folder_id = folder['id']

    for file in client.files(parents=folder_id):
        data[re.sub(r'\.png', '', file['name'])] = file['id']
    return data, client


origin_files = os.listdir()
json_path = 'geocoding2.json'
objects.environmental_files()
db, drive_client = db_creation()
# ==================================================================================================================


def new_file():
    filename = max([f if os.path.isdir(f) is False else 0 for f in os.listdir()], key=os.path.getctime)
    if filename not in origin_files:
        return filename
    else:
        return None


def drive_updater(file_id, file_path):
    global drive_client
    try:
        drive_client.update_file(file_id, file_path)
    except IndexError and Exception:
        drive_client = Drive(json_path)
        drive_client.update_file(file_id, file_path)


def updater(driver, name):
    currency = name.split('_')[0]
    period = int(name.split('_')[1])
    driver.get(f"{os.environ.get('link')}={currency}")
    WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.CLASS_NAME, 'swap-long-short-trend-chart')))
    elements = driver.find_elements(By.CLASS_NAME, 'swap-long-short-trend-chart  ')
    if len(elements) == 2:
        ActionChains(driver).move_to_element(elements[1].find_element(By.TAG_NAME, 'canvas')).perform()
        if period == 60:
            div = elements[1].find_element(By.CLASS_NAME, 'select-white')
            div.click()
            sleep(2)

            for li in div.find_elements(By.TAG_NAME, 'li'):
                if li.text == '1H':
                    ActionChains(driver).move_to_element(li).click().perform()
                    break
        else:
            sleep(3)

        element = elements[1].find_element(By.TAG_NAME, 'canvas')
        ActionChains(driver).move_to_element_with_offset(element, 315, 35).click().perform()
        WebDriverWait(driver, 20).until(ec.presence_of_element_located(
            (By.CLASS_NAME, 'chart-share-modal-content-footer-download')))
        sleep(3)
        driver.find_element(By.CLASS_NAME, 'chart-share-modal-content-footer-download').click()
        sleep(5)
        downloaded = new_file()
        if downloaded:
            drive_updater(db[name], downloaded)
            os.remove(downloaded)
    driver.get('https://google.com')


def start(stamp):
    if os.environ.get('local') is None:
        print(f'Запуск на сервере за {objects.time_now() - stamp}')
    while True:
        chrome_client = chrome(os.environ.get('local'))
        stamp = datetime.now().timestamp()
        for key in db:
            updater(chrome_client, key)
        print(f'Проход всех за {datetime.now().timestamp() - stamp}')
        chrome_client.close()


if os.environ.get('local'):
    start(objects.time_now())
