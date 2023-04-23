import os
from datetime import datetime, timedelta

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from utils import Item, date_to_internal, get_limited_time, set_driver, tz


def log_in(driver):
    get_limited_time(driver, 'https://hh.ru/account/login/', 5)
    username = os.getenv('hh_email')
    password = os.getenv('hh_password')
    driver.find_element(By.XPATH, '//button[@data-qa="expand-login-by-password"]').click()
    driver.find_element(By.XPATH, '//input[@data-qa="login-input-username"]').send_keys(username)
    driver.find_element(By.XPATH, '//input[@data-qa="login-input-password"]').send_keys(password)
    driver.find_element(By.XPATH, '//button[@data-qa="account-login-submit"]').click()

def parse_data(driver, stop_date):
    i = 1
    next_page_number = 2    
    date = datetime.now(tz=tz).date() + timedelta(days=1)
    items = []
    while date >= stop_date:
        try:
            driver.find_element(By.XPATH, f'//tr[{i}]')
        except NoSuchElementException:
            pass
            try:
                driver.find_element(By.XPATH, f'//div[@class="pager"]/span[{next_page_number}]').click()
                get_limited_time(driver, f'https://hh.ru/applicant/negotiations?page={next_page_number - 1}')
                next_page_number += 1
                i = 1
            except NoSuchElementException:
                return items
        try:
            driver.find_element(By.XPATH, f'//tr[{i}]/td[3]')
        except NoSuchElementException:
            i += 1
        vacancy = driver.find_element(
            By.XPATH, f'//tr[{i}]/td[3]/button').text
        organization = driver.find_element(
            By.XPATH, f'//tr[{i}]/td[3]/div/div/span').text
        date_str = driver.find_element(
            By.XPATH, f'//tr[{i}]/td[5]/span/span').text
        date = date_to_internal(date_str, tz)
        item=Item(vacancy=vacancy, organization=organization, date=date)
        if date >= stop_date:
            items.append(item)
#            print(i, item.vacancy, item.organization, item.date)
        i += 1
    return items

def go_to_negotiations(driver):
    get_limited_time(driver, 'https://hh.ru/?hhtmFrom=account_login/', 1)
    get_limited_time(driver, 'https://hh.ru/applicant/negotiations/')

def read_from_hh(stop_date):
    driver = set_driver()
    log_in(driver)
    go_to_negotiations(driver)
    result = parse_data(driver, stop_date)
    driver.quit()
    return result
