from rest_framework import serializers  # type: ignore
from django.conf import settings
from .models import Users, Product, Category, Orders, OrderItem, Review, Poster, Favorites, Promocode, UsedPromocode


def build_media_url(file_or_url, request):
    try:
        if not file_or_url:
            return None

        if isinstance(file_or_url, str):
            url = file_or_url
        else:
            url = file_or_url.url

        if not url:
            return None

        if url.startswith('/') and request:
            absolute_url = request.build_absolute_uri(url)
        else:
            absolute_url = url

        if settings.FORCE_HTTPS_MEDIA and absolute_url.startswith('http://'):
            return absolute_url.replace('http://', 'https://', 1)

        return absolute_url
    except (ValueError, AttributeError):
        return None


class PosterSerializer(serializers.ModelSerializer):
    poster = serializers.SerializerMethodField()

    class Meta:
        model = Poster
        fields = '__all__'

    def get_poster(self, obj):
        return build_media_url(obj.poster, self.context.get('request'))


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'name', 'text', 'stars', 'time', 'product', 'order', 'order_item', 'user']


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    # Или можно добавить средний рейтинг и количество отзывов
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()

    # Переопределяем все поля фотографий для конвертации в HTTPS
    photo1 = serializers.SerializerMethodField()
    photo2 = serializers.SerializerMethodField()
    photo3 = serializers.SerializerMethodField()
    photo4 = serializers.SerializerMethodField()
    photo5 = serializers.SerializerMethodField()
    photo6 = serializers.SerializerMethodField()
    photo7 = serializers.SerializerMethodField()
    photo8 = serializers.SerializerMethodField()
    photo9 = serializers.SerializerMethodField()
    photo10 = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'photo1', 'photo2', 'photo3', 'photo4', 'photo5',
                  'photo6', 'photo7', 'photo8', 'photo9', 'photo10',
                  'description', 'price', 'oldprice', 'category', 'category_name',
                  'flug_new', 'flug_popular', 'in_stock', 'quantity_step', 'reviews', 'average_rating', 'reviews_count']

    def _convert_to_https(self, photo_field):
        return build_media_url(photo_field, self.context.get('request'))

    def get_photo1(self, obj):
        return self._convert_to_https(obj.photo1)

    def get_photo2(self, obj):
        return self._convert_to_https(obj.photo2)

    def get_photo3(self, obj):
        return self._convert_to_https(obj.photo3)

    def get_photo4(self, obj):
        return self._convert_to_https(obj.photo4)

    def get_photo5(self, obj):
        return self._convert_to_https(obj.photo5)

    def get_photo6(self, obj):
        return self._convert_to_https(obj.photo6)

    def get_photo7(self, obj):
        return self._convert_to_https(obj.photo7)

    def get_photo8(self, obj):
        return self._convert_to_https(obj.photo8)

    def get_photo9(self, obj):
        return self._convert_to_https(obj.photo9)

    def get_photo10(self, obj):
        return self._convert_to_https(obj.photo10)

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return round(sum(r.stars for r in reviews) / reviews.count(), 1)
        return round(5.0, 1)

    def get_reviews_count(self, obj):
        return obj.reviews.count()
    
class FavoritesSerializer(serializers.ModelSerializer):
    product_info = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = Favorites
        fields = ['id', 'product', 'user', 'time', 'product_info']
        read_only_fields = ['user', 'time']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductSerializer(source='product', read_only=True)
    has_review = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_info', 'quantity', 'price', 'has_review']

    def get_has_review(self, obj):
        # Проверяем, есть ли отзыв на этот товар
        user = self.context.get('request').tg_user_data if hasattr(self.context.get('request'), 'tg_user_data') else None
        if user:
            from .models import Users
            try:
                tg_id = str(user.get('tg_id'))
                user_obj = Users.objects.get(tg_id=tg_id)
                return Review.objects.filter(user=user_obj, order_item=obj).exists()
            except:
                return False
        return False


class OrdersSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Orders
        fields = ['id', 'name', 'track_code', 'photo', 'price',
                  'user', 'order_date', 'status', 'isreturn', 'is_pickup', 'is_recipient_self',
                  'recipient_name', 'recipient_phone', 'delivery_date', 'delivery_time_slot',
                  'delivery_address', 'order_items']

    def get_photo(self, obj):
        return build_media_url(obj.photo, self.context.get('request'))


class PromocodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promocode
        fields = ['id', 'promocode', 'discount']


class UsedPromocodeSerializer(serializers.ModelSerializer):
    promocode_info = PromocodeSerializer(source='promocode', read_only=True)

    class Meta:
        model = UsedPromocode
        fields = ['id', 'promocode', 'user', 'promocode_info']
