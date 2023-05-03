import locale
from datetime import datetime

from dotenv import load_dotenv

from career_tracker import log_in_tracker, tracker, vacancy_to_tracker
from hh import log_in, read_from_hh
from utils import Item, date_to_internal, set_driver, tz

load_dotenv()
locale.setlocale(locale.LC_ALL, '')

if __name__ == '__main__':
#    item = Item(vacancy='Тестовая вакансия', organization='Тестовая организация', date=date_to_internal('24 апреля 2023', tz=tz), rejected=False)
#    driver = set_driver()
#    log_in_tracker(driver)
#    vacancy_to_tracker(driver, item)
#    driver.quit()

    answer = 'n'
    while answer.lower() != 'y':
        print('Введи дату ДД.ММ.ГГГГ, например 01.04.2023')
        date_str = input()
        stop_date = datetime.strptime(date_str, '%d.%m.%Y').date()
        print(f'{datetime.strftime(stop_date, "%d %B %Y")}, правильно? y/n')
        answer = input()
    items_list = read_from_hh(stop_date)
    items_list.reverse()
    tracker(items_list)
