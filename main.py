import time
import sqlite3
import telebot
from data.config import BOT_TOKEN, ADMIN_ID, API_KEY, MODEL1, MODEL2, LOG_FILE_PATH, MAX_MESSAGE_LENGTH, DB_PATH
from mistralai import Mistral

bot = telebot.TeleBot(BOT_TOKEN)
client = Mistral(api_key=API_KEY)
user_model_selection = {}
last_request_time = {}
user_context = {}

def log_error(error_message):
    try:
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {error_message}\n")
    except Exception as e:
        print(f"Ошибка записи в файл журнала: {e}")

def initialize_database():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)''')
        conn.commit()
    except Exception as e:
        log_error(f"Ошибка инициализации базы данных: {e}")
    finally:
        conn.close()

def save_user_id(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO users (id) VALUES (?)", (user_id,))
        conn.commit()
    except Exception as e:
        log_error(f"Ошибка сохранения идентификатора пользователя: {e}")
    finally:
        conn.close()

def get_user_count():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        return count
    except Exception as e:
        log_error(f"Ошибка получения количества пользователей: {e}")
        return 0
    finally:
        conn.close()

def update_model_buttons(chat_id, message_id, selected_model):
    markup = telebot.types.InlineKeyboardMarkup()

    button1_text = "✅ GPT v1" if selected_model == MODEL1 else "GPT v1"
    button2_text = "✅ GPT v2" if selected_model == MODEL2 else "GPT v2"

    button1 = telebot.types.InlineKeyboardButton(text=button1_text, callback_data="GPT v1")
    button2 = telebot.types.InlineKeyboardButton(text=button2_text, callback_data="GPT v2")

    markup.add(button1, button2)

    bot.edit_message_reply_markup(chat_id, message_id, reply_markup=markup)

@bot.message_handler(commands=['start'])
def start_message(message):
    save_user_id(message.chat.id)
    bot.send_message(message.chat.id, "👋 Здравствуйте!\nПросто отправьте сообщение, и вы получите ответ на него!\n\nОтправьте /help для получения справки.")

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "✨ <b>Мои команды</b>\n\n/start - перезапуск\n/img - генерация изображений\n/mode - выбор модели\n/reset - сбросить контекст\n/help - справка", parse_mode='HTML')

@bot.message_handler(commands=['mode'])
def model_command(message):
    selected_model = user_model_selection.get(message.chat.id, MODEL1)

    markup = telebot.types.InlineKeyboardMarkup()
    button1_text = "✅ GPT v1" if selected_model == MODEL1 else "GPT v1"
    button2_text = "✅ GPT v2" if selected_model == MODEL2 else "GPT v2"

    button1 = telebot.types.InlineKeyboardButton(text=button1_text, callback_data="GPT v1")
    button2 = telebot.types.InlineKeyboardButton(text=button2_text, callback_data="GPT v2")
    markup.add(button1, button2)

    bot.send_message(message.chat.id, "Выберите модель:", reply_markup=markup)
    if message.chat.id not in user_model_selection:
        user_model_selection[message.chat.id] = MODEL1

@bot.callback_query_handler(func=lambda call: call.data in ['GPT v1', 'GPT v2'])
def handle_model_selection(call):
    chat_id = call.message.chat.id
    current_model = user_model_selection.get(chat_id, MODEL1)

    if (call.data == 'GPT v1' and current_model == MODEL1) or (call.data == 'GPT v2' and current_model == MODEL2):
        bot.answer_callback_query(call.id, text="Эта модель уже выбрана")
        return

    if call.data == 'GPT v1':
        user_model_selection[chat_id] = MODEL1
    elif call.data == 'GPT v2':
        user_model_selection[chat_id] = MODEL2

    update_model_buttons(chat_id, call.message.message_id, user_model_selection[chat_id])

@bot.message_handler(commands=['reset'])
def reset_context(message):
    user_context[message.chat.id] = []
    bot.send_message(message.chat.id, "✨ Контекст был сброшен.")

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id == ADMIN_ID:
        markup = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")
        markup.add(button)
        bot.send_message(message.chat.id, "Админ-панель", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У вас нет доступа к этой команде.")

@bot.callback_query_handler(func=lambda call: call.data == "statistics")
def handle_statistics(call):
    if call.from_user.id == ADMIN_ID:
        try:
            user_count = get_user_count()
            bot.send_message(call.message.chat.id, f"✨ Всего пользователей: {user_count}")
        except Exception as e:
            log_error(f"Ошибка при получении статистики: {e}")

@bot.message_handler(func=lambda message: True)
def handle_user_request(message):
    model = user_model_selection.get(message.chat.id, MODEL1)

    chat_id = message.chat.id
    current_time = time.time()

    if chat_id in last_request_time:
        time_since_last_request = current_time - last_request_time[chat_id]
        if time_since_last_request < 1:
            time_to_wait = 1 - time_since_last_request
            time.sleep(time_to_wait)

    try:
        user_messages = user_context.get(chat_id, [])
        
        system_message = {"role": "system", "content": "Используй форматирование текста markdown для Telegram."}
        if not any(msg["role"] == "system" and msg["content"] == system_message["content"] for msg in user_messages):
            user_messages.insert(0, system_message)

        user_messages.append({"role": "user", "content": message.text})
        
        waiting_message = bot.send_message(chat_id, "⏳ Ожидайте. Обрабатываю ваш запрос...")

        response = client.chat.complete(
            model=model,
            messages=user_messages
        )
        output_text = response.choices[0].message.content
        
        parts = [output_text[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(output_text), MAX_MESSAGE_LENGTH)]
        bot.edit_message_text(parts[0], chat_id, waiting_message.message_id, parse_mode='markdown')

        for part in parts[1:]:
            bot.send_message(chat_id, part)

        user_messages.append({"role": "assistant", "content": output_text})
        user_context[chat_id] = user_messages

    except Exception as e:
        log_error(f"Ошибка обработки запроса пользователя: {e}")

    last_request_time[chat_id] = time.time()


if __name__ == '__main__':
    initialize_database()
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            log_error(f"Ошибка запуска: {e}")
            time.sleep(15)