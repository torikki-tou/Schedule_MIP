import telebot as tb
import parsing_tools
from config import TOKEN


bot = tb.TeleBot(TOKEN)

base_keyboard = tb.types.ReplyKeyboardMarkup(resize_keyboard=True)
base_keyboard.row(tb.types.KeyboardButton('На сегодня'), tb.types.KeyboardButton('На завтра'), tb.types.KeyboardButton('На неделю'))


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(
        message.chat.id,
        'Привет! Используй кнопки, чтобы получать расписание, когда тебе оно понадобится. '
        'А ещё я сам присылаю расписание на завтра каждый день в 20:30, кроме субботы. '
        'Потому что в субботу я присылаю расписание на всю следующую неделю!',
        reply_markup=base_keyboard
    )


@bot.message_handler(content_types=['text'])
def main_handler(message):
    bot.send_chat_action(message.chat.id, 'typing')

    if message.text == 'На сегодня':
        bot.send_message(
            message.chat.id,
            parsing_tools.today(),
            parse_mode='MarkdownV2',
            reply_markup=base_keyboard
        )
    elif message.text == 'На завтра':
        bot.send_message(
            message.chat.id,
            parsing_tools.next_day(),
            parse_mode='MarkdownV2',
            reply_markup=base_keyboard
        )
    elif message.text == 'На неделю':
        bot.send_message(
            message.chat.id,
            parsing_tools.next_week(),
            parse_mode='MarkdownV2',
            reply_markup=base_keyboard
        )
    else:
        bot.send_message(
            message.chat.id,
            'Прости, я не понимаю твоё сообщение :(',
            reply_markup=base_keyboard
        )


if __name__ == '__main__':
    print('Bot started')
    bot.infinity_polling()
