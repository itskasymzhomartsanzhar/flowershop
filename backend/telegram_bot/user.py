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
from api.notifications import send_order_status_notification
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

    if command.args == 'delivery_terms':
        text = (
            "Условия доставки🚚\n\n"
            "Мы доставляем заказы по Краснодару собственными курьерами, чтобы контролировать качество сервиса и сохранить свежесть цветов до момента вручения.\n\n"
            "В периоды высокой загрузки, когда количество заказов сильно увеличивается, мы можем привлекать курьерские службы-партнёры. Это позволяет не задерживать доставку и привозить заказы в запланированное время.\n\n"
            "Доставка по Краснодару входит в сервисный сбор. В него также входит упаковка цветов и подготовка заказа к отправке.\n\n"
            "Размер сервисного сбора составляет 15% от суммы заказа."
        )
        await message.answer(text)
        return

    text = (
        "Рады видеть в нашем сервисе СРЕЗ 💚\n\n"
        "Вы можете выбрать цветок по кнопке КАТАЛОГ или ОТКРЫТЬ МАГАЗИН\n\n"
        "А если не получится, то менеджеры рады помочь — @srez_zabota"
    )
    await message.answer(text, reply_markup=kb.web_app_button('https://flowershop.swifttest.ru'))


@user_router.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_web_app_data(message: Message):
    data = (message.web_app_data.data or '').strip() if message.web_app_data else ''
    if data != 'delivery_terms':
        return
    text = (
        "Условия доставки🚚\n\n"
        "Мы доставляем заказы по Краснодару собственными курьерами, чтобы контролировать качество сервиса и сохранить свежесть цветов до момента вручения.\n\n"
        "В периоды высокой загрузки, когда количество заказов сильно увеличивается, мы можем привлекать курьерские службы-партнёры. Это позволяет не задерживать доставку и привозить заказы в запланированное время.\n\n"
        "Доставка по Краснодару входит в сервисный сбор. В него также входит упаковка цветов и подготовка заказа к отправке.\n\n"
        "Размер сервисного сбора составляет 15% от суммы заказа."
    )
    await message.answer(text)


@user_router.callback_query(lambda c: c.data and c.data.startswith('order:'))
async def handle_staff_order_action(callback_query, bot: Bot):
    staff_chat_id = getenv('ORDER_ASSEMBLERS_CHAT_ID', '')
    if not staff_chat_id:
        print("STAFF_CHAT_GUARD", {"reason": "missing_env"})
        await callback_query.answer()
        return
    try:
        staff_chat_id_int = int(staff_chat_id)
    except ValueError:
        print("STAFF_CHAT_GUARD", {"reason": "invalid_env", "value": staff_chat_id})
        await callback_query.answer()
        return

    if callback_query.message.chat.id != staff_chat_id_int:
        print("STAFF_CHAT_GUARD", {
            "reason": "chat_mismatch",
            "expected": staff_chat_id_int,
            "actual": callback_query.message.chat.id,
            "from": callback_query.from_user.id
        })
        await callback_query.answer()
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
        payer_name = order.payer_name or order.user.name or order.user.telegram_username or str(order.user.tg_id)
        payer_phone = order.payer_phone or ""
        recipient_name = order.recipient_name or payer_name
        recipient_phone = order.recipient_phone or payer_phone
        status_label = get_status_label(order.status)

        items = []
        for item in order.order_items.all():
            items.append(f"{item.product.name} x{item.quantity} = {int(item.price) * int(item.quantity)} ₽")
        items_block = "\n".join(items) if items else "Состав заказа недоступен"

        if order.is_recipient_self:
            recipient_block = f"Заказчик и получатель: <b>{payer_name}</b>, <b>{payer_phone or 'не указан'}</b>\n"
        else:
            recipient_block = (
                f"Заказчик: <b>{payer_name}</b>, <b>{payer_phone or 'не указан'}</b>\n"
                f"Получатель: <b>{recipient_name}</b>, <b>{recipient_phone or 'не указан'}</b>\n"
            )

        promo_line = f"Промокод: <b>{order.promocode}</b>\n" if order.promocode else ""
        comment_line = f"Комментарий: <b>{order.comment}</b>\n" if order.comment else ""

        return (
            f"Заказ: <b>#{order.track_code}</b>\n"
            f"Статус: <b>{status_label}</b>\n"
            f"Сумма: <b>{order.price} ₽</b>\n"
            f"Формат: <b>{delivery_mode}</b>\n"
            f"Время: <b>{delivery_dt}</b>\n"
            f"Адрес: <b>{address}</b>\n"
            f"{recipient_block}"
            f"{promo_line}"
            f"{comment_line}\n"
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

    try:
        await sync_to_async(send_order_status_notification)(order)
    except Exception:
        pass

    await callback_query.answer('Ок')
