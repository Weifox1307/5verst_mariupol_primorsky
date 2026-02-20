import telebot
import os
import sys
import re

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(TOKEN)

# Группируем подозрительные слова по категориям
MARKERS = {
    "money": ["выплат", "деньги", "карт", "сбер", "доход", "заработ", "₽"],
    "action": ["жми", "переходи", "оформляй", "забирай", "подпишись"],
    "job": ["комплектовщик", "склад", "вакансия", "зп", "подработка"],
    "spam_bots": ["@sberbank", "bot"]
}

def is_spam(text):
    text = text.lower()
    score = 0
    
    # 1. Считаем "вес" сообщения
    if any(word in text for word in MARKERS["money"]): score += 2
    if any(word in text for word in MARKERS["action"]): score += 1
    if any(word in text for word in MARKERS["job"]): score += 2
    if any(word in text for word in MARKERS["spam_bots"]): score += 2
    
    # 2. Если есть ссылки (http или @username) - добавляем вес
    if re.search(r'http|@\w+', text): score += 2
    
    # 3. Если много эмодзи (признак спама)
    emoji_count = len(re.findall(r'[^\w\s,.]', text))
    if emoji_count > 5: score += 1

    # Вердикт: если набрано 3 и более баллов - это спам
    return score >= 3

def clean_chat():
    print(f"--- Запуск очистки чата {CHAT_ID} ---")
    try:
        updates = bot.get_updates(limit=100, timeout=10, offset=-100)
        if not updates: return

        for update in updates:
            if not update.message: continue
            msg = update.message
            user = msg.from_user

            if str(msg.chat.id) != str(CHAT_ID): continue

            # Удаляем чужих ботов всегда
            if user.is_bot and user.username != bot.get_me().username:
                try:
                    bot.ban_chat_member(CHAT_ID, user.id)
                    bot.delete_message(CHAT_ID, msg.message_id)
                except: pass
                continue

            # Проверка текста по "умному" фильтру
            if msg.text:
                if is_spam(msg.text):
                    print(f"Удаляю спам (score >= 3) от {user.first_name}")
                    try:
                        bot.delete_message(CHAT_ID, msg.message_id)
                    except Exception as e:
                        if "message to delete not found" not in str(e):
                            print(f"Ошибка: {e}")

        print("--- Очистка завершена ---")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if TOKEN and CHAT_ID: clean_chat()
