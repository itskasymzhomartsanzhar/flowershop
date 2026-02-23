from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError



class Users(models.Model):

    tg_id = models.BigIntegerField('Telegram ID')
    name = models.CharField('Имя', max_length=400, null=True, blank=True)
    telegram_username = models.CharField('Никнейм', max_length=400, null=True, blank=True)
    address = models.CharField('Адрес', max_length=400, null=True, blank=True)
    registered_time = models.DateTimeField("Дата регистрации", auto_now_add=True)
    notification_promotion = models.BooleanField("Уведомление об Акциях и Новинках", default=True)
    notification_order_status = models.BooleanField("Уведомление о статусе заказа ", default=True)
    notification_liked = models.BooleanField("Уведомление о новинках избранных", default=True)
    is_superuser = models.BooleanField("Суперпользователь (Админ)", default=False)

    list_per_page = 500

    def __str__(self):
        return f'{self.tg_id}'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Poster(models.Model):
    poster = models.ImageField('Постер', upload_to='poster')

    list_per_page = 500

    def __str__(self):
        return f'Постер'

    class Meta:
        verbose_name = 'Постер'
        verbose_name_plural = 'Постер'

class Category(models.Model):
    
    name = models.CharField('Название', max_length=300, null=True, blank=True)

    list_per_page = 500

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Promocode(models.Model):
    
    promocode = models.CharField('Промокод', max_length=100, null=True, blank=True)
    discount = models.BigIntegerField('Процент скидки в %', default=0, null=True)

    list_per_page = 500

    def __str__(self):
        return f'{self.promocode} / -{self.discount}%'

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'


class ServiceFeeSettings(models.Model):
    percentage = models.PositiveSmallIntegerField('Процент сервисного сбора', default=10)

    def clean(self):
        if self.percentage > 100:
            raise ValidationError({'percentage': 'Процент не может быть больше 100'})

    def save(self, *args, **kwargs):
        if not self.pk and ServiceFeeSettings.objects.exists():
            raise ValidationError('Можно создать только одну запись сервисного сбора')
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Сервисный сбор: {self.percentage}%'

    class Meta:
        verbose_name = 'Сервисный сбор'
        verbose_name_plural = 'Сервисный сбор'


class DeliverySettings(models.Model):
    min_days_ahead = models.PositiveSmallIntegerField('Минимум дней до доставки', default=0)
    max_days_ahead = models.PositiveSmallIntegerField('Максимум дней до доставки', default=14)

    def clean(self):
        if self.max_days_ahead < self.min_days_ahead:
            raise ValidationError({'max_days_ahead': 'Максимум не может быть меньше минимума'})
        if self.max_days_ahead > 90:
            raise ValidationError({'max_days_ahead': 'Максимум не может быть больше 90'})

    def save(self, *args, **kwargs):
        if not self.pk and DeliverySettings.objects.exists():
            raise ValidationError('Можно создать только одну запись настроек доставки')
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Доставка: {self.min_days_ahead}-{self.max_days_ahead} дней'

    class Meta:
        verbose_name = 'Настройки отложенной доставки'
        verbose_name_plural = 'Настройки отложенной доставки'


class DeliveryTimeSlot(models.Model):
    label = models.CharField('Слот времени', max_length=32, unique=True)
    is_active = models.BooleanField('Активен', default=True)
    sort_order = models.PositiveSmallIntegerField('Порядок', default=0)

    def clean(self):
        if not self.label:
            raise ValidationError({'label': 'Слот времени обязателен'})

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Слот времени доставки'
        verbose_name_plural = 'Слоты времени доставки'
        ordering = ['sort_order', 'label']


class PaymentReminderSettings(models.Model):
    message_text = models.TextField(
        'Текст напоминания',
        default='Напоминаем: заказ #{order_number} ожидает оплату. Сумма: {amount} ₽.\nОплатить: {payment_url}'
    )
    delay_minutes = models.PositiveSmallIntegerField('Отправить через X минут', default=15)

    def clean(self):
        if self.delay_minutes > 1440:
            raise ValidationError({'delay_minutes': 'Значение не может быть больше 1440 минут'})

    def save(self, *args, **kwargs):
        if not self.pk and PaymentReminderSettings.objects.exists():
            raise ValidationError('Можно создать только одну запись настроек напоминания')
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Напоминание об оплате: через {self.delay_minutes} мин'

    class Meta:
        verbose_name = 'Напоминание об оплате'
        verbose_name_plural = 'Напоминание об оплате'


class UsedPromocode(models.Model):
    
    promocode = models.ForeignKey(Promocode, on_delete=models.CASCADE, null=True, related_name='used_promocodes')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, related_name='used_promocodes')


    list_per_page = 500

    def __str__(self):
        return f'{self.promocode.promocode} - @{self.user.telegram_username}'

    class Meta:
        verbose_name = 'Использованный промокод'
        verbose_name_plural = 'Использованные промокоды'

# models.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)




