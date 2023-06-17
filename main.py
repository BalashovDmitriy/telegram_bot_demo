import telebot
import requests
import json

from os import getenv

CURRENCY_RATES_FILE = "currency_rates.json"

TELEGRAM_API_KEY = getenv('PAVEL_TELEGRAM_API_KEY')
API_KEY = getenv('APILAYER_API_KEY')

bot = telebot.TeleBot(TELEGRAM_API_KEY)


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
def start(message) -> None:
    """
    Приветствие бота
    :param message: объект message
    :return: None
    """
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton("👋 Поздороваться с Павлом")
    markup.add(btn1)
    bot.send_message(message.from_user.id, f"👋Привет <b>{message.from_user.first_name}</b>! Меня зовут Павел👋 \n "
                                           f"Я бот.Нажмите кнопку снизу чтобы поздороваться со "
                                           f"мной", reply_markup=markup, parse_mode='html')


@bot.message_handler(content_types=['text'])
def get_text_messages(message) -> None:
    """
    Основные разделы для работы
    :param message: объект message
    :return: None
    """
    if message.text == '👋 Поздороваться с Павлом' or message.text == 'Назад':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = telebot.types.KeyboardButton('Валюты')
        btn2 = telebot.types.KeyboardButton('Акции')
        btn3 = telebot.types.KeyboardButton('Youtube')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, '<b>Выберите интересующий вас раздел</b>',
                         reply_markup=markup, parse_mode='html')
    elif message.text in ['Валюты', 'Акции', 'Youtube']:
        commands(message)
    elif message.text == 'Доллар':
        print("работает")
        data = get_currency_rate("USD")
        bot.send_message(message.from_user.id, f"За 1 доллар сейчас дают {round(data['rates']['RUB'], 2)}р.")
    elif message.text == 'Евро':
        data = get_currency_rate("EUR")
        bot.send_message(message.from_user.id, f"За 1 евро сейчас дают {round(data['rates']['RUB'], 2)}р.")
    elif message.text == 'Фунт стерлингов':
        data = get_currency_rate("GBP")
        bot.send_message(message.from_user.id, f"За 1 фунт стерлингов сейчас дают {round(data['rates']['RUB'], 2)}р.")
    elif message.text == '':
        pass


def commands(message):
    if message.text == "Валюты":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = telebot.types.KeyboardButton('Доллар')
        btn2 = telebot.types.KeyboardButton('Евро')
        btn3 = telebot.types.KeyboardButton('Фунт стерлингов')
        btn4 = telebot.types.KeyboardButton('Назад')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.from_user.id, '<b>Выберите валюту</b>',
                         reply_markup=markup, parse_mode='html')
    elif message.text == "Акции":
        bot.send_message(message.from_user.id, 'Функция для работы с акциями')
    elif message.text == "Youtube":
        bot.send_message(message.from_user.id, 'Функция для работы с Youtube')


def currency(message):


    # elif message.text == 'Доллар':
    #     data = get_currency_rate("USD")
    #     if save_to_json(data):
    #         bot.send_message(message.from_user.id, f"За 1 доллар сейчас дают {round(data['rates']['RUB'], 2)}р.",
    #                          parse_mode='Markdown')
    #     else:
    #         bot.send_message(message.from_user.id, f"Курс не изменился")
    #
    # elif message.text == 'Евро':
    #     data = get_currency_rate("EUR")
    #     if save_to_json(data):
    #         bot.send_message(message.from_user.id, f"За 1 евро сейчас дают {round(data['rates']['RUB'], 2)}р.",
    #                          parse_mode='Markdown')
    #     else:
    #         bot.send_message(message.from_user.id, f"Курс не изменился")
    #
    # elif message.text == "Выход":
    #     bot.send_message(message.from_user.id, "Разваливаюсь... Начните писать что-нибудь, чтобы добить меня",
    #                      parse_mode='Markdown')
    #     bot.stop_bot()


bot.polling(none_stop=True)  # обязательная для работы бота часть
