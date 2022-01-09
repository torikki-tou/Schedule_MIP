import requests
import datetime as dt
import config

timezone = dt.timezone(dt.timedelta(hours=3), 'МСК')


def markdown_helper(row_string: str) -> str:
    """Добавляет слеши перед символами, чтобы разметка телеграма работала корректно"""
    exclusions = ['*', '_']

    refactored_string = ''
    for char in row_string:
        if char not in exclusions and 1 <= ord(char) <= 127:
            refactored_string += '\\' + char
        else:
            refactored_string += char
    return refactored_string


def set_params(from_time: str, until_time: str, key) -> dict:
    """Создает словарь параметров под конкретное соединение"""
    time_params = {
        'timeMin': f'{from_time}T00:00:00+03:00',
        'timeMax': f'{until_time}T00:00:00+03:00',
        'key': key
    }
    return {**config.PARAMS, **time_params}


def lecture_format(lecture) -> str:
    """Парсит запись о конкретной лекции и формирует в строку"""
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
    """Парсит дату с точностью до дня и формирует строку с указанием дня недели"""
    date = dt.datetime.strptime(
        lecture['start']['dateTime'].split('T')[0],
        '%Y-%m-%d'
    )
    return f'\n\n*__{config.weekdays[date.weekday()]}, {date.day} {config.months[date.month]}__*\n'


def today(group_key: str) -> str:
    """Расписание на сегодня для конкретной группы"""
    # Сегодняшняя дата и следующий день для параметров запроса
    _today = dt.datetime.now(timezone).date()
    end_day = _today + dt.timedelta(days=1)

    # Запрос и получение списка лекций в виде словаря
    data = requests.get(
        url=config.URL,
        headers=config.HEADERS,
        params=set_params(
            from_time=str(_today),
            until_time=str(end_day),
            key=group_key)
    )
    data = data.json()['items']

    # Проверка наличия лекций
    if not data:
        return markdown_helper('*Поздравляю! Сегодня у тебя нет ни одной пары!*\n\n')

    # Сортировка, подготовка к оформлению в строку
    sorted_data = sorted(
        data,
        key=lambda lecture: lecture['start']['dateTime']
    )

    # Оформление данных в формате для ответа
    response = 'Вот твоё расписание на сегодня:\n\n'
    for _class in sorted_data:
        response += lecture_format(_class)

    return markdown_helper(response)


def next_day(group_key: str) -> str:
    """Расписание на неделю для конкретной группы"""
    # Завтрашняя дата и следующий день для параметров запроса
    tomorrow = dt.datetime.now(timezone).date() + dt.timedelta(days=1)
    end_day = tomorrow + dt.timedelta(days=1)

    # Проверка времени, чтобы узнать может ли ещё поменяться расписание
    can_change = False if dt.datetime.now(timezone).hour >= 20 else True

    # Запрос и получение списка лекций в виде словаря
    data = requests.get(
        url=config.URL,
        headers=config.HEADERS,
        params=set_params(
            from_time=str(tomorrow),
            until_time=str(end_day),
            key=group_key)
    )
    data = data.json()['items']

    # Проверка наличия лекций
    if not data:
        response = '*Поздравляю! Завтра у тебя нет ни одной пары!*'
        if can_change:
            response += '\n\nОднако расписание на каждый день может меняться до 20:00 предыдущего дня, ' \
                        'поэтому будь внимателен!'
        else:
            response += '\n\nСейчас уже позже 20:00, поэтому расписание меняться больше не должно'
        return markdown_helper(response)

    # Сортировка, подготовка к оформлению в строку
    sorted_data = sorted(
        data,
        key=lambda lecture: lecture['start']['dateTime']
    )

    # Оформление данных в формате для ответа
    response = 'Вот твоё расписание на завтра:\n\n'
    for _class in sorted_data:
        response += lecture_format(_class)

    # Проверка времени, чтобы узнать может ли ещё поменяться расписание
    if not can_change:
        response += '\nСейчас уже позже 20:00, поэтому расписание меняться больше не должно'
    else:
        response += 'Расписание на завтра может меняться до 20:00 сегодняшнего дня!'

    return markdown_helper(response)


def next_week(group_key: str) -> str:
    """Расписание на неделю для конкретной группы"""
    # Завтрашняя дата и дата спустя для параметров запроса
    tomorrow = dt.datetime.now(timezone).date() + dt.timedelta(days=1)
    end_day = tomorrow + dt.timedelta(days=7)

    # Запрос и получение списка лекций в виде словаря
    data = requests.get(
        url=config.URL,
        headers=config.HEADERS,
        params=set_params(
            from_time=str(tomorrow),
            until_time=str(end_day),
            key=group_key)
    )
    data = data.json()['items']

    # Проверка наличия лекций
    if not data:
        return markdown_helper(
            '*Поздравляю! У тебя нет пар всю следующую неделю!*\n\n'
            'Однако расписание на каждый день может меняться до 20:00 предыдущего дня, поэтому будь внимателен!')

    # Сортировка, подготовка к оформлению в строку
    sorted_data = sorted(
        data,
        key=lambda item: item['start']['dateTime']
    )

    # Оформление данных в формате для ответа
    date = ''
    response = 'Вот твоё расписание на следующую неделю:\n'
    for lecture in sorted_data:

        if date != lecture['start']['dateTime'].split('T')[0]:
            response += date_format(lecture)
            date = lecture['start']['dateTime'].split('T')[0]

        response += lecture_format(lecture)
    response += '\nРасписание на каждый день может меняться до 20:00 предыдущего дня, будь внимателен!'

    return markdown_helper(response)
