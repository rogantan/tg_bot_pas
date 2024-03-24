import random
import string
import time
from t import TOKEN
import telebot


def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password


bot = telebot.TeleBot(TOKEN)


class LenState(telebot.handler_backends.StatesGroup):
    length = telebot.handler_backends.State()


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message: telebot.types.Message):
    bot.reply_to(message, text=f"<b>Привет, {message.from_user.first_name}!</b> Этот бот генерирует "
                          f"<i>случайный пароль.</i>", parse_mode='HTML')
    time.sleep(2)
    bot.send_message(message.from_user.id, text="Для того, чтобы сгенерировать <u>новый пароль</u> нажмите на /create",
                     parse_mode='HTML')


@bot.message_handler(commands=['create'])
def create(message: telebot.types.Message):
    bot.send_message(message.chat.id, text="Введите длину <b>пароля</b>: ", parse_mode='HTML')
    bot.set_state(message.from_user.id, LenState.length, message.chat.id)


@bot.message_handler(state=LenState.length)
def state(message: telebot.types.Message):
    try:
        with bot.retrieve_data(message.from_user.id) as data:
            data['length'] = message.text
        length = int(data['length'])
        result = generate_password(length)
    except ValueError:
        bot.delete_state(message.from_user.id, message.chat.id)
        bot.send_message(message.chat.id, text="<b>Введено некорректное значение!</b>", parse_mode='HTML')
        time.sleep(1)
        bot.send_message(message.chat.id, text="Введите новое значение:")
        bot.set_state(message.from_user.id, LenState.length, message.chat.id)
    else:
        bot.send_message(message.from_user.id, text="Новый пароль будет сформирован через:", parse_mode='HTML')
        time.sleep(1)
        for i in range(5, 0, -1):
            bot.send_message(message.from_user.id, text=f"<b>{i}</b>", parse_mode='HTML')
            time.sleep(1)
        bot.send_message(message.chat.id, text=f"{result}")
        time.sleep(1)
        bot.send_message(message.chat.id, text="<i>Пароль сформирован!</i>", parse_mode='HTML')
        bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state='*')
def state_1(message: telebot.types.Message):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.chat.id, text="Для того, чтобы сгенерировать <u>новый пароль</u> нажмите на /create",
                     parse_mode='HTML')


bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
bot.infinity_polling()
