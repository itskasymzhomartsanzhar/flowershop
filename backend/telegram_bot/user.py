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


bot = Bot(getenv('BOT_TOKEN', ''), default=DefaultBotProperties(parse_mode=ParseMode.HTML))



@user_router.message(CommandStart())
async def start_message(message: Message, bot: Bot, command: CommandObject, state: FSMContext):
    full_name = f"{message.from_user.first_name or ''} {message.from_user.last_name or ''}".strip()
    username = message.from_user.username or ''
    display_name = full_name or username or 'Пользователь'

    user, created = await sync_to_async(Users.objects.get_or_create)(
        tg_id=message.from_user.id,
        defaults={
            'telegram_username': username,
            'name': display_name,
        }
    )

    if not created:
        updated_fields = []
        if username and user.telegram_username != username:
            user.telegram_username = username
            updated_fields.append('telegram_username')
        if display_name and user.name != display_name:
            user.name = display_name
            updated_fields.append('name')
        if updated_fields:
            await sync_to_async(user.save)(update_fields=updated_fields)

    text = (
        "👋 Привет! Это интернет-магазин Flower Shop\n\n"
    )
    await message.answer(text, reply_markup=kb.web_app_button('https://flowershop.swifttest.ru'))

