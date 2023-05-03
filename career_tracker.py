import os
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from utils import (get_limited_time, item_str_format, months, set_driver,
                   str_format)


def log_in_tracker(driver):
    get_limited_time(driver, 'https://career.praktikum-services.ru/sign-in/')
    username = os.getenv('tracker_email')
    password = os.getenv('tracker_password')
    driver.find_element(By.XPATH, '//input[@name="email"]').send_keys(username)
    driver.find_element(By.XPATH, '//input[@name="password"]').send_keys(password)
    driver.find_element(By.XPATH, '//form/fieldset/button').click()
    time.sleep(5)

def get_old_items_set(driver):
    get_limited_time(driver, 'https://career.praktikum-services.ru/diary/', 5)
    time.sleep(5)
    result = set()
    i = 1
    while True:
        try:
            organization = driver.find_element(By.XPATH, f'//div[@data-rbd-droppable-id="response"]/div[{i}]/div/div/div/p[1]').text
            vacancy = driver.find_element(By.XPATH, f'//div[@data-rbd-droppable-id="response"]/div[{i}]/div/div/div/p[2]').text
            date = driver.find_element(By.XPATH, f'//div[@data-rbd-droppable-id="response"]/div[{i}]/div/div[2]').text
            result.add(str_format(vacancy, organization))
            i += 1
        except NoSuchElementException:
            return result

def clean_data(old_results_set, items_list):
    items_to_tracker = []
    items_not_to_tracker = []
    for item in items_list:
        if item_str_format(item) in old_results_set:
            items_not_to_tracker.append(item)
        else:
            items_to_tracker.append(item)
    return {'items_to_tracker': items_to_tracker,
            'items_not_to_tracker': items_not_to_tracker}

def answer_question(data):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    print('Можем выложить в трекер следующие вакансии:\n')
    for item in data['items_to_tracker']:
        item.print()
    print('\n\nА с этими придётся разбираться самостоятельно:\n')
    for item in data['items_not_to_tracker']:
        item.print()
    print('\nВыкладываем? y/n')
    answer = input()
    if answer.lower() == 'y':
        return True
    return False

def set_date(driver, item, text):
    driver.find_element(By.XPATH, f'//div[./p[text()="{text}"]]/div/div/input').click()
    current_month_year = driver.find_element(By.XPATH, '//div[@role="none presentation"]/div/div[1]/div/div/div[1]/div[1]/div/p').text
    counter = 0
    while months[current_month_year.split()[0]] != item.date.strftime('%B'):
        driver.find_element(By.XPATH, '//div[@role="none presentation"]/div/div[1]/div/div/div[1]/div[1]/button').click()
        current_month_year = driver.find_element(By.XPATH, '//div[@role="none presentation"]/div/div[1]/div/div/div[1]/div[1]/div/p').text
        counter += 1
        if counter > 20:
            raise Exception('проблемы с датой')
    week_day = item.date.isocalendar().weekday
    x = item.date.day % 7
    if x <= week_day:
        week_number = item.date.day // 7 + 1
    else:
        week_number = item.date.day // 7 + 2
    time.sleep(1)
    driver.find_element(By.XPATH, f'//div[@role="none presentation"]/div/div[1]/div/div/div[2]/div/div[{week_number}]/div[{week_day}]/button').click()
    driver.find_element(By.XPATH, f'//div[@role="none presentation"]/div/div[2]/button[./span[text()="Сохранить"]]').click()

def vacancy_to_tracker(driver, item):
    driver.find_element(By.XPATH, '//button[./span/div/p[text()="Добавить новый отклик"]]').click()
    driver.find_element(By.XPATH, '//div[./p[text()="Источник вакансии"]]/div/div/div[@role="button"]').click()
    driver.find_element(By.XPATH, '//li[./span[text()="hh"]]').click()
    driver.find_element(By.NAME, 'company_name').send_keys(item.organization)
    driver.find_element(By.NAME, 'position').send_keys(item.vacancy)

    set_date(driver, item, 'Отклик на вакансию')
    if item.rejected:
        set_date(driver, item, 'Отказ')
        
    driver.find_element(By.XPATH, f'//div[@role="dialog"]/div[@variant="response"]//button[@type="submit"]').click()
    time.sleep(1)    

def vacancies_to_tracker(driver, items):
    for item in items:
        vacancy_to_tracker(driver, item)

def tracker(items_list):
    driver = set_driver()
    log_in_tracker(driver)
    old_results_set = get_old_items_set(driver)
    data = clean_data(old_results_set, items_list)
    to_tracker = answer_question(data)
#    test_items = [Item(vacancy='Тестовая вакансия', organization='Тестовая организация', date=datetime(day=14, month=4, year=2023).date()),
#                  Item(vacancy='Тестовая вакансия 2', organization='Тестовая организация 2', date=datetime(day=17, month=4, year=2023).date())]
    if to_tracker:
        vacancies_to_tracker(driver, data['items_to_tracker'])
        print('Вакансии какие можно выложены, а эти есть в базе, обрабатывай сам:\n')
        for item in data['items_not_to_tracker']:
            print(item.vacancy, item.organization, item.date)
    driver.quit()
