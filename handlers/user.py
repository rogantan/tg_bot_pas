import time
from datetime import datetime
from init_bot import bot
from telebot import formatting as form
from telebot.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from functions import gen_markup_media, gen_markup_bool, User, Newsletter, Opros
from db import (add_user, select_users_id, select_user, select_admin_id, select_admins_id, add_newsletter,
                select_newsletters, save_variants, save_question, select_questions, get_question, get_variants,
                update_statistic, select_total_statistic)


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.send_message(message.from_user.id, text=f'Привет, {message.from_user.first_name}!')
    time.sleep(1)
    if select_user(str(message.from_user.id)) is None:
        admin_id = select_admin_id()
        bot.send_message(chat_id=admin_id[0],
                         text=f'Написал пользователь id - {message.from_user.id}, имя - {message.from_user.first_name}')
        add_user(str(message.from_user.id), message.from_user.username, message.from_user.first_name)
    else:
        bot.send_message(message.from_user.id, text=f'Меня зовут {form.hitalic("Екатерина Полякова")}', parse_mode='HTML')
        time.sleep(1)
        bot.send_message(message.from_user.id, text=f'Я открыла для себя {form.hbold("Access Bars")} в 2017 году. До знакомства с '
                                                f'{form.hbold("Access Bars")} я:\n'
                                                f'- рисовала энергетические картины,\n'
                                                f'- вела занятия по лицевой гимнастике,\n'
                                                f'- занималась аромотерапией,\n'
                                                f'- давала сеансы массажа по методике Рейки Дао Дэ Ки.', parse_mode='HTML')
        time.sleep(2)
        bot.send_message(message.from_user.id, text=f'{form.hbold("Access Bars")} помог мне вывести мои знания на новый уровень. '
                                                f'Невероятный набор инструментов для работы с собой и другими людьми, '
                                                f'неограниченные возможности для {form.hitalic("трансформации")}, восхитительные изменения, '
                                                f'которые я наблюдаю в своей жизни и жизни своих клиентов, окрыляют. '
                                                f'У меня горячее желание {form.hitalic("развиваться")} в данном направлении и делиться своими знаниями с миром.',
                        parse_mode='HTML')
        time.sleep(3)
        bot.send_message(message.from_user.id, text=f'Я буду рада встретиться с каждым из Вас:\n'
                                                f'- {form.hbold("на сессии")} (обещаю, это будет лучший энергетический массаж в Вашей жизни :)),\n'
                                                f'- {form.hbold("на обучении")} (Вы сможете дарить хорошее настроение и позитивные изменения в жизни близким Вам людям),\n'
                                                f'- {form.hbold("на Встречах знакомств с инструментами Аксесс")} (я подробнее расскажу Вам об Access Bars, а Вы вживую увидите мою энергетику)',
                        parse_mode='HTML')
    time.sleep(5)
    bot.send_message(message.from_user.id, text="Если вы хотите лично мне написать, нажмите команду /write")


@bot.message_handler(commands=['write'])
def write(message: Message):
    bot.send_message(message.from_user.id, text="Напишите ваше имя: ")
    bot.set_state(message.from_user.id, User.name)


@bot.message_handler(state=User.name)
def write_name(message: Message):
    with bot.retrieve_data(message.from_user.id) as data:
        data['name'] = message.text
    bot.send_message(message.from_user.id, text="Спасибо! Напишите, пожалуйста, ваши цели, ожидания от Access Bars:")
    bot.set_state(message.from_user.id, User.purpose)


@bot.message_handler(state=User.purpose)
def write_purpose(message: Message):
    admins_list = select_admin_id()
    with bot.retrieve_data(message.from_user.id) as data:
        data['purpose'] = message.text
    bot.send_message(message.from_user.id, text="Спасибо большое! Я свяжусь с вами в ближайшее время :)")
    bot.send_message(chat_id=admins_list[0], text=f"Пользователь @{message.from_user.username} хочет в вами связаться\n"
                                       f"Имя - {data['name']}, цели - {data['purpose']}")
    bot.delete_state(message.from_user.id, message.from_user.id)


@bot.message_handler(commands=['social_media'])
def media(message: Message):
    bot.send_message(message.from_user.id, text=f"Мои {form.hbold('социальные сети')}:", reply_markup=gen_markup_media(), parse_mode='HTML')


