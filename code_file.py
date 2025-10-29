import telebot
from telebot import types
import requests

weather_api_key = '2cc213560a984e94aa274022251109'

bot = telebot.TeleBot('8254669891:AAE7ePtIM_oc9VTWcdRNtbFehEO8zV4SoPo')

user_states = {}  # user_states[user_id] = 'waiting_for_city'

def menu(message, first_time=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('⚡ О боте ⚡')
    btn2 = types.KeyboardButton('☀️ Узнать погоду на завтра ☀️')
    btn3 = types.KeyboardButton('↩️ Выход ↩️')
    markup.row(btn1)
    markup.row(btn2,btn3)

    if first_time:
        bot.send_message(
            message.chat.id,
            f'Привет, {message.from_user.first_name}! Я могу:\n'
            '1. Рассказать о себе\n'
            '2. Узнать погоду в любом городе на завтра 🌤'
            '3. Выйти из приложения',
            parse_mode='Markdown'
        )

    bot.send_message(
        message.chat.id,
        "Выберите действие:",
        reply_markup=markup
    )



@bot.message_handler(commands=['start', 'hello', 'Привет'])
def start(message):
    user_states[message.from_user.id] = None  # сброс состояния
    menu(message, first_time=True)


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_states.get(user_id) == 'waiting_for_city':
        if text == '🔙 Вернуться в меню':
            user_states[user_id] = None
            menu(message)
        else:
            get_city_and_show_weather(message)
        return

    # Обработка кнопок меню
    if text == '⚡ О боте ⚡':
        about_bot(message)
    elif text == '☀️ Узнать погоду на завтра ☀️':
        ask_for_city(message)
    elif text=='↩️ Выход ↩️':
        exit_bot(message)
    elif text == '🔙 Вернуться в меню':
        user_states[user_id] = None
        menu(message,first_time=False)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки ниже.", reply_markup=get_menu_markup())


def about_bot(message):
    bot.send_message(
        message.chat.id,
        f'Бот создан, чтобы узнавать погоду для вас и ваших близких 🌹\n'
        'Просто выберите "Узнать погоду" и введите название города — я скажу, какая будет погода завтра!'
    )
    menu(message)


def ask_for_city(message):
    user_states[message.from_user.id] = 'waiting_for_city'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('🔙 Вернуться в меню')
    markup.add(btn)
    bot.send_message(
        message.chat.id,
        '🌆 Введите название города (например, Москва, Лондон, Токио):',
        reply_markup=markup
    )


def get_city_and_show_weather(message):
    city = message.text.strip()
    user_id = message.from_user.id

    if not city or city == '🔙 Вернуться в меню':
        bot.send_message(message.chat.id, "Название города не может быть пустым. Попробуйте снова:")
        return

    url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        'key': weather_api_key,
        'q': city,
        'days': 2,
        'lang': 'ru',
        'aq': 'no'
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200:
            error_msg = data.get('error', {}).get('message', 'Неизвестная ошибка')
            bot.send_message(message.chat.id, f"❌ Ошибка: {error_msg}")
            menu(message,first_time=False)
            return

        forecast = data['forecast']['forecastday'][1]
        day = forecast['day']
        location = data['location']['name']
        country = data['location']['country']

        avg_temp = day['avgtemp_c']
        max_temp = day['maxtemp_c']
        min_temp = day['mintemp_c']
        condition = day['condition']['text']
        chance_of_rain = day['daily_chance_of_rain']
        humidity = day['avghumidity']

        emoji = ("🌤" if "ясно" in condition.lower() else
                 "🌧" if "дождь" in condition.lower() or "ливень" in condition.lower() else
                 "☁️" if "облачно" in condition.lower() else "🌨")

        weather_msg = (
            f"{emoji} **Погода в {location}, {country} на завтра:**\n\n"
            f"🌡 Средняя температура: {avg_temp}°C\n"
            f"📈 Максимум: {max_temp}°C | Минимум: {min_temp}°C\n"
            f"💧 Влажность: {humidity}%\n"
            f"☔ Вероятность дождя: {chance_of_rain}%\n"
            f"📝 Условия: {condition.capitalize()}"
        )

        bot.send_message(message.chat.id, weather_msg, parse_mode='Markdown')

    except requests.exceptions.RequestException:
        bot.send_message(message.chat.id, "⚠️ Ошибка подключения к сервису погоды.")
    except KeyError:
        bot.send_message(message.chat.id, "❌ Не удалось найти данные о погоде. Проверьте название города.")
    finally:
        user_states[user_id] = None
        menu(message, first_time=False)


def get_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('🔙 Вернуться в меню'))
    return markup

@bot.message_handler(commands=['exit', 'stop', 'end'])
def exit_bot(message):
    user_id = message.from_user.id
    user_states[user_id] = None
    remove_markup = types.ReplyKeyboardRemove()  # убирает клавиатуру
    bot.send_message(
        message.chat.id,
        f"До новых встреч, {message.from_user.first_name}!\n"
        "Для возобновления работы нажмите /start",
        reply_markup=remove_markup
    )


bot.polling(non_stop=True)
