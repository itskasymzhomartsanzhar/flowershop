from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0026_add_sort_order_product_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="deliverysettings",
            name="delivery_fee",
            field=models.PositiveIntegerField(default=0, verbose_name="Стоимость доставки"),
        ),
    ]
