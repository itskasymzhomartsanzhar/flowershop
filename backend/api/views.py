from django.shortcuts import render
from .models import Users, Product, Category, Orders, Poster, Favorites, Review, Promocode, UsedPromocode, OrderItem, ServiceFeeSettings, PaymentSession, DeliverySettings, DeliveryTimeSlot, PaymentReminderSettings
import requests
import random
from urllib.parse import quote
import uuid
import json
from django.core.cache import cache
from django.conf import settings
from requests.auth import HTTPBasicAuth
from rest_framework import status, viewsets, permissions, mixins # type: ignore
from rest_framework.decorators import action, api_view, permission_classes  # type: ignore
from rest_framework.response import Response # type: ignore
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from yookassa import Configuration, Payment # type: ignore
import uuid
from requests.exceptions import JSONDecodeError
from .serializers import UsersSerializer, ProductSerializer, CategorySerializer, OrdersSerializer, PosterSerializer, FavoritesSerializer, ReviewSerializer
from django.db.models import Avg, Count
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action  # type: ignore
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime, timedelta, date
from math import radians, sin, cos, sqrt, atan2
import time
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.db import transaction

Configuration.account_id = getattr(settings, 'YOOKASSA_ACCOUNT_ID', '1134900')
Configuration.secret_key = getattr(settings, 'YOOKASSA_SECRET_KEY', 'test_KuPzb4yyMFfgEfEYnfJ4gWO8QQtFTzA6TSqCaK3LuAs')
PICKUP_ADDRESS_PLACEHOLDER = 'ул. Пушкина, дом 1'
PAYMENT_RETURN_URL = getattr(settings, 'PAYMENT_RETURN_URL', 'https://swiftstore.tw1.su/')
ORDER_ASSEMBLERS_CHAT_ID = str(getattr(settings, 'ORDER_ASSEMBLERS_CHAT_ID', '') or '').strip()


def _telegram_api_url(method):
    return f"https://api.telegram.org/bot{settings.BOT_TOKEN}/{method}"


def send_telegram_payment_link(tg_id, text, payment_url):
    payload = {
        "chat_id": int(tg_id),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [[{"text": "Оплатить заказ", "url": payment_url}]]
        }
    }
    try:
        response = requests.post(_telegram_api_url("sendMessage"), json=payload, timeout=10)
        data = response.json()
        if response.status_code == 200 and data.get("ok"):
            message = data.get("result", {})
            return True, message.get("message_id")
    except Exception:
        return False, None
    return False, None


def send_telegram_mock_payment_button(tg_id, text, callback_data):
    payload = {
        "chat_id": int(tg_id),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [[{"text": "Оплатить", "callback_data": callback_data}]]
        }
    }
    try:
        response = requests.post(_telegram_api_url("sendMessage"), json=payload, timeout=10)
        data = response.json()
        if response.status_code == 200 and data.get("ok"):
            message = data.get("result", {})
            return True, message.get("message_id")
    except Exception:
        return False, None
    return False, None