@bot.message_handler(commands=['tg_channel'])
def channel(message: Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Tg-channel", url="https://t.me/akcecckrasota"))
    bot.send_message(message.from_user.id, text=f"{form.hitalic('Добро пожаловать!')}", reply_markup=markup, parse_mode='HTML')


@bot.message_handler(commands=['newsletter'])
def newsletter(message: Message):
    admins_list = select_admins_id(str(message.from_user.id))
    if admins_list is not None:
        bot.send_message(message.from_user.id, text="Введите текст рассылки:")
        bot.set_state(message.from_user.id, Newsletter.text)
    else:
        bot.send_message(message.from_user.id, text=f"У вас {form.hbold('нет прав')} на эту команду...", parse_mode='HTML')


@bot.message_handler(commands=['opros'])
def create_opros(message: Message):
    admins_list = select_admins_id(str(message.from_user.id))
    if admins_list is not None:
        bot.send_message(message.from_user.id, text="Введите текст вопроса")
        bot.set_state(message.from_user.id, Opros.question_text)


@bot.message_handler(state=Opros.question_text)
def question_text(message: Message):
    with bot.retrieve_data(message.from_user.id) as text:
        text['question'] = message.text
    # save to db
    now_date = datetime.now()
    save_question(question_text=text['question'], admin_id=str(message.from_user.id), date=now_date)
    bot.send_message(message.from_user.id, text="Вопрос добавился!")
    time.sleep(1)
    bot.send_message(message.from_user.id, text="Теперь введите варианты ответов...\n"
                                                "Каждый вариант с новой строчки")
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.set_state(message.from_user.id, Opros.choices_text, message.chat.id)


@bot.message_handler(state=Opros.choices_text)
def choices_text(message: Message):
    admin_id = str(message.from_user.id)
    with bot.retrieve_data(message.from_user.id) as text:
        text['variants'] = message.text
    variants = text['variants'].split('\n')
    for variant in variants:
        save_variants(variant, admin_id)
    bot.send_message(message.from_user.id, text="Варианты ответов добавлены!")
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(state=Newsletter.text)
def state_text(message: Message):
    with bot.retrieve_data(message.from_user.id) as mess:
        mess['text'] = message.text
    date = datetime.now()
    add_newsletter(mess['text'], date, str(message.from_user.id))
    users_list = select_users_id()
    for user in users_list:
        bot.send_message(chat_id=user[0], text=mess['text'], parse_mode='HTML')
    bot.send_message(message.from_user.id, text="Фотографию добавляем?", reply_markup=gen_markup_bool("yes_p", "no_p"))


@bot.message_handler(commands=['send_opros'])
def send_opros(message: Message):
    questions = select_questions()
    arr = []
    for question in questions:
        arr.append(f"{question[0]}) {question[1]}\n")
    text = "".join(arr)
    bot.send_message(message.from_user.id, text=text)
    bot.send_message(message.from_user.id, text="Введите id вопроса, который хотите отправить")
    bot.set_state(message.from_user.id, Opros.num_question)


@bot.message_handler(state=Opros.num_question)
def num_question(message: Message):
    with bot.retrieve_data(message.from_user.id) as text:
        text['num'] = message.text
    num = int(message.text)
    question = get_question(num)
    variants = get_variants(num)
    text = f"{question[0]}\n"
    markup = InlineKeyboardMarkup()
    for var in variants:
        markup.add(InlineKeyboardButton(text=f"{var[0]}", callback_data=f"{var[1]}"))
    users = select_users_id()
    for user in users:
        bot.send_message(chat_id=user[0], text=text, reply_markup=markup)
    bot.delete_state(message.from_user.id, message.chat.id)


@bot.message_handler(commands=['all_newsletters'])
def all_newsletters(message: Message):
    newsletters = select_newsletters()
    arr = []
    for newsletter in newsletters:
        arr.append(f"{newsletter[0]}) {newsletter[1]}\nДата публикации {newsletter[2]}\n")
    text = "\n".join(arr)
    bot.send_message(message.from_user.id, text=text)


@bot.message_handler(commands=['total_statistic'])
def statistic(message: Message):
    users = select_users_id()
    markup = InlineKeyboardMarkup()
    for user in users:
        markup.add(InlineKeyboardButton(text=f"{user[1]}", callback_data=f"{user[1]}"))
    bot.send_message(message.from_user.id, text="Выберите пользователя, у которого хотите посмотреть статистику",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: CallbackQuery):
    if call.data == "yes_p":
        bot.send_message(call.from_user.id, text="Отправьте фото:")
    elif call.data == "no_p":
        bot.delete_state(call.from_user.id, call.from_user.id)
    elif call.data.isdigit():
        choice_id = int(call.data)
        date = datetime.now()
        update_statistic(choice_id, str(call.from_user.id), date)
    else:
        statistic = select_total_statistic(call.data)
        arr = []
        arr.append(f" Статистика для @{statistic[0][0]}\n")
        for stat in statistic:
            arr.append(f"{stat[1]}\nОтвет - {stat[2]} {stat[3]}\n\n")
        text = "".join(arr)
        bot.send_message(call.from_user.id, text=text)
    bot.delete_message(call.from_user.id, call.message.message_id)


@bot.message_handler(content_types=['photo'])
def photo(message: Message):
    users_list = select_users_id()
    admins_list = select_admins_id(str(message.from_user.id))
    if admins_list is not None:
        for user in users_list:
             bot.send_photo(chat_id=user[0], photo=message.photo[-1].file_id)
    else:
        bot.send_message(message.from_user.id, text="Вы не можете отправлять фотографии...")


@bot.message_handler(state='*')
def cancel(message: Message):
    bot.send_message(message.from_user.id, text='Список доступных команд для бота:\n'
                                                '/social_media - мои социальные сети\n'
                                                '/tg_channel - мой телеграм-канал\n')
