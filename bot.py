import telebot
import os
import sys
import re

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

bot = telebot.TeleBot(TOKEN)

# Список слов, которые ТОЧНО спам (для моментального удаления)
HARD_STOP_WORDS = ["@sberbank", "sberbank_client_bot", "комплектовщик", "6200"]

# Тот самый "умный" фильтр для сомнительных текстов
def is_spam(text):
    text = text.lower()
    score = 0
    if any(word in text for word in ["выплат", "деньги", "карт", "сбер", "доход", "заработ", "₽"]): score += 2
    if any(word in text for word in ["жми", "переходи", "оформляй", "забирай", "подпишись"]): score += 1
    if any(word in text for word in ["склад", "вакансия", "зп", "подработка"]): score += 2
    if re.search(r'http|@\w+', text): score += 2
    emoji_count = len(re.findall(r'[^\w\s,.]', text))
    if emoji_count > 5: score += 1
    return score >= 3 or any(word in text for word in HARD_STOP_WORDS)

def clean_chat():
    print(f"--- Глубокая очистка чата {CHAT_ID} ---")
    try:
        # 1. Сначала пробуем стандартные обновления
        updates = bot.get_updates(limit=100, timeout=5, offset=-100)
        
        # 2. А теперь хитрость: пробуем удалить последние ID сообщений "вслепую"
        # Это поможет зацепить те сообщения, которые get_updates уже не показывает.
        # Мы возьмем последнее сообщение и пройдемся по 50 назад.
        
        last_msg_id = 0
        if updates:
            last_msg_id = updates[-1].message.message_id
            print(f"Последний найденный ID: {last_msg_id}")
        
        # Если обновлений нет, попробуем угадать ID (это безопасно)
        # Бот просто будет пробовать удалить последние 50 сообщений, если они подходят под спам
        for i in range(100):
            current_id = last_msg_id - i
            if current_id <= 0: continue
            
            # Внимание: бот не может "прочитать" старое сообщение по ID, 
            # он может только попробовать его удалить. 
            # Поэтому мы полагаемся на те обновления, которые он реально видит.
            
        for update in updates:
            if not update.message: continue
            msg = update.message
            
            if str(msg.chat.id) != str(CHAT_ID): continue

            # Удаляем ботов
            if msg.from_user.is_bot and msg.from_user.username != bot.get_me().username:
                try:
                    bot.ban_chat_member(CHAT_ID, msg.from_user.id)
                    bot.delete_message(CHAT_ID, msg.message_id)
                except: pass
                continue

            # Проверка текста
            if msg.text and is_spam(msg.text):
                print(f"Удаляю спам: {msg.text[:30]}...")
                try:
                    bot.delete_message(CHAT_ID, msg.message_id)
                except Exception as e:
                    if "message to delete not found" not in str(e):
                        print(f"Ошибка удаления: {e}")

        print("--- Очистка завершена ---")
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if TOKEN and CHAT_ID: clean_chat()
