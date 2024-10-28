from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.handler_backends import State, StatesGroup


class User(StatesGroup):
    name = State()
    purpose = State()


class Newsletter(StatesGroup):
    text = State()
    id = State()


class Opros(StatesGroup):
    question_text = State()
    choices_text = State()
    num_question = State()


def gen_markup_media() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("VK", url="https://vk.com/accesspolyakova"),
        InlineKeyboardButton("INST", url="https://www.instagram.com/ekaterinapolyakova.access/"),
        InlineKeyboardButton("Tg-channel", url="https://t.me/akcecckrasota")
    )
    return markup


def gen_markup_bool(yes: str, no: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Да", callback_data=yes),
               InlineKeyboardButton("Нет", callback_data=no))
    return markup