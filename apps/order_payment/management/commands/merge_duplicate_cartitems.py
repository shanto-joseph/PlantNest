from django.core.management.base import BaseCommand
from apps.order_payment.models import CartItem
from django.db.models import Count

class Command(BaseCommand):
    help = 'Merge duplicate CartItem rows for each (cart, product) pair.'

    def handle(self, *args, **options):
        duplicates = (
            CartItem.objects
            .values('cart', 'product')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )
        total_merged = 0
        for dup in duplicates:
            cart = dup['cart']
            product = dup['product']
            items = CartItem.objects.filter(cart=cart, product=product).order_by('id')
            main_item = items.first()
            duplicate_items = items[1:]
            total_quantity = sum(item.quantity for item in items)
            main_item.quantity = total_quantity
            main_item.save()
            for item in duplicate_items:
                item.delete()
            total_merged += len(duplicate_items)
            self.stdout.write(f"Merged {len(duplicate_items)} duplicates for cart={cart}, product={product}")
        self.stdout.write(self.style.SUCCESS(f"Done. Total duplicates merged: {total_merged}")) 