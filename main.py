import telebot
import requests
import json
import os

from os import getenv
from telebot import types
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

bot = telebot.TeleBot(getenv('PAVEL_TELEGRAM_API_KEY'))

CURRENCY_RATES_FILE = "currency_rates.json"
API_KEY = getenv('APILAYER_API_KEY')


def get_currency_rate(currency: str):
    """Получает курс валюты от API и возвращает его в виде float"""

    url = f"https://api.apilayer.com/exchangerates_data/latest?base={currency}"
    response = requests.get(url, headers={'apikey': API_KEY})
    response_data = json.loads(response.text)
    return response_data


def save_to_json(data_to_save: dict):
    """Сохраняет данные в JSON-файл"""
    with open(CURRENCY_RATES_FILE) as json_file:
        data = json.load(json_file)
    if round(data['rates']['RUB'], 2) == round(data_to_save['rates']['RUB'], 2):
        return False
    else:
        with open(CURRENCY_RATES_FILE, "w") as json_file:
            json.dump(data_to_save, json_file)
    return True


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Привет, Павел!")
    markup.add(btn1)
    bot.send_message(message.from_user.id, "👋 Привет! Я бот, меня зовут Павел_спекулянт!", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message, time_operation=None):
    if message.text == '👋 Привет, Павел!':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
        btn1 = types.KeyboardButton('Доллар')
        btn2 = types.KeyboardButton('Евро')
        btn3 = types.KeyboardButton('Выход')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, 'Выберите курс валюты или нажмите выход',
                         reply_markup=markup)  # ответ бота

    elif message.text == 'Доллар':
        data = get_currency_rate("USD")
        if save_to_json(data):
            bot.send_message(message.from_user.id, f"За 1 доллар сейчас дают {round(data['rates']['RUB'], 2)}р.", parse_mode='Markdown')
        else:
            bot.send_message(message.from_user.id, f"Курс не изменился")

    elif message.text == 'Евро':
        data = get_currency_rate("EUR")
        if save_to_json(data):
            bot.send_message(message.from_user.id, f"За 1 евро сейчас дают {round(data['rates']['RUB'], 2)}р.", parse_mode='Markdown')
        else:
            bot.send_message(message.from_user.id, f"Курс не изменился")

    elif message.text == "Выход":
        bot.send_message(message.from_user.id, "Разваливаюсь... Начните писать что-нибудь, чтобы добить меня",
                         parse_mode='Markdown')
        bot.stop_bot()


bot.polling(none_stop=True, interval=0)  # обязательная для работы бота часть
