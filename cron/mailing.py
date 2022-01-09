import datetime as dt
from time import sleep

from main import bot
from parsing_tools import next_day, next_week
from dbworker import get_all_signed, get_group, get_group_key


is_saturday = dt.datetime.now().weekday() == 5
signed_users = get_all_signed()

for user in signed_users:
    group = get_group(user)
    group_key = get_group_key(group)
    if is_saturday:
        text = next_week(group_key)
    else:
        text = next_day(group_key)
    bot.send_message(
        user,
        text,
        parse_mode='MarkdownV2'
    )
    sleep(0.04)
