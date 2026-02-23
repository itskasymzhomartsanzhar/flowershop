import asyncio
import logging
from os import getenv, environ

import django

environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()
from aiogram import Dispatcher, Bot
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from django.shortcuts import get_object_or_404
from rest_framework import status  # type: ignore
from rest_framework.decorators import api_view, permission_classes  # type: ignore
from rest_framework.permissions import IsAuthenticated  # type: ignore
from rest_framework.response import Response  # type: ignore
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
from aiogram.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,WebAppInfo
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

from django.core.cache import cache
from asgiref.sync import sync_to_async
from yookassa import Payment, Configuration    # type: ignore
from telegram_bot.user import user_router
#from telegram_bot.admin import admin_router



    
async def main():

    bot = Bot('7898807263:AAEVGakrVXbQxLXE7jeMTThmruE0ZXz9RBE', default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_routers(user_router)

    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Завершение работы')
