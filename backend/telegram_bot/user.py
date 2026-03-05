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
from api.models import Users, Product, Orders, OrderItem
from api.order_flow import build_staff_keyboard, get_next_status, get_status_label
from django.db import transaction
from django.utils import timezone
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

    print(
        "USER_REGISTERED",
        {
            "tg_id": user.tg_id,
            "name": user.name,
            "telegram_username": user.telegram_username,
            "created": created,
        }
    )

    text = (
        "👋 Привет! Это интернет-магазин Flower Shop\n\n"
    )
    await message.answer(text, reply_markup=kb.web_app_button('https://flowershop.swifttest.ru'))


@user_router.callback_query(lambda c: c.data and c.data.startswith('order:'))
async def handle_staff_order_action(callback_query, bot: Bot):
    staff_chat_id = getenv('ORDER_ASSEMBLERS_CHAT_ID', '')
    if not staff_chat_id:
        await callback_query.answer('Доступ запрещен', show_alert=True)
        return
    try:
        staff_chat_id_int = int(staff_chat_id)
    except ValueError:
        await callback_query.answer('Доступ запрещен', show_alert=True)
        return

    if callback_query.message.chat.id != staff_chat_id_int:
        await callback_query.answer('Доступ запрещен', show_alert=True)
        return

    parts = callback_query.data.split(':', 2)
    if len(parts) != 3:
        await callback_query.answer('Недоступно', show_alert=True)
        return

    _, order_id_raw, target_status = parts
    try:
        order_id = int(order_id_raw)
    except ValueError:
        await callback_query.answer('Недоступно', show_alert=True)
        return

    def _build_staff_text(order):
        delivery_mode = "Самовывоз" if order.is_pickup else "Доставка"
        address = "Самовывоз" if order.is_pickup else (order.delivery_address or "Не указан")
        delivery_dt = f"{order.delivery_date} {order.delivery_time_slot}".strip() if order.delivery_date else "Как можно скорее"
        recipient_name = order.recipient_name or order.user.name or order.user.telegram_username or str(order.user.tg_id)
        recipient_phone = order.recipient_phone or ""
        status_label = get_status_label(order.status)

        items = []
        for item in order.order_items.all():
            items.append(f"{item.product.name} x{item.quantity} = {int(item.price) * int(item.quantity)} ₽")
        items_block = "\n".join(items) if items else "Состав заказа недоступен"

        return (
            f"Заказ: <b>#{order.track_code}</b>\n"
            f"Статус: <b>{status_label}</b>\n"
            f"Сумма: <b>{order.price} ₽</b>\n"
            f"Формат: <b>{delivery_mode}</b>\n"
            f"Время: <b>{delivery_dt}</b>\n"
            f"Адрес: <b>{address}</b>\n"
            f"Получатель: <b>{recipient_name}</b>, <b>{recipient_phone or 'не указан'}</b>\n\n"
            f"Состав:\n{items_block}"
        )

    def _advance_status():
        with transaction.atomic():
            order = Orders.objects.select_for_update().select_related('user').prefetch_related('order_items__product').filter(id=order_id).first()
            if not order:
                return None, 'Заказ не найден'
            expected = get_next_status(order)
            if not expected or expected != target_status:
                return order, 'Недоступно'
            updated = Orders.objects.filter(id=order.id, status=order.status).update(
                status=target_status
            )
            if not updated:
                return order, 'Уже обработано'
            order.refresh_from_db()
            order = Orders.objects.select_related('user').prefetch_related('order_items__product').get(id=order.id)
            return order, None

    order, error = await sync_to_async(_advance_status)()
    if error:
        await callback_query.answer(error, show_alert=True)
        return

    staff_keyboard = build_staff_keyboard(order)
    text = _build_staff_text(order)
    try:
        await bot.edit_message_text(
            text=text,
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            parse_mode=ParseMode.HTML,
            reply_markup=staff_keyboard
        )
    except Exception:
        pass

    await callback_query.answer('Ок')

