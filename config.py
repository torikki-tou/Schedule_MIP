import os
from enum import Enum

TOKEN = os.environ.get('TOKEN')

URL = 'https://clients6.google.com/calendar/v3/calendars/c_537r1a5d5tl0titv5e1e7qgsbs@group.calendar.google.com/events'

SECRET = os.environ.get('SECRET')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL') + SECRET

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.203'
}

PARAMS = {
    'calendarId': 'c_537r1a5d5tl0titv5e1e7qgsbs@group.calendar.google.com',
    'singleEvents': 'true',
    'timeZone': 'Europe/Moscow',
    'maxAttendees': '1',
    'maxResults': '250',
    'sanitizeHtml': 'true',
    # 'timeMin': '2021-11-08T00:00:00+03:00',
    # 'timeMax': '2021-11-09T00:00:00+03:00',
    # 'key': ''
}

DB_PARAMS = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'port': os.environ.get('DB_PORT'),
    'database': os.environ.get('DB_NAME'),
}


class Status(Enum):
    S_START = 0
    S_GROUP = 1


weekdays = {
    0: 'Понедельник',
    1: 'Вторник',
    2: 'Среда',
    3: 'Четверг',
    4: 'Пятница',
    5: 'Суббота',
    6: 'Воскресенье',
}

months = {
    1: 'января',
    2: 'февраля',
    3: 'марта',
    4: 'апреля',
    5: 'мая',
    6: 'июня',
    7: 'июля',
    8: 'августа',
    9: 'сентября',
    10: 'октября',
    11: 'ноября',
    12: 'декабря',
}