class Product(models.Model):
    
    name = models.CharField('Название', max_length=400, null=True, blank=True)
    photo1 = models.ImageField('Фотография 1', null=True, upload_to='product')
    photo2 = models.ImageField('Фотография 2', null=True, upload_to='product', blank=True)
    photo3 = models.ImageField('Фотография 3', null=True, upload_to='product', blank=True)
    photo4 = models.ImageField('Фотография 4', null=True, upload_to='product', blank=True)
    photo5 = models.ImageField('Фотография 5', null=True, upload_to='product', blank=True)
    photo6 = models.ImageField('Фотография 6', null=True, upload_to='product', blank=True)
    photo7 = models.ImageField('Фотография 7', null=True, upload_to='product', blank=True)
    photo8 = models.ImageField('Фотография 8', null=True, upload_to='product', blank=True)
    photo9 = models.ImageField('Фотография 9', null=True, upload_to='product', blank=True)
    photo10 = models.ImageField('Фотография 10', null=True, upload_to='product', blank=True)
    description = models.TextField('Описание', null=True, blank=True)
    price = models.BigIntegerField('Цена', default=0, null=True)
    oldprice = models.BigIntegerField('Прошлая цена', default=0, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, related_name='products')
    flug_new = models.BooleanField("Флаг Новинки", default=False)
    flug_popular = models.BooleanField("Флаг популярно", default=False)
    display = models.BooleanField("Показывать", default=True)
    in_stock = models.BigIntegerField('Количество на складе', null=True, blank=True)
    quantity_step = models.PositiveIntegerField('Шаг количества', default=1)
    

    
    list_per_page = 250
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
    
    def __str__(self):
        return self.name or 'Без названия'
    
    def get_photos(self):
        photos = []
        for i in range(1, 11):
            photo = getattr(self, f'photo{i}')
            if photo:
                photos.append(photo)
        return photos






class Review(models.Model):

    name = models.CharField('Имя', max_length=400, null=True, blank=True)
    text = models.TextField('Текст отзыва', null=True, blank=True)
    stars = models.BigIntegerField('Количество звезд', default=5, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    order = models.ForeignKey('Orders', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    order_item = models.ForeignKey('OrderItem', on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, related_name='reviews')
    time = models.DateField("Дата и время", auto_now_add=True)


    list_per_page = 250

    def __str__(self):
        return f'{self.name} / {self.stars} / {self.product.name if self.product else "Без продукта"}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Favorites(models.Model):
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, related_name='favorites')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, related_name='favorites')
    time = models.DateField("Дата и время", auto_now_add=True)


    list_per_page = 250

    def __str__(self):
        return f'{self.user.telegram_username} - {self.product.name}'

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'



class Orders(models.Model):
    class StatusEnum(models.TextChoices):
        PAID = 'PAID', _('Оплачен')
        ASSEMBLING = 'ASSEMBLING', _('Собирается ')
        ONTHEWAY = 'ONTHEWAY', _('В пути')
        DELIVERED = 'DELIVERED', _('Доставлено')

    name = models.CharField('Название', max_length=400, null=True, blank=True)
    track_code = models.CharField('Трек номер', max_length=400, null=True, blank=True)
    photo = models.ImageField('Фотография', null=True, upload_to='orders', blank=True)
    price = models.BigIntegerField('Цена', default=0, null=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, related_name='orders')
    order_date = models.DateTimeField("Дата и время оформления", auto_now_add=True)
    status = models.CharField('Статус', choices=StatusEnum.choices, null=True, blank=True ,max_length=350)
    isreturn = models.BooleanField('Возврат', default=False)
    is_pickup = models.BooleanField('Самовывоз', default=False)
    is_recipient_self = models.BooleanField('Заказчик является получателем', default=True)
    recipient_name = models.CharField('Имя получателя', max_length=255, blank=True)
    recipient_phone = models.CharField('Телефон получателя', max_length=64, blank=True)
    delivery_date = models.DateField('Дата доставки', null=True, blank=True)
    delivery_time_slot = models.CharField('Временной слот доставки', max_length=32, null=True, blank=True)

    # Связь многие-ко-многим с продуктами через промежуточную модель
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')

    delivery_address = models.TextField('Адрес доставки', null=True, blank=True)

    list_per_page = 250



    def __str__(self):
        return f'{self.name} - {self.price} ₽'

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField('Количество', default=1)
    price = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.order.name} - {self.product.name} x{self.quantity}'

    class Meta:
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'


class PaymentSession(models.Model):
    class StatusEnum(models.TextChoices):
        PENDING = 'PENDING', 'Ожидает оплаты'
        SUCCEEDED = 'SUCCEEDED', 'Оплачен'
        CANCELED = 'CANCELED', 'Отменен'
        WAITING = 'WAITING', 'Ожидает подтверждения'

    payment_id = models.CharField(max_length=128, unique=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='payment_sessions')
    order = models.ForeignKey(Orders, on_delete=models.SET_NULL, null=True, blank=True, related_name='payment_sessions')
    status = models.CharField(max_length=32, choices=StatusEnum.choices, default=StatusEnum.PENDING)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    phone = models.CharField(max_length=64, blank=True)
    address = models.TextField(blank=True)
    is_pickup = models.BooleanField(default=False)
    is_recipient_self = models.BooleanField(default=True)
    recipient_name = models.CharField(max_length=255, blank=True)
    recipient_phone = models.CharField(max_length=64, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time_slot = models.CharField(max_length=32, blank=True)
    comment = models.TextField(blank=True)
    promocode = models.CharField(max_length=100, blank=True)
    goods = models.JSONField(default=list)
    summary = models.JSONField(default=dict)
    confirmation_url = models.TextField(blank=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    telegram_message_id = models.BigIntegerField(null=True, blank=True)
    assemblers_notified_at = models.DateTimeField(null=True, blank=True)
    reminder_due_at = models.DateTimeField(null=True, blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.payment_id} ({self.status})'

    class Meta:
        verbose_name = 'Платежная сессия'
        verbose_name_plural = 'Платежные сессии'
