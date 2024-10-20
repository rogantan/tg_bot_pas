import telebot
from init_bot import bot
from db import create_tables
from handlers import register_handlers


if __name__ == "__main__":
    create_tables()
    register_handlers()
    bot.add_custom_filter(telebot.custom_filters.StateFilter(bot))
    bot.infinity_polling()
