import telebot
import os
import sys

# Получаем настройки из Secrets репозитория GitHub
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(TOKEN)

# Список запрещенных слов (можешь дополнить своими)
SPAM_KEYWORDS = [
    "крипта", "инвестиции", "заработок", "выплаты", 
    "подпишись", "казино", "crypto", "invest", "trading"
]

def clean_chat():
    print(f"--- Запуск очистки чата {CHAT_ID} ---")
    
    try:
        # Получаем последние обновления
        updates = bot.get_updates(timeout=10, allowed_updates=["message"])
        
        for update in updates:
            if not update.message:
                continue
                
            msg = update.message
            user = msg.from_user

            # Проверяем, что это сообщение из нужной нам группы
            if str(msg.chat.id) != str(CHAT_ID):
                continue

            # 1. Удаляем сторонних ботов (кроме самого себя)
            if user.is_bot and user.username != bot.get_me().username:
                print(f"found: бот-спамер @{user.username}. Удаляю...")
                try:
                    bot.ban_chat_member(CHAT_ID, user.id)
                    bot.delete_message(CHAT_ID, msg.message_id)
                except Exception as e:
                    print(f"Error banning bot: {e}")
                continue

            # 2. Проверка текста на спам-фильтр
            if msg.text:
                text_lower = msg.text.lower()
                if any(word in text_lower for word in SPAM_KEYWORDS):
                    print(f"found: спам от {user.first_name}. Удаляю сообщение...")
                    try:
                        bot.delete_message(CHAT_ID, msg.message_id)
                        # Если хочешь сразу банить людей за спам, раскомментируй строку ниже:
                        # bot.ban_chat_member(CHAT_ID, user.id)
                    except Exception as e:
                        print(f"Error deleting message: {e}")

        print("--- Очистка завершена успешно ---")

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("ОШИБКА: Не заданы TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID в Secrets!")
        sys.exit(1)
    clean_chat()
