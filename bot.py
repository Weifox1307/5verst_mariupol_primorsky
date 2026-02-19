import telebot
import os
import sys

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(TOKEN)

# Расширенный список слов для твоего чата
SPAM_KEYWORDS = [
    "крипта", "инвестиции", "заработок", "выплаты", 
    "подпишись", "казино", "crypto", "invest", "trading",
    "мрэо", "водительское", "автошколы", "официально", "документация"
]

def clean_chat():
    print(f"--- Запуск очистки чата {CHAT_ID} ---")
    try:
        # Берем историю последних сообщений
        updates = bot.get_updates(limit=100, timeout=10, offset=-100)
        
        if not updates:
            print("Новых сообщений не найдено.")
            return

        for update in updates:
            if not update.message:
                continue
                
            msg = update.message
            user = msg.from_user

            if str(msg.chat.id) != str(CHAT_ID):
                continue

            # Удаление других ботов
            if user.is_bot and user.username != bot.get_me().username:
                try:
                    bot.ban_chat_member(CHAT_ID, user.id)
                    bot.delete_message(CHAT_ID, msg.message_id)
                except: pass
                continue

            # Удаление по ключевым словам
            if msg.text:
                text_lower = msg.text.lower()
                if any(word in text_lower for word in SPAM_KEYWORDS):
                    try:
                        bot.delete_message(CHAT_ID, msg.message_id)
                        print(f"Удалено спам-сообщение от {user.first_name}")
                    except Exception as e:
                        # Если сообщение уже удалено, просто игнорируем ошибку
                        if "message to delete not found" not in str(e):
                            print(f"Ошибка при удалении: {e}")

        print("--- Очистка завершена ---")

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        sys.exit(1)
    clean_chat()
