from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0024_orders_comment_orders_payer_name_orders_payer_phone_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orders",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("PENDING_PAYMENT", "Ожидает оплаты"),
                    ("PLACED", "Оформление"),
                    ("ASSEMBLING_STARTED", "Сборка начата"),
                    ("ASSEMBLING_DONE", "Сборка готова"),
                    ("COURIER_PICKED", "Курьер забрал"),
                    ("DELIVERING", "Доставка"),
                    ("READY_FOR_PICKUP", "Готов к выдаче"),
                    ("ISSUED", "Выдан"),
                    ("PAID", "Оплачен"),
                    ("ASSEMBLING", "Собирается "),
                    ("ONTHEWAY", "В пути"),
                    ("DELIVERED", "Доставлено"),
                ],
                max_length=350,
                null=True,
                verbose_name="Статус",
            ),
        ),
    ]
