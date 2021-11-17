import telebot as tb
from flask import Flask, request
from flask_sslify import SSLify
import parsing_tools
import config


bot = tb.TeleBot(config.TOKEN, threaded=False)

app = Flask(__name__)
sslify = SSLify(app)

bot.remove_webhook()
bot.set_webhook(url=config.WEBHOOK_URL)


@app.route('/' + config.SECRET, methods=['POST'])
def webhook():
    update = tb.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200


def homepage_keyboard() -> tb.types.ReplyKeyboardMarkup:
    base_keyboard = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)
    base_keyboard.row(
        tb.types.KeyboardButton('На сегодня'),
        tb.types.KeyboardButton('На завтра'),
        tb.types.KeyboardButton('На неделю')
    )
    return base_keyboard


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        'Привет! Используй кнопки, чтобы получать расписание, когда тебе оно понадобится. '
        'А ещё я сам присылаю расписание на завтра каждый день в 20:30, кроме субботы. '
        'Потому что в субботу я присылаю расписание на всю следующую неделю!',
        reply_markup=homepage_keyboard()
    )


@bot.message_handler(content_types=['text'])
def main_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')

    if message.text == 'На сегодня':
        bot.send_message(
            message.chat.id,
            parsing_tools.today(),
            parse_mode='MarkdownV2',
            reply_markup=homepage_keyboard()
        )
    elif message.text == 'На завтра':
        bot.send_message(
            message.chat.id,
            parsing_tools.next_day(),
            parse_mode='MarkdownV2',
            reply_markup=homepage_keyboard()
        )
    elif message.text == 'На неделю':
        bot.send_message(
            message.chat.id,
            parsing_tools.next_week(),
            parse_mode='MarkdownV2',
            reply_markup=homepage_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            'Прости, я не понимаю твоё сообщение :(',
            reply_markup=homepage_keyboard()
        )
