import telebot
import os
import sys

# Настройки из Secrets
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(TOKEN)

# Список стоп-слов
SPAM_KEYWORDS = [
    "крипта", "инвестиции", "заработок", "выплаты", 
    "подпишись", "казино", "crypto", "invest", "М Р Э О", "trading"
]

def clean_chat():
    print(f"--- Запуск очистки чата {CHAT_ID} ---")
    
    try:
        # 1. Получаем обновления. 
        # offset=-1 заставляет Telegram отдать последние сообщения, даже если они "прочитаны"
        updates = bot.get_updates(limit=100, timeout=10, offset=-100)
        
        if not updates:
            print("Новых сообщений в очереди не найдено.")
            return

        print(f"Получено сообщений для анализа: {len(updates)}")
        
        for update in updates:
            if not update.message:
                continue
                
            msg = update.message
            user = msg.from_user

            # Проверяем, что сообщение из нашей группы
            if str(msg.chat.id) != str(CHAT_ID):
                continue

            # Логика удаления ботов
            if user.is_bot and user.username != bot.get_me().username:
                print(f"Удаляю бота: @{user.username}")
                try:
                    bot.ban_chat_member(CHAT_ID, user.id)
                    bot.delete_message(CHAT_ID, msg.message_id)
                except: pass
                continue

            # Логика удаления по ключевым словам
            if msg.text:
                text_lower = msg.text.lower()
                if any(word in text_lower for word in SPAM_KEYWORDS):
                    print(f"Удаляю спам от {user.first_name}: {msg.text[:20]}...")
                    try:
                        bot.delete_message(CHAT_ID, msg.message_id)
                    except Exception as e:
                        print(f"Не удалось удалить: {e}")

        print("--- Очистка завершена ---")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("Ошибка: Проверьте токены в Secrets!")
        sys.exit(1)
    clean_chat()
