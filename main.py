import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = "@lugansk112"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

SPAM_KEYWORDS = ['канал 18+', 'пиши в лс', 'пиши в личку', 'встречусь', 'хуй', 'член', 'секс', 'соска', 'люблю мужчин']

@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member_handler(message: types.Message):
    for user in message.new_chat_members:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton(text="✅ Я подписался", callback_data="checksub")
        )
        await bot.restrict_chat_member(message.chat.id, user.id, ChatPermissions(can_send_messages=False))
        await bot.send_message(
            message.chat.id,
            "👋 Привет, чтобы писать в этом чате — подпишись на канал {}\n"
            "И нажми кнопку ниже 👇".format(CHANNEL_USERNAME),
            reply_markup=keyboard
        )
        logging.info("👀 Новый пользователь {} добавлен и ограничен.".format(user.id))

@dp.callback_query_handler(lambda c: c.data == "checksub")
async def process_subscription(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['creator', 'administrator', 'member']:
            await bot.restrict_chat_member(chat_id, user_id, ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True))
            await callback_query.answer("✅ Подписка подтверждена! Можешь писать.")
        else:
            await callback_query.answer("❌ Ты не подписан на канал!", show_alert=True)
    except:
        await callback_query.answer("⚠️ Ошибка при проверке подписки", show_alert=True)

@dp.message_handler(lambda message: message.text and any(word in message.text.lower() for word in SPAM_KEYWORDS))
async def spam_filter(message: types.Message):
    await message.delete()
    await message.answer("🚫 Сообщение удалено за нарушение правил.")
    logging.info("❌ Удален спам от {}: {}".format(message.from_user.id, message.text))

@dp.message_handler(commands=["log"])
async def get_log(message: types.Message):
    await message.reply("✅ Бот активен и слушает чат.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
