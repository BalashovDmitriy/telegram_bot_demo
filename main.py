import telebot
import requests
import json

from os import getenv
from googleapiclient.discovery import build

CURRENCY_RATES_FILE = "currency_rates.json"

TELEGRAM_API_KEY = getenv('PAVEL_TELEGRAM_API_KEY')
APILAYER_API_KEY = getenv('APILAYER_API_KEY')
FINNHUB_API_KEY = getenv('FINNHUB_API_KEY')
YT_API_KEY = getenv('GOOGLE_API_KEY')

bot = telebot.TeleBot(TELEGRAM_API_KEY)


def get_currency_rate(currency: str) -> dict:
    """Получает курс валюты от API и возвращает его в виде float"""

    url = f"https://api.apilayer.com/exchangerates_data/latest?base={currency}"
    response = requests.get(url, headers={'apikey': APILAYER_API_KEY})
    response_data = json.loads(response.text)
    return response_data


def get_crypro_price(crypto: str) -> str:
    params = {
        'symbol': f'BINANCE:{crypto}',
        'resolution': 1,
        'token': FINNHUB_API_KEY
    }
    url = "https://finnhub.io/api/v1/crypto/candle"
    response = requests.get(url, params=params)
    data_candles = json.loads(response.text)
    return data_candles['c'][-1]


def get_youtube_service() -> build:
    """Создает и возвращает объект YouTube API service, используя ключ API из переменной окружения."""
    youtube = build('youtube', 'v3', developerKey=YT_API_KEY)
    return youtube


def get_search_results(query: str) -> list[dict]:
    """Выполняет поиск видео в YouTube по заданному запросу и возвращает список видео."""

    youtube = get_youtube_service()
    search_response = youtube.search().list(
        q=query,
        type='video',
        part='id,snippet',
        maxResults=5
    ).execute()

    videos = []
    for search_result in search_response.get('items', []):
        video_id = search_result['id']['videoId']
        video_info = youtube.videos().list(
            id=video_id,
            part='snippet,statistics'
        ).execute()

        video = {
            'video_id': video_id,
            'title': video_info['items'][0]['snippet']['title'],
            'channel_title': video_info['items'][0]['snippet']['channelTitle'],
            'view_count': int(video_info['items'][0]['statistics']['viewCount']),
            'like_count': int(video_info['items'][0]['statistics']['likeCount'])
        }
        videos.append(video)

    return videos


def format_video_info(video_info: dict) -> dict:
    """Форматирует информацию о видео для вывода в консоль и возвращает словарь со всей информацией о видео."""

    formatted_video_info = {
        'title': f"{video_info['title'][:35]}..." if len(video_info['title']) > 35 else video_info['title'],
        'view_count': video_info['view_count'],
        'like_count': video_info['like_count'],
        'ratio': f"{round(video_info['ratio'] * 100, 1)} %",
        'url': f"<https://www.youtube.com/watch?v={video_info['video_id']}>"
    }
    return formatted_video_info


def print_video_info(video_info: dict) -> str:
    """Печатает информацию о видео в консоль в виде строки таблицы."""
    return f"Количество просмотров: {video_info['view_count']:<10}\n" \
           f"Лайков: {video_info['like_count']:<6}\n" \
           f"Рейтинг: {video_info['ratio']:<7}\n" \
           f"Ссылка: {video_info['url']:<35}\n"


# def save_to_json(data_to_save: dict):
#     """Сохраняет данные в JSON-файл"""
#     with open(CURRENCY_RATES_FILE) as json_file:
#         data = json.load(json_file)
#     if round(data['rates']['RUB'], 2) == round(data_to_save['rates']['RUB'], 2):
#         return False
#     else:
#         with open(CURRENCY_RATES_FILE, "w") as json_file:
#             json.dump(data_to_save, json_file)
#     return True
#

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
    if message.text == '👋 Поздороваться с Павлом' or message.text == 'В меню' or message.text == 'назад':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = telebot.types.KeyboardButton('Валюты')
        btn2 = telebot.types.KeyboardButton('Криптовалюты')
        btn3 = telebot.types.KeyboardButton('Youtube')
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, '<b>Выберите интересующий вас раздел</b>',
                         reply_markup=markup, parse_mode='html')
    elif message.text in ['Валюты', 'Криптовалюты', 'Youtube']:
        commands(message)
    elif message.text == 'Доллар':
        data = get_currency_rate("USD")
        bot.send_message(message.from_user.id, f"За 1 доллар сейчас дают {round(data['rates']['RUB'], 2)}р.")
    elif message.text == 'Евро':
        data = get_currency_rate("EUR")
        bot.send_message(message.from_user.id, f"За 1 евро сейчас дают {round(data['rates']['RUB'], 2)}р.")
    elif message.text == 'Фунт стерлингов':
        data = get_currency_rate("GBP")
        bot.send_message(message.from_user.id, f"За 1 фунт стерлингов сейчас дают {round(data['rates']['RUB'], 2)}р.")
    elif message.text == 'Bitcoin':
        data = get_crypro_price("BTCUSDT")
        bot.send_message(message.from_user.id, f"За 1 BTC сейчас дают {data} USDT")
    elif message.text == 'Etherium':
        data = get_crypro_price("ETHUSDT")
        bot.send_message(message.from_user.id, f"За 1 ETH сейчас дают {data} USDT")
    elif message.text == 'Litecoin':
        data = get_crypro_price("LTCUSDT")
        bot.send_message(message.from_user.id, f"За 1 LTC сейчас дают {data} USDT")
    else:
        videos = get_search_results(message.text)
        for video in videos:
            video.update({'ratio': video['like_count'] / video['view_count']})
        video_stats_sorted = sorted(videos, key=lambda x: x['ratio'], reverse=True)
        for i in range(5):
            video_info = format_video_info(video_stats_sorted[i])
            bot.send_message(message.from_user.id, print_video_info(video_info))
        bot.send_message(message.from_user.id, "Введите новый поисковый запрос. Введите 'назад'"
                                               " для выхода из режима запросов к youtube")


def commands(message):
    if message.text == "Валюты":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = telebot.types.KeyboardButton('Доллар')
        btn2 = telebot.types.KeyboardButton('Евро')
        btn3 = telebot.types.KeyboardButton('Фунт стерлингов')
        btn4 = telebot.types.KeyboardButton('В меню')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.from_user.id, '<b>Выберите валюту</b>',
                         reply_markup=markup, parse_mode='html')
    elif message.text == "Криптовалюты":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        btn1 = telebot.types.KeyboardButton('Bitcoin')
        btn2 = telebot.types.KeyboardButton('Etherium')
        btn3 = telebot.types.KeyboardButton('Litecoin')
        btn4 = telebot.types.KeyboardButton('В меню')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.from_user.id, '<b>Выберите криптовалюту</b>',
                         reply_markup=markup, parse_mode='html')
    elif message.text == "Youtube":
        bot.send_message(message.from_user.id, '<b>Введите поисковый запрос в строке</b>', parse_mode='html')
        bot.send_message(message.from_user.id, '<b>Будет выведено 5 релевантных ответов</b>', parse_mode='html')
        bot.send_message(message.from_user.id, '<b>Каждое видео со своим количеством просмотров,'
                                               'количеством лайков, и рейтингом </b>', parse_mode='html')


bot.polling(none_stop=True, timeout=0)  # обязательная для работы бота часть
