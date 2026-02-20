import telebot
import os
import sys
import re

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(TOKEN)

# Самые жесткие маркеры из твоего примера
HARD_STOP_WORDS = [
    "sberbank", "сбербанк", "выплата", "заявка онлайн", 
    "зимней поддержки", "карта cбербанка", "@sberbank",
    "комплектовщики", "склад", "ночные"
]

def clean_text(text):
    if not text: return ""
    # Убираем лишние символы, невидимые пробелы и приводим к нижнему регистру
    return re.sub(r'[^\w\s]', '', text).lower().strip()

def is_spam(msg):
    # Проверяем и текст, и описание к фото/видео
    content = msg.text or msg.caption or ""
    if not content: return False
    
    text_normal = content.lower()
    text_no_signs = clean_text(content)
    
    # 1. Проверка на жесткие стоп-слова
    for word in HARD_STOP_WORDS:
        if word in text_normal or word in text_no_signs:
            return True
            
    # 2. Умный фильтр (баллы)
    score = 0
    if any(w in text_normal for w in ["₽", "выплат", "карт", "деньги", "сбер"]): score += 2
    if any(w in text_normal for w in ["жми", "переходи", "оформляй", "забирай"]): score += 2
    if re.search(r'http|@\w+|t\.me', text_normal): score += 2
    if len(re.findall(r'[^\w\s,.]', content)) > 10: score += 1 # Много эмодзи
    
    return score >= 3

def clean_chat():
    print(f"--- Глубокая очистка чата {CHAT_ID} ---")
    try:
        # Берем последние 100 событий
        updates = bot.get_updates(limit=100, timeout=10, offset=-100)
        if not updates:
            print("Новых обновлений нет.")
            return

        for update in updates:
            msg = update.message
            if not msg or str(msg.chat.id) != str(CHAT_ID):
                continue

            user = msg.from_user
            
            # Игнорируем себя
            if user.username == bot.get_me().username:
                continue

            # Удаляем ботов (кроме себя)
            if user.is_bot:
                try:
                    bot.ban_chat_member(CHAT_ID, user.id)
                    bot.delete_message(CHAT_ID, msg.message_id)
                    print(f"Забанен бот: @{user.username}")
                except: pass
                continue

            # Проверка контента
            if is_spam(msg):
                print(f"Удаляю спам от {user.first_name} (ID: {msg.message_id})")
                try:
                    bot.delete_message(CHAT_ID, msg.message_id)
                except Exception as e:
                    if "message to delete not found" not in str(e):
                        print(f"Ошибка удаления: {e}")

        print("--- Очистка завершена ---")
    except Exception as e:
        print(f"Ошибка в основном цикле: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if TOKEN and CHAT_ID:
        clean_chat()
