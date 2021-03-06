import telebot as tb
# from flask import Flask, request
# from flask_sslify import SSLify
import parsing_tools
import dbworker
import config


bot = tb.TeleBot(config.TOKEN, threaded=False)

# app = Flask(__name__)
# sslify = SSLify(app)
#
# bot.remove_webhook()
# bot.set_webhook(url=config.WEBHOOK_URL)
#
#
# @app.route('/' + config.SECRET, methods=['POST'])
# def webhook():
#     update = tb.types.Update.de_json(request.stream.read().decode('utf-8'))
#     bot.process_new_updates([update])
#     return 'ok', 200


def setup_keyboard(pk: int) -> tb.types.ReplyKeyboardMarkup:
    """Собирает клавиатуру в соответствии со статусом пользователя"""
    keyboard = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)
    status = dbworker.get_status(pk)
    got_group = dbworker.get_group(pk) or None
    signed_up = dbworker.is_signed_up(pk)
    if status == config.Status.S_START.value and got_group:
        keyboard.row(
            tb.types.KeyboardButton('На сегодня'),
            tb.types.KeyboardButton('На завтра'),
            tb.types.KeyboardButton('На неделю')
        )
        keyboard.row(
            tb.types.KeyboardButton('Подписаться на рассылку' if not signed_up else 'Отписаться от рассылки'),
            tb.types.KeyboardButton('Изменить группу')
        )
    if status == config.Status.S_GROUP.value and got_group:
        keyboard.row(
            tb.types.KeyboardButton('На главную')
        )
    keyboard.row(
        tb.types.KeyboardButton('Помощь'),
        tb.types.KeyboardButton('О проекте'),
        tb.types.KeyboardButton('Поддержать')
    )
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    """Обработка команды /start, создание в базе нового пользователя, начало ветки выбора группы"""
    bot.send_chat_action(message.chat.id, 'typing')

    response = 'Привет! Используй кнопки, чтобы получать расписание, когда тебе оно понадобится. ' \
               'А ещё я сам присылаю расписание на завтра каждый день в 20:30, кроме субботы. ' \
               'Потому что в субботу я присылаю расписание на всю следующую неделю! '

    # Создание нового пользователя
    dbworker.new_user(pk=message.chat.id, username=message.from_user.username)

    # Проверка наличия установленной группы
    if not dbworker.get_group(pk=message.chat.id):
        dbworker.set_status(pk=message.chat.id, status=config.Status.S_GROUP.value)
        response += '\n\nЕдинственное, что от тебя потребуется — номер твоей группы'

    bot.send_message(
        message.chat.id,
        response,
        reply_markup=setup_keyboard(message.chat.id)
    )


@bot.message_handler(
    func=lambda message:
    dbworker.get_status(pk=message.chat.id) is None or dbworker.get_group(pk=message.chat.id) is None
)
def status_none(message):
    """Проверка наличия пользователя в базе"""
    bot.send_chat_action(message.chat.id, 'typing')

    if not dbworker.get_status(pk=message.chat.id):
        bot.send_message(
            message.chat.id,
            'Бот получил крупное обновление, чтобы продолжить им пользоваться, пожалуйста, введите /start ещё раз',
            reply_markup=tb.types.ReplyKeyboardRemove()
        )

    if not dbworker.get_group(pk=message.chat.id):
        dbworker.set_status(pk=message.chat.id, status=config.Status.S_GROUP.value)
        bot.send_message(
            message.chat.id,
            'Для продолжения необходимо ввести номер группы!',
            reply_markup=setup_keyboard(message.chat.id)
        )


