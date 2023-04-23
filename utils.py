from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from selenium import webdriver
from selenium.common.exceptions import TimeoutException

tz = timezone(timedelta(hours=3), name='Мск')

@dataclass
class Item:
    vacancy: str
    date: datetime.date
    organization: str

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

def date_to_internal(date_str, tz):
    if date_str == 'вчера':
        full_timestamp = datetime.now(tz=tz) - timedelta(days=1)
        return full_timestamp.date()
    split_date = date_str.split()
    split_date[1] = months[split_date[1]]
    changed_date = ' '.join(split_date).rstrip()
    return datetime.strptime(changed_date, '%d %B %Y').date()

def set_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    return webdriver.Chrome(options=options)

def get_limited_time(driver, url, time=10):
    driver.set_page_load_timeout(time)
    try:
        driver.get(url)
    except TimeoutException:
        pass

def str_format(vacancy, organization):
    return vacancy + ' ' + organization

def item_str_format(item):
    return str_format(item.vacancy, item.organization)
