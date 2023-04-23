import locale
from datetime import datetime

from dotenv import load_dotenv

from career_tracker import tracker
from hh import read_from_hh

load_dotenv()
locale.setlocale(locale.LC_ALL, '')

if __name__ == '__main__':    
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
