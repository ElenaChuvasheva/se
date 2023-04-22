import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By

tz=timezone(timedelta(hours=3), name='Мск')

months = {
    'января': 'Январь',
    'февраля': 'Февраль',
    'марта': 'Март',
    'апреля': 'Апрель',
    'мая': 'Май',
    'июня': 'Июнь',
    'июля': 'Июль',
    'августа': 'Август',
    'сентября': 'Сентябрь',
    'октября': 'Октябрь',
    'ноября': 'Ноябрь',
    'декабря': 'Декабрь'
}

@dataclass
class Item:
    vacancy: str
    date: datetime.date
    organization: str

def date_to_internal(date_str):
    if date_str == 'вчера':        
        full_timestamp = datetime.now(tz=tz) - timedelta(days=1)
        return full_timestamp.date()
    split_date = date_str.split()
    split_date[1] = months[split_date[1]]
    changed_date = ' '.join(split_date).rstrip()
    return datetime.strptime(changed_date, '%d %B %Y').date()

def get_limited_time(driver, url, time):
    driver.set_page_load_timeout(time)
    try:
        driver.get(url)
    except TimeoutException:
        pass

def set_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options)

def log_in(driver):
    get_limited_time(driver, 'https://hh.ru/account/login/', 5)
    print('выходим со стартовой страницы')
    username = os.getenv('email')
    password = os.getenv('password')
    driver.find_element(By.XPATH, '//button[@data-qa="expand-login-by-password"]').click()
    driver.find_element(By.XPATH, '//input[@data-qa="login-input-username"]').send_keys(username)
    driver.find_element(By.XPATH, '//input[@data-qa="login-input-password"]').send_keys(password)
    driver.find_element(By.XPATH, '//button[@data-qa="account-login-submit"]').click()

def parse_data(driver, stop_date):
    i = 1
    next_page_number = 2    
    date = datetime.now(tz=tz).date() + timedelta(days=1)
    print(date)
    items = []
    while date >= stop_date:
        try:
            driver.find_element(By.XPATH, f'//tr[{i}]')
        except NoSuchElementException:
            print('следующая страница')
            try:
                driver.find_element(By.XPATH, f'//div[@class="pager"]/span[{next_page_number}]').click()
                get_limited_time(driver, f'https://hh.ru/applicant/negotiations?page={next_page_number - 1}', 10)
                next_page_number += 1
                i = 1
            except NoSuchElementException:
                print('конец')
                return items
        try:
            driver.find_element(By.XPATH, f'//tr[{i}]/td[3]')
        except NoSuchElementException:
            i += 1
        vacancy = driver.find_element(
            By.XPATH, f'//tr[{i}]/td[3]/button').text
        organization = driver.find_element(
            By.XPATH, f'//tr[{i}]/td[3]/div/div/span').text
        date = driver.find_element(
            By.XPATH, f'//tr[{i}]/td[5]/span/span').text
        date = date_to_internal(date)
        item=Item(vacancy=vacancy, organization=organization, date=date)
        if date >= stop_date:
            items.append(item)
            print(i, item.vacancy, item.organization, item.date)
        i += 1
    return items

def go_to_negotiations(driver):
    get_limited_time(driver, 'https://hh.ru/?hhtmFrom=account_login/', 1)
    print('выходим с промежуточной страницы')
    get_limited_time(driver, 'https://hh.ru/applicant/negotiations/', 10)

def read_from_hh(stop_date):
    driver = set_driver()
    log_in(driver)
    go_to_negotiations(driver)
    result = parse_data(driver, stop_date)
    driver.quit()
    return result
