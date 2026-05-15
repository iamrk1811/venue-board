import random
import time
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from transactions.const import TransactionTypes
from transactions.serializers import TransactionIngestSerializer
from transactions.services import TransactionService
from venues.models import Venue

MENUS = {
    "pub": [
        ("beer_pint", "Pint of Lager", Decimal("5.50")),
        ("beer_pint_ale", "Pint of Ale", Decimal("5.20")),
        ("wine_glass", "Glass of House Wine", Decimal("6.50")),
        ("spirits_single", "Single Spirit & Mixer", Decimal("7.00")),
        ("burger", "Beef Burger", Decimal("14.00")),
        ("fish_chips", "Fish & Chips", Decimal("15.50")),
        ("nachos", "Nachos", Decimal("8.00")),
        ("soft_drink", "Soft Drink", Decimal("3.50")),
    ],
    "restaurant": [
        ("starter", "Seasonal Starter", Decimal("9.50")),
        ("main_chicken", "Grilled Chicken", Decimal("18.00")),
        ("main_fish", "Pan-Fried Fish", Decimal("22.00")),
        ("main_steak", "Sirloin Steak", Decimal("28.00")),
        ("main_veggie", "Vegetarian Main", Decimal("16.00")),
        ("dessert", "Dessert of the Day", Decimal("8.50")),
        ("wine_bottle", "Bottle of Wine", Decimal("32.00")),
        ("soft_drink", "Soft Drink", Decimal("4.00")),
        ("coffee", "Coffee", Decimal("3.50")),
    ],
    "function_space": [
        ("canape", "Canapés (per person)", Decimal("12.00")),
        ("buffet_main", "Buffet Main Course", Decimal("25.00")),
        ("dessert_buffet", "Dessert Buffet", Decimal("10.00")),
        ("wine_bottle", "Bottle of Wine", Decimal("35.00")),
        ("champagne", "Bottle of Champagne", Decimal("55.00")),
        ("soft_drink_jug", "Soft Drink Jug", Decimal("8.00")),
        ("coffee_station", "Coffee Station (per person)", Decimal("6.00")),
    ],
}

WEIGHTS = {
    "pub": [30, 15, 15, 10, 10, 8, 7, 5],
    "restaurant": [15, 20, 15, 10, 10, 10, 10, 5, 5],
    "function_space": [20, 25, 15, 15, 10, 10, 5],
}

TXN_TYPES = [TransactionTypes.SALE, TransactionTypes.VOID, TransactionTypes.REFUND]
TXN_WEIGHTS = [80, 12, 8]

# Map VenueTypes int to menu key
VENUE_TYPE_MENU = {1: "pub", 2: "restaurant", 3: "function_space"}


def pick_items(venue_type_int: int, is_sale: bool) -> list[dict]:
    if not is_sale:
        return []
    menu_key = VENUE_TYPE_MENU.get(venue_type_int, "pub")
    menu = MENUS[menu_key]
    weights = WEIGHTS[menu_key]
    n_items = random.choices([1, 2, 3, 4], weights=[40, 35, 15, 10])[0]
    chosen = random.choices(menu, weights=weights, k=n_items)
    return [
        {
            "item_id": item[0],
            "name": item[1],
            "qty": random.choices([1, 2, 3], weights=[70, 20, 10])[0],
            "price": item[2],
        }
        for item in chosen
    ]


def build_payload(venue, occurred_at) -> dict:
    txn_type = random.choices(TXN_TYPES, weights=TXN_WEIGHTS)[0]
    is_sale = txn_type == TransactionTypes.SALE
    items = pick_items(venue.type, is_sale)
    if items:
        total = sum(Decimal(str(i["price"])) * i["qty"] for i in items)
    else:
        total = Decimal(str(round(random.uniform(8, 80), 2)))

    staff_num = random.randint(1, 5)
    return {
        "venue_id": venue.id,
        "timestamp": occurred_at.isoformat(),
        "type": txn_type,
        "items": items,
        "total": str(total),
        "staff_id": f"staff_{venue.id:03d}_{staff_num:02d}",
    }


def ingest(data: dict, stderr) -> bool:
    serializer = TransactionIngestSerializer(data=data)
    if not serializer.is_valid():
        stderr.write(f"Validation error: {serializer.errors}")
        return False
    TransactionService.ingest(serializer.validated_data)
    return True


class Command(BaseCommand):
    help = "Continuously generate realistic POS transactions across all venues"

    def add_arguments(self, parser):
        parser.add_argument("--rate", type=float, default=2.0, help="Transactions per second (default: 2)")
        parser.add_argument("--duration", type=int, default=0, help="Run for N seconds (0 = indefinitely)")
        parser.add_argument(
            "--backfill",
            type=int,
            default=0,
            metavar="HOURS",
            help="Before live simulation, seed N hours of historical data (e.g. --backfill 24)",
        )

    def handle(self, *_, **options):
        rate = options["rate"]
        duration = options["duration"]
        backfill_hours = options["backfill"]
        interval = 1.0 / rate

        venues = list(Venue.objects.all())
        if not venues:
            self.stderr.write("No venues found. Run seed_venues first.")
            return

        # backfill historical data
        if backfill_hours > 0:
            self.stdout.write(f"Backfilling {backfill_hours}h of historical data...")
            now = timezone.now()
            # 10 transactions per hour per venue
            txns_per_hour = 10
            count = 0
            for h in range(backfill_hours, 0, -1):
                hour_start = now - timedelta(hours=h)
                for venue in venues:
                    for _ in range(txns_per_hour):
                        offset = random.uniform(0, 3599)
                        occurred_at = hour_start + timedelta(seconds=offset)
                        try:
                            ingest(build_payload(venue, occurred_at), self.stderr)
                            count += 1
                        except Exception as e:
                            self.stderr.write(f"Backfill error: {e}")
            self.stdout.write(self.style.SUCCESS(f"Backfill done: {count} transactions."))


        # simulation
        self.stdout.write(self.style.SUCCESS(
            f"Simulator started: {rate} txn/s across {len(venues)} venues"
            + (f" for {duration}s" if duration else " (indefinitely)")
        ))

        start = time.time()
        count = 0

        while True:
            if duration and (time.time() - start) >= duration:
                break

            venue = random.choice(venues)
            try:
                ingest(build_payload(venue, timezone.now()), self.stderr)
                count += 1
                if count % 50 == 0:
                    self.stdout.write(f"  {count} transactions generated...")
            except Exception as e:
                self.stderr.write(f"Error: {e}")

            time.sleep(interval)

        self.stdout.write(self.style.SUCCESS(f"Simulator done. {count} transactions generated."))
