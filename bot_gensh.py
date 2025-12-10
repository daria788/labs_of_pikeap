import telebot
import json
from telebot import types

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

bot = telebot.TeleBot('83')
characters = config["characters"]
aliases = config["aliases"]

user_states = {}

def menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('⚡ О боте ⚡')
    btn2 = types.KeyboardButton('Артефакты персонажей')
    btn3 = types.KeyboardButton('↩️ Выход ↩️')
    markup.row(btn1)
    markup.row(btn2, btn3)
    return markup

def back_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('🔙 Вернуться в меню')
    markup.add(btn)
    return markup

@bot.message_handler(commands=['start', 'hello'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        f'Привет, {message.from_user.first_name}! 👋\n'
        'Я могу:\n'
        '1. Рассказать о себе\n'
        '2. Показать сборку артефактов для персонажа\n'
        '3. Выйти из приложения',
        reply_markup=menu()
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_states.get(user_id) == 'waiting_for_character':
        if text == '🔙 Вернуться в меню':
            user_states[user_id] = None
            bot.send_message(message.chat.id, "Возврат в меню", reply_markup=menu())
        else:
            show_character_build(message, text)  
        return

    if text == '⚡ О боте ⚡':
        about_bot(message)
    elif text == 'Артефакты персонажей':
        ask_for_character(message)
    elif text == '↩️ Выход ↩️':
        bot.send_message(message.chat.id, "До новых встреч! 👋", reply_markup=types.ReplyKeyboardRemove())
    elif text == '🔙 Вернуться в меню':
        user_states[user_id] = None
        bot.send_message(message.chat.id, "Возврат в меню", reply_markup=menu())
    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки меню.", reply_markup=menu())

def about_bot(message):
    bot.send_message(
        message.chat.id,
        "🤖 Бот создан, чтобы помочь вам собрать персонажей для комфортной игры в Genshin Impact.\n\n"
        "Данные взяты с https://genshin.gg/builds/",
        reply_markup=menu()
    )

def ask_for_character(message):
    user_id = message.from_user.id
    user_states[user_id] = 'waiting_for_character'
    bot.send_message(
        message.chat.id,
        "Введите имя персонажа (например: *Аяка*, *Hu Tao*, *Сяо*):",
        parse_mode="Markdown",
        reply_markup=back_menu_markup()
    )

def show_character_build(message, query):
    user_id = message.from_user.id
    q = query.lower().strip()

    key = None
    if q in characters:
        key = q
    elif q in aliases:
        key = aliases[q]
    else:
        for k, v in characters.items():
            if q == v["name_en"].lower() or q == v["name_ru"].lower():
                key = k
                break

    if key and key in characters:
        c = characters[key]
        if isinstance(c['artifact_set'], list):
            artifact_line = " + ".join(c['artifact_set'])
            pieces_line = f"{c['pieces'][0]} + {c['pieces'][1]}"
        else:
            artifact_line = c['artifact_set']
            pieces_line = str(c['pieces'])

        reply = (
            f"✨ *{c['name_en']}* ({c['name_ru']}) — _{c['role']}_\n\n"
            f"⚔️ *Оружие*: {c['weapon']}\n"
            f"🛡️ *Сет*: {artifact_line} ({pieces_line} шт.)\n\n"
            f"🔮 *Статы*:\n"
            f"• Пески: {c['sands']}\n"
            f"• Кубок: {c['goblet']}\n"
            f"• Тиара: {c['circlet']}"
        )
        bot.send_message(message.chat.id, reply, parse_mode="Markdown", reply_markup=back_menu_markup())
    else:
        bot.send_message(
            message.chat.id,
            "❌ Персонаж не найден.\nПопробуйте: *Аяка*, *Ху Тао*, *Сяо*, *Беннет*, *Кли* и т.д.",
            parse_mode="Markdown",
            reply_markup=back_menu_markup()
        )

if __name__ == "__main__":
    print("✅ Бот запущен!")

    bot.polling(none_stop=True)
