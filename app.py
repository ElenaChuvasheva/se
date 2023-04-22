import locale
from datetime import datetime

from dotenv import load_dotenv

from hh import read_from_hh

load_dotenv()
locale.setlocale(locale.LC_ALL, '')

if __name__ == '__main__':
    stop_date = datetime(year=2023, month=4, day=4).date()
    items = read_from_hh(stop_date)
