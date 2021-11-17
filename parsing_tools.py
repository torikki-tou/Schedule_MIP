import requests
import datetime as dt
import config


def markdown_helper(row_string: str) -> str:
    exclusions = ['*', '_']
    refactored_string = ''
    for char in row_string:
        if char not in exclusions and 1 <= ord(char) <= 127:
            refactored_string += '\\' + char
        else:
            refactored_string += char
    return refactored_string


def set_params(from_time: str, until_time: str) -> dict:
    time_params = {
        'timeMin': f'{from_time}T00:00:00+03:00',
        'timeMax': f'{until_time}T00:00:00+03:00',
    }
    return {**config.PARAMS, **time_params}


def lecture_format(lecture) -> str:

    def time_format(start_end: str = 'start' or 'end') -> str:
        hours = lecture[start_end]['dateTime'].split('T')[1].split('+')[0][0:2]
        minutes = lecture[start_end]['dateTime'].split('T')[1].split('+')[0][3:5]
        return hours + ':' + minutes

    lecture_name = lecture['summary']
    location = lecture['location'].split(' - ')[0]
    teacher = lecture['location'].split(' - ')[1]
    start_time = time_format('start')
    end_time = time_format('end')
    duration = f'{start_time} - {end_time}'
    return f'*{lecture_name}*\n_{location} \u2014 {teacher} \u2014 {duration}_\n\n'


def date_format(lecture: dict) -> str:
    date = dt.datetime.strptime(
        lecture['start']['dateTime'].split('T')[0],
        '%Y-%m-%d'
    )

    return f'\n\n*__{config.weekdays[date.weekday()]}, {date.day} {config.months[date.month]}__*\n'


def today() -> str:
    # noinspection PyShadowingNames
    today = dt.date.today()
    end_day = today + dt.timedelta(days=1)

    data = requests.get(
        url=config.URL,
        headers=config.HEADERS,
        params=set_params(
            from_time=str(today),
            until_time=str(end_day)),

    )
    data = data.json()['items']

    if data:
        sorted_data = sorted(
            data,
            key=lambda lecture: lecture['start']['dateTime']
        )

        response = 'Вот твоё расписание на сегодня:\n\n'
        for _class in sorted_data:
            response += lecture_format(_class)
    else:
        response = '*Поздравляю! Сегодня у тебя нет ни одной пары!*\n\n'

    return markdown_helper(response)


def next_day(notification: bool = False) -> str:
    tomorrow = dt.date.today() + dt.timedelta(days=1)
    end_day = tomorrow + dt.timedelta(days=1)

    data = requests.get(
        url=config.URL,
        headers=config.HEADERS,
        params=set_params(
            from_time=str(tomorrow),
            until_time=str(end_day)),

    )
    data = data.json()['items']

    if data:
        sorted_data = sorted(
            data,
            key=lambda lecture: lecture['start']['dateTime']
        )

        response = 'Вот твоё расписание на завтра:\n\n'
        for _class in sorted_data:
            response += lecture_format(_class)
        if notification:
            response += '\nСейчас уже позже 20:00, поэтому расписание меняться больше не должно'
        else:
            response += 'Расписание на завтра может меняться до 20:00 сегодняшнего дня!'
    else:
        response = '*Поздравляю! Завтра у тебя нет ни одной пары!*\n\n' \
                   'Однако расписание на каждый день может меняться до 20:00 предыдущего дня, поэтому будь внимателен!'

    return markdown_helper(response)


def next_week(notification: bool = False) -> str:
    tomorrow = dt.date.today() + dt.timedelta(days=1)
    end_day = tomorrow + dt.timedelta(days=7)

    data = requests.get(
        url=config.URL,
        headers=config.HEADERS,
        params=set_params(
            from_time=str(tomorrow),
            until_time=str(end_day)),

    )
    data = data.json()['items']

    if data:
        sorted_data = sorted(
            data,
            key=lambda lecture: lecture['start']['dateTime']
        )

        date = ''
        response = 'Вот твоё расписание на следующую неделю:\n'
        for _class in sorted_data:
            if date != _class['start']['dateTime'].split('T')[0]:
                response += date_format(_class)
                date = _class['start']['dateTime'].split('T')[0]
            response += lecture_format(_class)

        if notification:
            response += '\nСейчас уже позже 20:00, поэтому расписание меняться больше не должно'
        else:
            response += '\nРасписание на каждый день может меняться до 20:00 предыдущего дня, будь внимателен!'
    else:
        response = '*Поздравляю! У тебя нет пар всю следующую неделю!*\n\n' \
                   'Однако расписание на каждый день может меняться до 20:00 предыдущего дня, поэтому будь внимателен!'
    return markdown_helper(response)
