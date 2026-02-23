from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo





def has18() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="✅ Мне больше 18 лет", callback_data="has18true")
    keyboard.button(text="❌ Мне нет 18 лет", callback_data="has18false")

    return keyboard.adjust(1).as_markup()


def web_app_button(url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Открыть магазин', web_app=WebAppInfo(url=url))
    return keyboard.as_markup()
