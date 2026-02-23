# management/commands/sync_moysklad_warehouses.py
from django.core.management.base import BaseCommand
from api.models import MoySkladWarehouse


class Command(BaseCommand):
    help = 'Синхронизирует склады из МойСклад'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю синхронизацию складов...')
        
        success = MoySkladWarehouse.sync_warehouses_from_moysklad()
        
        if success:
            count = MoySkladWarehouse.objects.filter(is_active=True).count()
            self.stdout.write(
                self.style.SUCCESS(f'✅ Успешно синхронизировано {count} складов')
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Ошибка при синхронизации складов')
            )