@bot.message_handler(
    func=lambda message: message.text in ('Помощь', 'О проекте', 'Поддержать', 'На главную')
)
def utils(message):
    """Обработка вспомогательных команд, доступных в любом режиме"""
    bot.send_chat_action(message.chat.id, 'typing')

    if message.text == 'Помощь':
        bot.send_message(
            message.chat.id,
            'Если у тебя возникли какие либо сложности, вопросы или предложения по функционалу бота, '
            'то напиши @torikki',
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )
    elif message.text == 'О проекте':
        bot.send_message(
            message.chat.id,
            '[\u0000](https://telegra.ph/O-proekte-11-18)Немного об этом боте и обо мне',
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )
    elif message.text == 'Поддержать':
        bot.send_message(
            message.chat.id,
            '[\u0000](https://www.tinkoff.ru/rm/perkhulov.tikhon1/YPnua68314)' +
            parsing_tools.markdown_helper(
                'Пользователей пока немного, поэтому бот работает на бесплатном хостинге, '
                'но вы всё равно можете скинуть мне копеечку за старания'),
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )
    elif message.text == 'На главную':
        dbworker.set_status(pk=message.chat.id, status=config.Status.S_START.value)
        bot.send_message(
            message.chat.id,
            'Отмена',
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )


@bot.message_handler(
    content_types=['text'],
    func=lambda message: dbworker.get_status(pk=message.chat.id) == config.Status.S_START.value
)
def start_status(message):
    """Обработка всех сообщений с базовым статусом, основные команды"""
    bot.send_chat_action(message.chat.id, 'typing')

    if message.text == 'На сегодня':
        bot.send_message(
            message.chat.id,
            parsing_tools.today(
                group_key=dbworker.get_group_key(group=dbworker.get_group(message.chat.id))
            ),
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )
    elif message.text == 'На завтра':
        bot.send_message(
            message.chat.id,
            parsing_tools.next_day(
                group_key=dbworker.get_group_key(group=dbworker.get_group(message.chat.id))
            ),
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )
    elif message.text == 'На неделю':
        bot.send_message(
            message.chat.id,
            parsing_tools.next_week(
                group_key=dbworker.get_group_key(group=dbworker.get_group(message.chat.id))
            ),
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )
    elif message.text == 'Подписаться на рассылку':
        dbworker.sign_up_or_off(message.chat.id, True)
        bot.send_message(
            message.chat.id,
            'Поздравляю, ты подписался на рассылку расписания\!'
            '\n\nТеперь ты каждый вечер будешь получать расписание на завтрашний день, '
            'а по субботам — на всю следующую неделю',
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )
    elif message.text == 'Отписаться от рассылки':
        dbworker.sign_up_or_off(message.chat.id, False)
        bot.send_message(
            message.chat.id,
            'Подписка на рассылку отключена',
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )
    elif message.text == 'Изменить группу':
        dbworker.set_status(pk=message.chat.id, status=config.Status.S_GROUP.value)
        bot.send_message(
            message.chat.id,
            'Теперь введи название группы',
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id)
        )
    else:
        bot.send_message(
            message.chat.id,
            'Прости, я не понимаю твоё сообщение :(',
            reply_markup=setup_keyboard(message.chat.id)
        )


@bot.message_handler(
    content_types=['text'],
    func=lambda message: dbworker.get_status(pk=message.chat.id) == config.Status.S_GROUP.value
)
def group_status(message):
    """Обработка сообщений со статусом ожидания номера группы"""
    bot.send_chat_action(message.chat.id, 'typing')

    # Проверка существования выбранной группы в базе
    if not dbworker.group_exists(message.text):

        # Получение полного списка групп
        all_groups = dbworker.get_all_groups()

        bot.send_message(
            message.chat.id,
            '[\u0000](https://telegra.ph/Kak-dobavit-svoyu-gruppu-v-bota-11-18)' +
            parsing_tools.markdown_helper(
                'Я пока не могу присылать расписание для этой группы :('
                '\nВозможно, ты просто неправильно написал(а) ее название. '
                f'\n\nПоддерживаются: {", ".join(all_groups)}'
                '\n\nЕсли твоя группа ещё не поддерживается, то вот гайд как её добавить:'),
            parse_mode='MarkdownV2',
            reply_markup=setup_keyboard(message.chat.id))
        return

    # Присвоение выбранной группы пользователю, переход в обычный режим
    dbworker.set_group(pk=message.chat.id, group=message.text)
    dbworker.set_status(pk=message.chat.id, status=config.Status.S_START.value)

    bot.send_message(
        message.chat.id,
        f'Отлично, теперь я знаю, что ты из группы {message.text}, и смогу присылать тебе расписание',
        reply_markup=setup_keyboard(message.chat.id))


if __name__ == '__main__':
    bot.infinity_polling()
