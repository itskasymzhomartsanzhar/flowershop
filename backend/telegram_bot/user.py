from os import getenv, environ

from aiogram import Dispatcher, Bot
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram.types import LabeledPrice
from asgiref.sync import sync_to_async
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import LabeledPrice, PreCheckoutQuery, SuccessfulPayment, ContentType
from aiogram.utils.i18n import gettext as _
from aiogram import Bot
from aiogram.methods.get_user_profile_photos import GetUserProfilePhotos
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from asgiref.sync import sync_to_async
import django.contrib
from django.db.models import Sum
from aiogram.types import URLInputFile

from pathlib import Path
from datetime import datetime
from os import getenv, environ

from django.db.models import Q
from datetime import datetime, timedelta
from django.db.models import Count, Min, OuterRef, Prefetch, Q, Subquery, Max
from django.core.exceptions import ObjectDoesNotExist
from api.models import Users, Product, Orders
import requests
import aiohttp
import json
import re
import os
from aiogram.fsm.state import State, StatesGroup
from .state import Register
from . import keyboards as kb

user_router = Router()


bot = Bot('7898807263:AAEVGakrVXbQxLXE7jeMTThmruE0ZXz9RBE', default=DefaultBotProperties(parse_mode=ParseMode.HTML))



@user_router.message(CommandStart())
async def start_message(message: Message, bot: Bot, command: CommandObject, state: FSMContext):
    # Получаем или создаем пользователя
    # Формируем полное имя из first_name и last_name
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()

    await sync_to_async(Users.objects.get_or_create)(
        tg_id=message.from_user.id,
        defaults={
            'telegram_username': message.from_user.username or '',
            'name': full_name or message.from_user.username or 'Пользователь',
        }
    )

    text = (
        "👋 Привет! Это интернет-магазин Flower Shop\n\n"
    )
    await message.answer(text, reply_markup=kb.web_app_button('https://flowershop.swifttest.ru'))

