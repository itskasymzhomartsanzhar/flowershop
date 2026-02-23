from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .models import Users, Product, Category, Orders
admin.site.unregister(Group)
admin.site.unregister(User)
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Orders, OrderItem, Users, Product, Category, Review, Favorites, Promocode, UsedPromocode, Poster, ServiceFeeSettings, PaymentSession, DeliverySettings, DeliveryTimeSlot, PaymentReminderSettings
# admin.py
from django.utils.html import format_html


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity_step', 'in_stock', 'display')
    list_filter = ('display', 'category')
    search_fields = ('name',)
    actions = ['enable_auto_sync', 'disable_auto_sync']
    

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']
    can_delete = False


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'price', 'status', 'is_pickup', 'is_recipient_self', 'delivery_date', 'delivery_time_slot', 'isreturn', 'order_date']
    list_filter = ['status', 'is_pickup', 'is_recipient_self', 'delivery_date', 'isreturn', 'order_date']
    search_fields = ['name', 'track_code', 'user__telegram_username']
    inlines = [OrderItemInline]

    """     def has_add_permission(self, request):
            return False

        def has_delete_permission(self, request, obj=None):
            return False
        """
    def response_change(self, request, obj):
        if "_return" in request.POST:
            obj.isreturn = True
            obj.save()

            messages.success(request, 'Возврат выполнен успешно')

            return HttpResponseRedirect(reverse('admin:api_orders_changelist'))

        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj._status_changed = True
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price']
    list_filter = ['order__status', 'order__order_date']
    search_fields = ['order__name', 'product__name']

# Регистрация остальных моделей
@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['tg_id', 'name', 'telegram_username', 'registered_time']
    search_fields = ['tg_id', 'name', 'telegram_username']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'order', 'order_item', 'stars', 'time']
    list_filter = ['stars', 'time']
    search_fields = ['name', 'product__name', 'order__name']

@admin.register(Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'time']

@admin.register(Promocode)
class PromocodeAdmin(admin.ModelAdmin):
    list_display = ['promocode', 'discount']

@admin.register(UsedPromocode)
class UsedPromocodeAdmin(admin.ModelAdmin):
    list_display = ['promocode', 'user']

@admin.register(Poster)
class PosterAdmin(admin.ModelAdmin):
    list_display = ['__str__']


@admin.register(ServiceFeeSettings)
class ServiceFeeSettingsAdmin(admin.ModelAdmin):
    list_display = ['percentage']

    def has_add_permission(self, request):
        if ServiceFeeSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    list_display = ['min_days_ahead', 'max_days_ahead']

    def has_add_permission(self, request):
        if DeliverySettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(DeliveryTimeSlot)
class DeliveryTimeSlotAdmin(admin.ModelAdmin):
    list_display = ['label', 'is_active', 'sort_order']
    list_filter = ['is_active']
    search_fields = ['label']


@admin.register(PaymentReminderSettings)
class PaymentReminderSettingsAdmin(admin.ModelAdmin):
    list_display = ['delay_minutes']

    def has_add_permission(self, request):
        if PaymentReminderSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(PaymentSession)
class PaymentSessionAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'user', 'status', 'amount', 'order', 'created_at']
    list_filter = ['status', 'created_at', 'is_pickup']
    search_fields = ['payment_id', 'user__tg_id', 'user__telegram_username']
    readonly_fields = ['payment_id', 'user', 'order', 'status', 'amount', 'phone', 'address', 'is_pickup', 'is_recipient_self', 'recipient_name', 'recipient_phone', 'delivery_date', 'delivery_time_slot', 'comment', 'promocode', 'goods', 'summary', 'confirmation_url', 'telegram_chat_id', 'telegram_message_id', 'assemblers_notified_at', 'reminder_due_at', 'reminder_sent_at', 'created_at', 'updated_at']
