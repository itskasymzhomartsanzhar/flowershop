import asyncio
import asyncpg
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError

# === НАСТРОЙКИ ===
BOT_TOKEN = "7898807263:AAEVGakrVXbQxLXE7jeMTThmruE0ZXz9RBE"
DB_DSN = "postgresql://flowershop:flowershop_db_pwd@localhost:5444/flowershop"
IMAGE_PATH = "photo.jpg"  # путь к картинке

TEXT = """Эта новость не может вас не порадовать 💚
У нас появились новые цветочные сеты 🌿
Свежие гортензии, нежные гвоздики, весенние ветки, дельфиниумы и даже львиный зев — собрали готовые сочетания, которые легко вписываются в ваш дом без всего лишнего.
Просто цветы, которые выглядят дорого и свежо уже с первого взгляда!
И да, у вас всё ещё есть скидка на первый заказ 20%
по промокоду ▶️ВЕСНА◀️
Самое время порадовать себя или близких ✨"""

BUTTON = InlineKeyboardMarkup([[
    InlineKeyboardButton("ОФОРМИТЬ ЗАКАЗ", url="https://t.me/srezflowers_bot")
]])

# === РАССЫЛКА ===
async def main():
    conn = await asyncpg.connect(DB_DSN)
    
    # Замените на реальное название таблицы и колонки
    rows = await conn.fetch("SELECT tg_id FROM api_users WHERE notification_promotion = true")
    await conn.close()

    bot = Bot(token=BOT_TOKEN)
    
    ok, fail = 0, 0
    for row in rows:
        chat_id = row["tg_id"]
        try:
            with open(IMAGE_PATH, "rb") as photo:
                await bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=TEXT,
                    reply_markup=BUTTON
                )
            ok += 1
        except TelegramError as e:
            print(f"[FAIL] {chat_id}: {e}")
            fail += 1
        await asyncio.sleep(0.05)  # лимит Telegram: ~20 сообщений/сек

    print(f"Готово: {ok} ок, {fail} ошибок")

asyncio.run(main())
