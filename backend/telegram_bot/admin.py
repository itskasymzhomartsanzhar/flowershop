from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from asgiref.sync import sync_to_async
from django.db.models import Count, Sum, Avg, Q, Max, Min, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta
from api.models import Users, Product, Orders, Review, Favorites, Promocode, UsedPromocode, OrderItem

admin_router = Router()