def edit_telegram_payment_message(tg_id, message_id, text):
    if not tg_id or not message_id:
        return False
    payload = {
        "chat_id": int(tg_id),
        "message_id": int(message_id),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(_telegram_api_url("editMessageText"), json=payload, timeout=10)
        data = response.json()
        return response.status_code == 200 and data.get("ok")
    except Exception:
        return False


def send_telegram_status_message(tg_id, text):
    payload = {
        "chat_id": int(tg_id),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(_telegram_api_url("sendMessage"), json=payload, timeout=10)
        data = response.json()
        return response.status_code == 200 and data.get("ok")
    except Exception:
        return False


def _normalize_phone(value):
    phone = ''.join(ch for ch in str(value or '') if ch.isdigit() or ch == '+').strip()
    if phone.startswith('8'):
        phone = f'+7{phone[1:]}'
    if phone and not phone.startswith('+'):
        phone = f'+{phone}'
    return phone


def _format_recipient_block(is_recipient_self, user, recipient_name, recipient_phone):
    if is_recipient_self:
        fallback_name = user.name or (f'@{user.telegram_username}' if user.telegram_username else str(user.tg_id))
        return f"Заказчик и получатель: <b>{fallback_name}</b>, <b>{_normalize_phone(recipient_phone) or 'не указан'}</b>"
    return f"Получатель: <b>{recipient_name}</b>, <b>{_normalize_phone(recipient_phone) or 'не указан'}</b>"


def send_assemblers_order_message(chat_id, text):
    if not chat_id:
        return False
    payload = {
        "chat_id": int(chat_id),
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(_telegram_api_url("sendMessage"), json=payload, timeout=10)
        data = response.json()
        return response.status_code == 200 and data.get("ok")
    except Exception:
        return False


def build_assemblers_order_text(payment_session):
    order_number = payment_session.order.track_code if payment_session.order_id else payment_session.payment_id[:8].upper()
    delivery_mode = "Самовывоз" if payment_session.is_pickup else "Доставка"
    address_text = PICKUP_ADDRESS_PLACEHOLDER if payment_session.is_pickup else (payment_session.address or "Не указан")
    delivery_dt = f"{payment_session.delivery_date} {payment_session.delivery_time_slot}".strip() if payment_session.delivery_date else "Как можно скорее"
    recipient_block = _format_recipient_block(
        payment_session.is_recipient_self,
        payment_session.user,
        payment_session.recipient_name,
        payment_session.recipient_phone or payment_session.phone,
    )
    items = payment_session.goods or []
    items_lines = []
    for item in items:
        item_name = item.get('name') or f"Товар #{item.get('id')}"
        try:
            qty = int(item.get('quantity') or 0)
        except (TypeError, ValueError):
            qty = 0
        try:
            line_total = int(Decimal(str(item.get('line_total') or 0)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        except (InvalidOperation, TypeError, ValueError):
            line_total = 0
        items_lines.append(f"• {item_name} x{qty} = {line_total} ₽")
    items_block = '\n'.join(items_lines) if items_lines else '• Состав заказа недоступен'
    return (
        f"🆕 Новый оплаченный заказ\n"
        f"Заказ: <b>#{order_number}</b>\n"
        f"Сумма: <b>{payment_session.amount} ₽</b>\n"
        f"Формат: <b>{delivery_mode}</b>\n"
        f"Время: <b>{delivery_dt}</b>\n"
        f"Адрес: <b>{address_text}</b>\n"
        f"Контакт заказчика: <b>{_normalize_phone(payment_session.phone) or 'не указан'}</b>\n"
        f"{recipient_block}\n"
        f"Комментарий: <b>{payment_session.comment or 'нет'}</b>\n\n"
        f"Состав:\n{items_block}"
    )


def normalize_payment_status(status_value):
    mapping = {
        "pending": PaymentSession.StatusEnum.PENDING,
        "waiting_for_capture": PaymentSession.StatusEnum.WAITING,
        "succeeded": PaymentSession.StatusEnum.SUCCEEDED,
        "canceled": PaymentSession.StatusEnum.CANCELED,
    }
    return mapping.get((status_value or "").lower(), PaymentSession.StatusEnum.PENDING)


def build_payment_status_text(payment_session):
    order_number = payment_session.order.track_code if payment_session.order_id else payment_session.payment_id[:8].upper()
    delivery_mode = "Самовывоз" if payment_session.is_pickup else "Доставка"
    address_text = PICKUP_ADDRESS_PLACEHOLDER if payment_session.is_pickup else (payment_session.address or "Не указан")
    delivery_dt = f"{payment_session.delivery_date} {payment_session.delivery_time_slot}".strip() if payment_session.delivery_date else "Как можно скорее"
    recipient_block = _format_recipient_block(
        payment_session.is_recipient_self,
        payment_session.user,
        payment_session.recipient_name,
        payment_session.recipient_phone or payment_session.phone,
    )
    if payment_session.status == PaymentSession.StatusEnum.SUCCEEDED:
        return (
            f"✅ Оплата прошла успешно\n"
            f"Заказ: <b>#{order_number}</b>\n"
            f"Сумма: <b>{payment_session.amount} ₽</b>\n"
            f"Формат: <b>{delivery_mode}</b>\n"
            f"Время: <b>{delivery_dt}</b>\n"
            f"Адрес: <b>{address_text}</b>\n"
            f"{recipient_block}\n"
            f"Статус: <b>Оплачен</b>"
        )
    if payment_session.status == PaymentSession.StatusEnum.CANCELED:
        return (
            f"❌ Оплата отменена\n"
            f"Заказ: <b>#{order_number}</b>\n"
            f"Сумма: <b>{payment_session.amount} ₽</b>\n"
            f"Формат: <b>{delivery_mode}</b>\n"
            f"Время: <b>{delivery_dt}</b>\n"
            f"Адрес: <b>{address_text}</b>\n"
            f"{recipient_block}\n"
            f"Вы можете оформить оплату повторно в Mini App."
        )
    if payment_session.status == PaymentSession.StatusEnum.WAITING:
        return (
            f"⏳ Ожидается подтверждение оплаты\n"
            f"Заказ: <b>#{order_number}</b>\n"
            f"Сумма: <b>{payment_session.amount} ₽</b>\n"
            f"Формат: <b>{delivery_mode}</b>\n"
            f"Время: <b>{delivery_dt}</b>\n"
            f"Адрес: <b>{address_text}</b>\n"
            f"{recipient_block}"
        )
    return (
        f"🧾 Заказ создан\n"
        f"Номер: <b>#{order_number}</b>\n"
        f"Сумма: <b>{payment_session.amount} ₽</b>\n"
        f"Формат: <b>{delivery_mode}</b>\n"
        f"Время: <b>{delivery_dt}</b>\n"
        f"Адрес: <b>{address_text}</b>\n"
        f"{recipient_block}\n"
        f"Статус: <b>Ожидает оплаты</b>"
    )


def mark_promocode_as_used_if_needed(user, promocode_text):
    code = (promocode_text or "").strip()
    if not code:
        return
    promocode = Promocode.objects.filter(promocode__iexact=code).first()
    if not promocode:
        return
    UsedPromocode.objects.get_or_create(user=user, promocode=promocode)


def _get_payment_reminder_settings():
    settings_obj = PaymentReminderSettings.objects.first()
    if not settings_obj:
        return {
            'delay_minutes': 15,
            'message_text': 'Напоминаем: заказ #{order_number} ожидает оплату. Сумма: {amount} ₽.\nОплатить: {payment_url}'
        }
    return {
        'delay_minutes': int(settings_obj.delay_minutes or 15),
        'message_text': settings_obj.message_text or 'Напоминаем: заказ #{order_number} ожидает оплату. Сумма: {amount} ₽.\nОплатить: {payment_url}'
    }


def _build_payment_reminder_text(payment_session, template):
    order_number = payment_session.order.track_code if payment_session.order_id else payment_session.payment_id[:8].upper()
    context = {
        'order_number': order_number,
        'amount': str(payment_session.amount),
        'payment_url': payment_session.confirmation_url or '',
        'minutes': str(int(_get_payment_reminder_settings()['delay_minutes'])),
    }
    try:
        return str(template).format(**context)
    except Exception:
        return f"Напоминаем: заказ #{order_number} ожидает оплату. Сумма: {payment_session.amount} ₽.\nОплатить: {payment_session.confirmation_url or ''}"


def _try_send_payment_reminder(payment_session_id, check_due=True):
    lock_key = f'payment_reminder_lock:{payment_session_id}'
    try:
        if not cache.add(lock_key, 1, timeout=120):
            return False
    except Exception:
        return False
    try:
        session = PaymentSession.objects.filter(pk=payment_session_id).select_related('order', 'user').first()
        if not session:
            return False
        if session.reminder_sent_at:
            return False
        if session.status not in {PaymentSession.StatusEnum.PENDING, PaymentSession.StatusEnum.WAITING}:
            return False
        if check_due and (not session.reminder_due_at or timezone.now() < session.reminder_due_at):
            return False

        try:
            payment = Payment.find_one(session.payment_id)
            session = sync_payment_session_status(session, payment.status)
        except Exception:
            session.refresh_from_db()

        if session.reminder_sent_at:
            return False
        if session.status not in {PaymentSession.StatusEnum.PENDING, PaymentSession.StatusEnum.WAITING}:
            return False

        reminder_settings = _get_payment_reminder_settings()
        reminder_text = _build_payment_reminder_text(session, reminder_settings['message_text'])
        sent = send_telegram_status_message(session.telegram_chat_id, reminder_text)
        if not sent:
            return False

        now = timezone.now()
        updated = PaymentSession.objects.filter(pk=session.pk, reminder_sent_at__isnull=True).update(
            reminder_sent_at=now,
            updated_at=now
        )
        return bool(updated)
    finally:
        try:
            cache.delete(lock_key)
        except Exception:
            pass


def _schedule_payment_reminder(payment_session_id, delay_minutes):
    try:
        from .tasks import send_payment_reminder_task
    except Exception:
        return

    delay_seconds = max(0, int(delay_minutes)) * 60
    try:
        send_payment_reminder_task.apply_async(args=[payment_session_id, False], countdown=delay_seconds)
    except Exception:
        pass


def _dispatch_due_payment_reminders(limit=20):
    try:
        from .tasks import send_payment_reminder_task
    except Exception:
        return

    due_ids = list(
        PaymentSession.objects.filter(
            reminder_sent_at__isnull=True,
            reminder_due_at__isnull=False,
            reminder_due_at__lte=timezone.now(),
            status__in=[PaymentSession.StatusEnum.PENDING, PaymentSession.StatusEnum.WAITING],
        )
        .order_by('reminder_due_at')
        .values_list('id', flat=True)[:limit]
    )
    for payment_session_id in due_ids:
        try:
            send_payment_reminder_task.delay(payment_session_id, True)
        except Exception:
            break


@transaction.atomic
def ensure_order_for_payment_session(payment_session):
    locked_session = PaymentSession.objects.select_for_update().select_related('user', 'order').get(pk=payment_session.pk)
    if locked_session.order_id:
        return locked_session.order

    goods_data = locked_session.goods or []
    first_product = None
    first_photo = None
    if goods_data:
        first_id = goods_data[0].get('id')
        if first_id:
            product = Product.objects.filter(id=first_id).first()
            if product:
                first_product = product.name
                first_photo = product.photo1

    track_code = f"{uuid.uuid4().hex[:8].upper()}"
    order = Orders.objects.create(
        user=locked_session.user,
        name=first_product or f"Заказ от {locked_session.user.name or locked_session.user.telegram_username}",
        track_code=track_code,
        price=int(Decimal(str(locked_session.amount)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)),
        status=Orders.StatusEnum.PAID,
        isreturn=False,
        is_pickup=locked_session.is_pickup,
        is_recipient_self=locked_session.is_recipient_self,
        recipient_name=locked_session.recipient_name,
        recipient_phone=locked_session.recipient_phone,
        delivery_date=locked_session.delivery_date,
        delivery_time_slot=locked_session.delivery_time_slot or None,
        photo=first_photo if first_photo else None,
        delivery_address=locked_session.address,
    )

    for good in goods_data:
        try:
            product = Product.objects.get(id=int(good.get('id')))
            quantity = max(1, int(good.get('quantity', 1)))
            line_price = Decimal(str(good.get('price', 0))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=line_price
            )
        except Exception:
            continue

    mark_promocode_as_used_if_needed(locked_session.user, locked_session.promocode)
    cache.delete(f"cart:{locked_session.user.tg_id}")

    locked_session.order = order
    locked_session.save(update_fields=['order', 'updated_at'])
    return order


def sync_payment_session_status(payment_session, yookassa_status):
    mapped_status = normalize_payment_status(yookassa_status)
    if payment_session.status == mapped_status and not (mapped_status == PaymentSession.StatusEnum.SUCCEEDED and not payment_session.order_id):
        return payment_session

    payment_session.status = mapped_status
    payment_session.save(update_fields=['status', 'updated_at'])

    if mapped_status == PaymentSession.StatusEnum.SUCCEEDED:
        ensure_order_for_payment_session(payment_session)
        payment_session.refresh_from_db()
        if ORDER_ASSEMBLERS_CHAT_ID and not payment_session.assemblers_notified_at:
            sent = send_assemblers_order_message(ORDER_ASSEMBLERS_CHAT_ID, build_assemblers_order_text(payment_session))
            if sent:
                payment_session.assemblers_notified_at = timezone.now()
                payment_session.save(update_fields=['assemblers_notified_at', 'updated_at'])

    status_text = build_payment_status_text(payment_session)
    edited = edit_telegram_payment_message(payment_session.telegram_chat_id, payment_session.telegram_message_id, status_text)
    if not edited:
        send_telegram_status_message(payment_session.telegram_chat_id, status_text)

    return payment_session


class UsersViewSet(viewsets.ModelViewSet): 
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        tg_id = int(self.request.tg_user_data['tg_id'])

        if tg_id:
            return Users.objects.filter(tg_id=tg_id)
        else:
            return Users.objects.none()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=False, methods=['get'], url_path='profile')
    def get_profile(self, request):
        tg_id = self.request.tg_user_data.get('tg_id', None)

        if tg_id:
            user = get_object_or_404(Users, tg_id=tg_id)

        
        if not user:
            return Response({'error': 'User not found'}, status=404)
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='update-notifications')
    def update_notifications(self, request):
        
        tg_id = self.request.tg_user_data.get('tg_id', None)

        if tg_id:
            user = get_object_or_404(Users, tg_id=tg_id)

        
        if not user:
            return Response({'error': 'User not found'}, status=404)
        
        notification_type = request.data.get('notification_type')
        enabled = request.data.get('enabled', True)
        
        if notification_type == 'order_status':
            user.notification_order_status = enabled
        elif notification_type == 'promotion':
            user.notification_promotion = enabled
        elif notification_type == 'liked':
            user.notification_liked = enabled
        else:
            return Response({'error': 'Invalid notification type'}, status=400)
        
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @staticmethod
    def _round_money(value):
        return int(Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

    @staticmethod
    def _to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {'1', 'true', 'yes', 'on'}
        return bool(value)

    @staticmethod
    def _clean_text(value, max_len=255):
        return str(value or '').strip()[:max_len]

    @staticmethod
    def _validate_phone(value):
        normalized = _normalize_phone(value)
        digits_count = len([ch for ch in normalized if ch.isdigit()])
        if digits_count < 10 or digits_count > 15:
            return None
        return normalized

    @staticmethod
    def _safe_meta_value(value, max_len=128):
        if value is None:
            return ''
        return str(value).strip()[:max_len]

    def _build_yookassa_metadata(self, user, is_pickup, is_recipient_self, first_product_id, summary, promocode):
        metadata = {
            "tg_id": self._safe_meta_value(user.tg_id, max_len=64),
            "is_pickup": self._safe_meta_value(str(bool(is_pickup)).lower(), max_len=8),
            "is_recipient_self": self._safe_meta_value(str(bool(is_recipient_self)).lower(), max_len=8),
            "first_product_id": self._safe_meta_value(first_product_id or '', max_len=32),
            "total": self._safe_meta_value(summary.get('total', 0), max_len=32),
            "discount": self._safe_meta_value(summary.get('discount_percent', 0), max_len=8),
            "service_fee": self._safe_meta_value(summary.get('service_fee_percent', 0), max_len=8),
            "promocode": self._safe_meta_value(promocode.promocode if promocode else '', max_len=64),
        }
        return {key: value for key, value in metadata.items() if value != ''}

    def _get_service_fee_percentage(self):
        settings_obj = ServiceFeeSettings.objects.first()
        if not settings_obj:
            return 0
        return int(settings_obj.percentage or 0)

    @staticmethod
    def _get_product_step(product):
        step = int(getattr(product, 'quantity_step', 1) or 1)
        return max(1, step)

    def _get_delivery_settings(self):
        settings_obj = DeliverySettings.objects.first()
        if not settings_obj:
            settings_obj = DeliverySettings(min_days_ahead=0, max_days_ahead=14)
        slots = list(
            DeliveryTimeSlot.objects.filter(is_active=True)
            .order_by('sort_order', 'label')
            .values_list('label', flat=True)
        )
        if not slots:
            slots = ['10:00-12:00', '12:00-14:00', '14:00-16:00', '16:00-18:00']
        min_days = int(settings_obj.min_days_ahead or 0)
        max_days = int(settings_obj.max_days_ahead or 14)
        if max_days < min_days:
            max_days = min_days
        return min_days, max_days, slots

    def _delivery_options_payload(self):
        min_days, max_days, slots = self._get_delivery_settings()
        min_date = date.today() + timedelta(days=min_days)
        max_date = date.today() + timedelta(days=max_days)
        return {
            'min_days_ahead': min_days,
            'max_days_ahead': max_days,
            'min_date': min_date.isoformat(),
            'max_date': max_date.isoformat(),
            'time_slots': slots,
            'default_time_slot': slots[0] if slots else None,
        }

    def _validate_delivery_selection(self, delivery_date_raw, delivery_time_slot_raw):
        if not delivery_date_raw:
            return None, None, 'Выберите дату доставки'
        if not delivery_time_slot_raw:
            return None, None, 'Выберите время доставки'
        try:
            selected_date = date.fromisoformat(str(delivery_date_raw))
        except ValueError:
            return None, None, 'Некорректная дата доставки'

        slot = str(delivery_time_slot_raw).strip()
        options = self._delivery_options_payload()
        min_date = date.fromisoformat(options['min_date'])
        max_date = date.fromisoformat(options['max_date'])
        if selected_date < min_date or selected_date > max_date:
            return None, None, f'Дата должна быть в диапазоне {options["min_date"]} - {options["max_date"]}'
        if slot not in options['time_slots']:
            return None, None, 'Выбран недоступный временной слот'
        return selected_date, slot, None

    def _resolve_promocode(self, user, promocode_text):
        code = (promocode_text or '').strip().upper()
        if not code:
            return None, 0, None

        promocode = Promocode.objects.filter(promocode__iexact=code).first()
        if not promocode:
            return None, 0, 'Промокод не найден'

        if UsedPromocode.objects.filter(user=user, promocode=promocode).exists():
            return None, 0, 'Вы уже использовали этот промокод'

        discount = max(0, min(100, int(promocode.discount or 0)))
        return promocode, discount, None

    @staticmethod
    def _suggestions_cache_key(query, city, count):
        normalized_query = str(query or '').strip().lower()
        normalized_city = str(city or '').strip().lower()
        return f'addr_suggest:{normalized_query}:{normalized_city}:{int(count)}'

    def _fetch_dadata_suggestions(self, query, city=None, count=8):
        token = getattr(settings, 'DADATA_API_TOKEN', '')
        if not token:
            return []

        query_text = str(query or '').strip()
        if len(query_text) < 3:
            return []

        safe_count = max(1, min(10, int(count or 8)))
        cache_key = self._suggestions_cache_key(query_text, city, safe_count)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        payload = {
            "query": query_text,
            "count": safe_count,
        }
        city_name = str(city or '').strip()
        if city_name:
            payload["locations"] = [{"city": city_name}]

        headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.post(
                getattr(settings, 'DADATA_BASE_URL', 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address'),
                headers=headers,
                json=payload,
                timeout=3,
            )
            if response.status_code != 200:
                return []
            raw_items = response.json().get('suggestions', []) or []
        except Exception:
            return []

        suggestions = []
        for item in raw_items:
            value = (item or {}).get('value')
            unrestricted_value = (item or {}).get('unrestricted_value') or value
            if not value:
                continue
            data = (item or {}).get('data') or {}
            suggestions.append({
                'value': value,
                'unrestricted_value': unrestricted_value,
                'street': data.get('street') or '',
                'house': data.get('house') or '',
                'city': data.get('city') or data.get('settlement') or '',
                'region': data.get('region_with_type') or '',
            })

        cache.set(cache_key, suggestions, timeout=60 * 10)
        return suggestions

    @action(detail=False, methods=['get'], url_path='address-suggestions')
    def address_suggestions(self, request):
        query = str(request.query_params.get('q', '')).strip()
        city = str(request.query_params.get('city', '')).strip()
        try:
            count = int(request.query_params.get('count', 8))
        except (TypeError, ValueError):
            count = 8

        if len(query) < 3:
            return Response({'suggestions': []})

        suggestions = self._fetch_dadata_suggestions(query=query, city=city, count=count)
        return Response({'suggestions': suggestions})

    @action(detail=False, methods=['get'], url_path='delivery-options')
    def delivery_options(self, request):
        return Response(self._delivery_options_payload())

    def _build_cart_snapshot(self, request, tg_id, discount_percent=0):
        key = f'cart:{tg_id}'
        raw_cart = cache.get(key, {}) or {}

        parsed_items = []
        for product_id, quantity in raw_cart.items():
            try:
                parsed_id = int(product_id)
                parsed_qty = int(quantity)
            except (TypeError, ValueError):
                continue
            if parsed_qty > 0:
                parsed_items.append((parsed_id, parsed_qty))

        if not parsed_items:
            cache.delete(key)
            return {'cart': [], 'summary': {'items_count': 0, 'subtotal': 0, 'service_fee_percent': 0, 'service_fee_amount': 0, 'discount_percent': 0, 'discount_amount': 0, 'total': 0}}

        product_ids = [item[0] for item in parsed_items]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {product.id: product for product in products}

        normalized_cart = {}
        cart_items = []
        subtotal = 0
        total_quantity = 0

        for product_id, quantity in parsed_items:
            product = product_map.get(product_id)
            if not product:
                continue

            step = self._get_product_step(product)
            normalized_qty = (quantity // step) * step
            if normalized_qty <= 0:
                continue

            unit_price = int(product.price or 0)
            line_total = unit_price * normalized_qty
            subtotal += line_total
            total_quantity += normalized_qty
            normalized_cart[str(product_id)] = normalized_qty

            cart_items.append({
                'id': product.id,
                'name': product.name,
                'price': unit_price,
                'photo': request.build_absolute_uri(product.photo1.url) if product.photo1 else None,
                'quantity': normalized_qty,
                'quantity_step': step,
                'line_total': line_total,
            })

        cache.set(key, normalized_cart, timeout=60 * 60 * 24 * 7)

        if not cart_items:
            cache.delete(key)
            return {'cart': [], 'summary': {'items_count': 0, 'subtotal': 0, 'service_fee_percent': 0, 'service_fee_amount': 0, 'discount_percent': 0, 'discount_amount': 0, 'total': 0}}

        service_fee_percent = self._get_service_fee_percentage()
        service_fee_amount = 0
        if service_fee_percent > 0:
            service_fee_amount = self._round_money(Decimal(subtotal) * Decimal(service_fee_percent) / Decimal(100))

        base_total = subtotal + service_fee_amount
        discount_percent = max(0, min(100, int(discount_percent or 0)))
        discount_amount = 0
        if discount_percent > 0:
            discount_amount = self._round_money(Decimal(base_total) * Decimal(discount_percent) / Decimal(100))

        total = max(0, base_total - discount_amount)

        summary = {
            'items_count': total_quantity,
            'subtotal': subtotal,
            'service_fee_percent': service_fee_percent,
            'service_fee_amount': service_fee_amount,
            'discount_percent': discount_percent,
            'discount_amount': discount_amount,
            'total': total,
        }
        return {'cart': cart_items, 'summary': summary}


    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        _dispatch_due_payment_reminders(limit=10)
        data = request.data

        phone = self._validate_phone(data.get('phone'))
        raw_address = (data.get('address') or '').strip()
        comment = self._clean_text(data.get('comment', ''), max_len=1000)
        promocode_text = self._clean_text(data.get('promocode', ''), max_len=100)
        is_pickup = self._to_bool(data.get('is_pickup', False))
        is_recipient_self = self._to_bool(data.get('is_recipient_self', True))
        recipient_name = self._clean_text(data.get('recipient_name', ''), max_len=255)
        recipient_phone = self._validate_phone(data.get('recipient_phone'))
        delivery_date_raw = data.get('delivery_date')
        delivery_time_slot_raw = data.get('delivery_time_slot')
        tg_id = str(self.request.tg_user_data.get('tg_id'))
        address = PICKUP_ADDRESS_PLACEHOLDER if is_pickup else raw_address
        delivery_date_value = None
        delivery_time_slot_value = ''

        if not phone or not address:
            return Response({'error': 'Missing phone or address'}, status=status.HTTP_400_BAD_REQUEST)
        if not is_recipient_self and (not recipient_name or not recipient_phone):
            return Response({'error': 'Укажите имя и телефон получателя'}, status=status.HTTP_400_BAD_REQUEST)
        if is_recipient_self:
            recipient_name = ''
            recipient_phone = phone

        if not is_pickup:
            delivery_date_value, delivery_time_slot_value, delivery_error = self._validate_delivery_selection(
                delivery_date_raw,
                delivery_time_slot_raw
            )
            if delivery_error:
                return Response({'error': delivery_error}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(Users, tg_id=tg_id)
        promocode, discount_percent, promo_error = self._resolve_promocode(user, promocode_text)
        if promo_error:
            return Response({'error': promo_error}, status=status.HTTP_400_BAD_REQUEST)

        snapshot = self._build_cart_snapshot(request, tg_id, discount_percent=discount_percent)
        cart_items = snapshot['cart']
        summary = snapshot['summary']

        if not cart_items:
            return Response({'error': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        goods_metadata = [
            {
                'id': item['id'],
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'line_total': item['line_total'],
            }
            for item in cart_items
        ]
        if getattr(settings, 'MOCK_PAYMENT_BUTTON', True):
            mock_payment_id = f"mock_{uuid.uuid4().hex[:12]}"
            mock_text = (
                f"🧾 Заказ создан\n"
                f"Номер: <b>#{mock_payment_id[-6:].upper()}</b>\n"
                f"Сумма: <b>{summary['total']} ₽</b>\n"
                f"Статус: <b>Ожидает оплаты</b>"
            )
            sent, _ = send_telegram_mock_payment_button(
                tg_id=user.tg_id,
                text=mock_text,
                callback_data=f"mock_pay:{mock_payment_id}",
            )
            if not sent:
                return Response({'error': 'Не удалось отправить сообщение в Telegram. Попробуйте снова.'}, status=500)
            return Response({
                "payment_id": mock_payment_id,
                "payment_url_sent": True,
                "mock": True,
                "summary": summary,
            })

        first_product_id = goods_metadata[0]['id'] if goods_metadata else None
        amount_value = f"{Decimal(summary['total']).quantize(Decimal('1')):.2f}"
        idempotence_key = uuid.uuid4()

        try:
            yookassa_metadata = self._build_yookassa_metadata(
                user=user,
                is_pickup=is_pickup,
                is_recipient_self=is_recipient_self,
                first_product_id=first_product_id,
                summary=summary,
                promocode=promocode,
            )
            payment = Payment.create({
                "amount": {
                    "value": amount_value,
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": PAYMENT_RETURN_URL
                },
                "capture": True,
                "description": f"Заказ от пользователя",
                "metadata": yookassa_metadata
            }, idempotence_key)
        except Exception as e:
            return Response({'error': f'Payment error: {str(e)}'}, status=500)

        confirmation_url = getattr(getattr(payment, 'confirmation', None), 'confirmation_url', None)
        if not confirmation_url:
            return Response({'error': 'Payment confirmation URL is missing'}, status=500)

        session = PaymentSession.objects.create(
            payment_id=payment.id,
            user=user,
            status=normalize_payment_status(payment.status),
            amount=Decimal(amount_value),
            phone=phone,
            address=address,
            is_pickup=is_pickup,
            is_recipient_self=is_recipient_self,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            delivery_date=delivery_date_value,
            delivery_time_slot=delivery_time_slot_value,
            comment=comment,
            promocode=promocode.promocode if promocode else '',
            goods=goods_metadata,
            summary=summary,
            confirmation_url=confirmation_url,
            telegram_chat_id=user.tg_id,
            reminder_due_at=timezone.now() + timedelta(minutes=max(0, _get_payment_reminder_settings()['delay_minutes'])),
        )

        pending_text = build_payment_status_text(session) + f"\n\nСсылка на оплату:\n{confirmation_url}"
        sent, message_id = send_telegram_payment_link(user.tg_id, pending_text, confirmation_url)
        if sent and message_id:
            session.telegram_message_id = message_id
            session.save(update_fields=['telegram_message_id', 'updated_at'])
            _schedule_payment_reminder(session.id, _get_payment_reminder_settings()['delay_minutes'])
        else:
            return Response({'error': 'Не удалось отправить ссылку в Telegram. Попробуйте снова.'}, status=500)

        return Response({
            "payment_id": payment.id,
            "payment_url_sent": True,
            "summary": summary,
        })

    
    @action(detail=False, methods=['post'])
    def check_payment_status(self, request):
        _dispatch_due_payment_reminders(limit=10)
        payment_id = request.data.get('payment_id')

        if not payment_id:
            return Response({'error': 'Missing payment_id'}, status=status.HTTP_400_BAD_REQUEST)
        tg_id = self.request.tg_user_data.get('tg_id')
        user = get_object_or_404(Users, tg_id=tg_id)

        payment_session = PaymentSession.objects.filter(payment_id=payment_id, user=user).select_related('order').first()
        if not payment_session:
            return Response({'error': 'Payment session not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            payment = Payment.find_one(payment_id)
            payment_session = sync_payment_session_status(payment_session, payment.status)
        except Exception:
            pass

        status_text_map = {
            PaymentSession.StatusEnum.PENDING: 'Ожидает оплаты',
            PaymentSession.StatusEnum.WAITING: 'Ожидает подтверждения',
            PaymentSession.StatusEnum.SUCCEEDED: 'Оплата прошла успешно',
            PaymentSession.StatusEnum.CANCELED: 'Платёж отменён',
        }

        response_data = {
            'status': payment_session.status.lower(),
            'status_text': status_text_map.get(payment_session.status, 'Неизвестный статус'),
            'paid': payment_session.status == PaymentSession.StatusEnum.SUCCEEDED,
            'amount': str(payment_session.amount),
            'currency': 'RUB',
            'order_id': payment_session.order_id,
            'track_number': payment_session.order.track_code if payment_session.order_id else None,
        }
        return Response(response_data)
        

    @action(detail=False, methods=['get'])
    def payment_success(self, request):
        tg_id = request.query_params.get('tg_id')
        if not tg_id:
            return Response({'error': 'tg_id is required'}, status=400)
        key = f'cart:{tg_id}'
        cart = cache.get(key, {})

        if not cart:
            return Response({'message': 'Корзина пуста'}, status=400)

        product_ids = list(map(int, cart.keys()))
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}

        for product_id, quantity in cart.items():
            product = product_map.get(product_id)
            if product:
                print(f"- {product.name} (x{quantity}) = {product.price * quantity}₽")

        cache.delete(key)

        return Response({'message': 'Оплата прошла успешно!'})
    
    @action(detail=False, methods=['post'])
    @csrf_exempt
    def add_to_cart(self, request):
        tg_id = str(self.request.tg_user_data['tg_id'])
        product_id = str(request.data.get('product_id'))
        try:
            quantity = int(request.data.get('quantity', 1))
        except (TypeError, ValueError):
            return Response({'error': 'Quantity must be integer'}, status=400)

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=400)
        if quantity <= 0:
            return Response({'error': 'Quantity must be positive'}, status=400)

        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({'error': 'Product not found'}, status=404)
        step = self._get_product_step(product)
        if quantity % step != 0:
            return Response({'error': f'Quantity must be a multiple of step ({step})'}, status=400)

        key = f'cart:{tg_id}'
        cart = cache.get(key, {})

        cart[product_id] = cart.get(product_id, 0) + quantity

        cache.set(key, cart, timeout=60 * 60 * 24 * 7)  # 7 дней
        snapshot = self._build_cart_snapshot(request, tg_id)
        return Response({'message': 'Product added to cart', **snapshot})

    @action(detail=False, methods=['post'])
    @csrf_exempt
    def remove_from_cart(self, request):
        tg_id = str(self.request.tg_user_data['tg_id'])
        product_id = str(request.data.get('product_id'))

        key = f'cart:{tg_id}'
        cart = cache.get(key, {})

        if product_id in cart:
            del cart[product_id]
            cache.set(key, cart, timeout=60 * 60 * 24 * 7)
            return Response({'message': 'Product removed from cart'})
        return Response({'error': 'Product not found in cart'}, status=404)

    @action(detail=False, methods=['get'])
    def get_cart(self, request):
        tg_id = str(self.request.tg_user_data['tg_id'])
        snapshot = self._build_cart_snapshot(request, tg_id)
        return Response(snapshot)
    
    @action(detail=False, methods=['post'])
    @csrf_exempt
    def clear_cart(self, request):
        tg_id = str(self.request.tg_user_data['tg_id'])
        key = f'cart:{tg_id}'
        cache.delete(key)
        return Response({'message': 'Cart cleared'}, status=200)
    
    @action(detail=False, methods=['post'])
    @csrf_exempt
    def update_cart(self, request):
        tg_id = str(self.request.tg_user_data['tg_id'])
        product_id = str(request.data.get('product_id'))
        try:
            quantity = int(request.data.get('quantity', 0))
        except (TypeError, ValueError):
            return Response({'error': 'Quantity must be integer'}, status=400)

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=400)

        key = f'cart:{tg_id}'
        cart = cache.get(key, {})

        if quantity <= 0:
            cart.pop(product_id, None)
        else:
            product = Product.objects.filter(id=product_id).first()
            if not product:
                return Response({'error': 'Product not found'}, status=404)
            step = self._get_product_step(product)
            if quantity % step != 0:
                return Response({'error': f'Quantity must be a multiple of step ({step})'}, status=400)
            cart[product_id] = quantity

        cache.set(key, cart, timeout=60 * 60 * 24 * 7)
        snapshot = self._build_cart_snapshot(request, tg_id)
        return Response({'message': 'Cart updated', **snapshot})

    @action(detail=False, methods=['post'], url_path='validate-promocode')
    def validate_promocode(self, request):
        from .models import Promocode, UsedPromocode

        promocode_text = request.data.get('promocode', '').strip().upper()
        tg_id = self.request.tg_user_data.get('tg_id', None)

        if not promocode_text:
            return Response({
                'valid': False,
                'message': 'Промокод не указан'
            }, status=400)

        if not tg_id:
            return Response({
                'valid': False,
                'message': 'Пользователь не авторизован'
            }, status=401)

        try:
            user = get_object_or_404(Users, tg_id=tg_id)

            try:
                promocode = Promocode.objects.get(promocode__iexact=promocode_text)
            except Promocode.DoesNotExist:
                return Response({
                    'valid': False,
                    'message': 'Промокод не найден или не существует'
                })

            already_used = UsedPromocode.objects.filter(
                user=user,
                promocode=promocode
            ).exists()

            if already_used:
                return Response({
                    'valid': False,
                    'message': 'Вы уже использовали этот промокод'
                })

            # Промокод валиден
            return Response({
                'valid': True,
                'promocode': promocode.promocode,
                'discount': promocode.discount,
                'message': f'Промокод применен! Скидка {promocode.discount}%'
            })

        except Exception as e:
            return Response({
                'valid': False,
                'message': f'Ошибка при проверке промокода: {str(e)}'
            }, status=500)

    @action(detail=False, methods=['post'], url_path='apply-promocode')
    def apply_promocode(self, request):
        promocode_text = request.data.get('promocode', '').strip().upper()
        tg_id = self.request.tg_user_data.get('tg_id')

        if not promocode_text or not tg_id:
            return Response({
                'success': False,
                'message': 'Некорректные данные'
            }, status=400)

        user = get_object_or_404(Users, tg_id=tg_id)
        promocode, discount_percent, promo_error = self._resolve_promocode(user, promocode_text)

        if promo_error:
            return Response({
                'success': False,
                'message': promo_error
            }, status=400)

        snapshot = self._build_cart_snapshot(request, str(tg_id), discount_percent=discount_percent)

        return Response({
            'success': True,
            'discount': discount_percent,
            'summary': snapshot['summary'],
            'promocode': promocode.promocode if promocode else ''
        })


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ['get']

    @action(detail=False, methods=['get'], url_path='get-product-details')
    def get_product_details(self, request):
        product_id = request.query_params.get('id', None)
        product = get_object_or_404(Product, id=product_id)
        serializer = self.get_serializer(product)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='recommended')
    def get_recommended(self, request):
        products = Product.objects.all()
        
        if products.count() < 4:
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
        
        products_annotated = products.annotate(
            avg_rating=Avg('reviews__stars'),
            review_count=Count('reviews')
        )
        
        top_rated = list(products_annotated.filter(review_count__gt=0).order_by('-avg_rating')[:2])
        top_rated_ids = [p.id for p in top_rated]
        
        most_reviewed = list(
            products_annotated.exclude(id__in=top_rated_ids)
            .filter(review_count__gt=0)
            .order_by('-review_count')[:2]
        )
        most_reviewed_ids = [p.id for p in most_reviewed]
        
        remaining = list(products.exclude(id__in=top_rated_ids + most_reviewed_ids))
        random.shuffle(remaining)
        
        result = top_rated + most_reviewed + remaining
        
        serializer = self.get_serializer(result, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='price-ascending')
    def get_by_price_asc(self, request):
        products = Product.objects.all().order_by('price')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='price-descending')
    def get_by_price_desc(self, request):
        products = Product.objects.all().order_by('-price')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class FavoritesViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritesSerializer
    http_method_names = ['get', 'post', 'delete']

    @staticmethod
    def _resolve_tg_id(request):
        tg_id = None
        user_data = getattr(request, 'tg_user_data', None)
        if isinstance(user_data, dict):
            tg_id = user_data.get('tg_id')
        if not tg_id:
            tg_id = request.headers.get('X-Tg-Id')
        if not tg_id:
            tg_id = request.data.get('tg_id') if hasattr(request, 'data') else None
        if not tg_id:
            tg_id = request.query_params.get('tg_id') if hasattr(request, 'query_params') else None
        return tg_id

    def get_queryset(self):
        tg_id = self._resolve_tg_id(self.request)

        if tg_id:
            user = Users.objects.filter(tg_id=tg_id).first()
            if user:
                return Favorites.objects.filter(user=user).select_related('product')
        return Favorites.objects.none()

    
    def create(self, request):
        init_data = request.headers.get('InitData', '')
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({'error': 'Invalid data'}, status=400)
        
        tg_id = self._resolve_tg_id(request)

        if tg_id:
            user = get_object_or_404(Users, tg_id=tg_id)

        if not user:
            return Response({'error': 'User not found'}, status=404)
        
        product = get_object_or_404(Product, id=product_id)
        
        favorite, created = Favorites.objects.get_or_create(
            user=user,
            product=product
        )
        
        if created:
            serializer = self.get_serializer(favorite)
            return Response(serializer.data, status=201)
        else:
            return Response({'message': 'Already in favorites'}, status=200)
    
    @action(detail=False, methods=['delete'], url_path='remove')
    def remove_favorite(self, request):
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response({'error': 'Invalid data'}, status=400)
        
        
        tg_id = self._resolve_tg_id(request)

        # Проверяем наличие tg_id
        if tg_id:
            # Ищем пользователя по tg_id
            user = get_object_or_404(Users, tg_id=tg_id)

        if not user:
            return Response({'error': 'User not found'}, status=404)
        
        favorite = Favorites.objects.filter(user=user, product_id=product_id).first()
        if favorite:
            favorite.delete()
            return Response({'message': 'Removed from favorites'}, status=200)
        else:
            return Response({'error': 'Not in favorites'}, status=404)
    
    @action(detail=False, methods=['post'], url_path='toggle-notification')
    def toggle_notification(self, request):
        """Включить/выключить уведомления о товарах в наличии"""
        init_data = request.headers.get('InitData', '')
        notification_enabled = request.data.get('notification_enabled', True)
        
        
        tg_id = self.request.tg_user_data.get('tg_id', None)

        # Проверяем наличие tg_id
        if tg_id:
            # Ищем пользователя по tg_id
            user = get_object_or_404(Users, tg_id=tg_id)

        if not user:
            return Response({'error': 'User not found'}, status=404)
        
        user.notification_liked = notification_enabled
        user.save()
        
        return Response({
            'message': 'Notification settings updated',
            'notification_liked': user.notification_liked
        })

class PosterViewSet(viewsets.ModelViewSet):
    queryset = Poster.objects.all()
    serializer_class = PosterSerializer
    http_method_names = ['get']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.order_by('name')
    serializer_class = CategorySerializer
    http_method_names = ['get']

    @action(detail=False, methods=['get'])
    def get_categories(self, request):
        categories = Category.objects.order_by('name')
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all() 
    serializer_class = OrdersSerializer
    http_method_names = ['get']

    def get_queryset(self):
        tg_id = str(self.request.tg_user_data.get('tg_id', None))

        if tg_id:
            user = Users.objects.filter(tg_id=tg_id).first()
            if user:
                return Orders.objects.filter(user=user).order_by('-order_date')[:50]

        return Orders.objects.none()

    @action(detail=False, methods=['get'])
    def recent_orders(self, request):
        tg_id = str(request.tg_user_data.get('tg_id', None))

        if tg_id:
            user = Users.objects.filter(tg_id=tg_id).first()
            if user:
                recent_orders = Orders.objects.filter(user=user).order_by('-order_date')[:50]
                serializer = self.get_serializer(recent_orders, many=True)
                return Response(serializer.data)

        return Response([])



class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post']
    
    def get_queryset(self):
        return Review.objects.all()
    
    def create(self, request):
        tg_id = self.request.tg_user_data.get('tg_id', None)

        if tg_id:
            user = get_object_or_404(Users, tg_id=tg_id)
        
        if not user:
            return Response({'error': 'User not found'}, status=404)
        
        order_id = request.data.get('order_id')
        order_item_id = request.data.get('order_item_id')
        product_id = request.data.get('product_id')
        text = request.data.get('text')
        stars = request.data.get('stars', 5)

        if not order_id or not text:
            return Response({'error': 'Missing required fields'}, status=400)

        order = get_object_or_404(Orders, id=order_id, user=user, status='DELIVERED')

        from .models import OrderItem

        if order_item_id:
            order_item = get_object_or_404(OrderItem, id=order_item_id, order=order)
            product = order_item.product

            existing_review = Review.objects.filter(
                user=user,
                order_item=order_item
            ).first()
        elif product_id:
            order_item = OrderItem.objects.filter(order=order, product_id=product_id).first()
            if not order_item:
                return Response({'error': 'Product not found in this order'}, status=404)
            product = order_item.product

            existing_review = Review.objects.filter(
                user=user,
                order_item=order_item
            ).first()
        else:
            return Response({'error': 'Either order_item_id or product_id is required'}, status=400)

        if existing_review:
            return Response(
                {'error': 'You have already reviewed this product'},
                status=400
            )

        review = Review.objects.create(
            user=user,
            order=order,
            order_item=order_item,
            product=product,
            name=user.name or user.telegram_username,
            text=text,
            stars=stars,
        )
        
        serializer = self.get_serializer(review)
        return Response(serializer.data, status=201)
    
    @action(detail=False, methods=['get'], url_path='check')
    def check_review(self, request):

        tg_id = str(self.request.tg_user_data['tg_id'])

        if tg_id:
            user = get_object_or_404(Users, tg_id=tg_id)
        order_id = request.query_params.get('order_id')
        order_item_id = request.query_params.get('order_item_id')

        if not user or not order_id:
            return Response({'has_review': False})

        try:
            order = Orders.objects.get(id=order_id, user=user)

            if order_item_id:
                from .models import OrderItem
                has_review = Review.objects.filter(
                    user=user,
                    order_item_id=order_item_id
                ).exists()
            else:
                has_review = Review.objects.filter(
                    user=user,
                    order=order
                ).exists()

            return Response({'has_review': has_review})
        except Orders.DoesNotExist:
            return Response({'has_review': False})


@csrf_exempt
@api_view(['POST'])
@permission_classes([])
def yookassa_webhook(request):
    _dispatch_due_payment_reminders(limit=10)
    payment_object = request.data.get('object', {})
    payment_id = payment_object.get('id')

    if not payment_id:
        return Response({'ok': False, 'error': 'missing payment id'}, status=400)

    payment_session = PaymentSession.objects.filter(payment_id=payment_id).select_related('order').first()
    if not payment_session:
        return Response({'ok': True}, status=200)

    try:
        payment = Payment.find_one(payment_id)
        sync_payment_session_status(payment_session, payment.status)
    except Exception:
        return Response({'ok': False}, status=400)

    return Response({'ok': True}, status=200)
