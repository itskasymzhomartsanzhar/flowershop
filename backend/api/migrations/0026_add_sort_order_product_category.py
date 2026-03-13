from django.db import migrations, models


def fill_sort_order(apps, schema_editor):
    Category = apps.get_model("api", "Category")
    Product = apps.get_model("api", "Product")

    for category in Category.objects.all():
        if not category.sort_order:
            category.sort_order = category.id
            category.save(update_fields=["sort_order"])

    for product in Product.objects.all():
        if not product.sort_order:
            product.sort_order = product.id
            product.save(update_fields=["sort_order"])


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0025_alter_orders_status_pending_payment"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Порядок"),
        ),
        migrations.AddField(
            model_name="product",
            name="sort_order",
            field=models.PositiveIntegerField(default=0, verbose_name="Порядок"),
        ),
        migrations.RunPython(fill_sort_order, migrations.RunPython.noop),
    ]
