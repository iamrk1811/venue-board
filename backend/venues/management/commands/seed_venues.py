from django.core.management.base import BaseCommand
from venues.models import Venue

VENUES = [
    ("Skyline Lounge", 1, "Mumbai, Maharashtra"),
    ("Royal Orchid Banquet", 2, "Bengaluru, Karnataka"),
    ("Blue Moon Pub", 3, "Kolkata, West Bengal"),
    ("Palm Tree Restaurant", 1, "Chennai, Tamil Nadu"),
    ("Golden Spoon Cafe", 2, "Pune, Maharashtra"),
    ("Velvet Nights Club", 3, "Hyderabad, Telangana"),
    ("Emerald Banquets", 1, "Jaipur, Rajasthan"),
    ("Urban Tandoor", 2, "Bhubaneswar, Odisha"),
    ("Sunset Rooftop Bar", 3, "Ahmedabad, Gujarat"),
    ("Lakeview Dining", 1, "Lucknow, Uttar Pradesh"),
    ("The Rustic Fork", 2, "Kochi, Kerala"),
    ("Crystal Palace Hall", 3, "Indore, Madhya Pradesh"),
    ("Olive Garden Bistro", 1, "Surat, Gujarat"),
    ("Moonlight Events", 2, "Patna, Bihar"),
    ("Silver Oak Lounge", 3, "Chandigarh, Punjab"),
    ("The Grand Feast", 1, "Amritsar, Punjab"),
    ("Vintage Barrel Pub", 2, "Noida, Uttar Pradesh"),
    ("Coral Banquet Hall", 3, "Visakhapatnam, Andhra Pradesh"),
    ("Spice Symphony", 1, "Bhopal, Madhya Pradesh"),
    ("Pearl View Restaurant", 2, "Thiruvananthapuram, Kerala"),
    ("Fusion Fiesta", 3, "Nagpur, Maharashtra"),
    ("Red Velvet Lounge", 1, "Howrah, West Bengal"),
    ("The Celebration Hub", 2, "Mysuru, Karnataka"),
    ("Gardenia Function Hall", 3, "Srinagar, Jammu and Kashmir"),
    ("Midnight Brew Pub", 1, "Ludhiana, Punjab"),
    ("Royal Crown Banquet", 2, "Durgapur, West Bengal"),
    ("Flavors of India", 3, "Kanpur, Uttar Pradesh"),
    ("The Urban Plate", 1, "Madurai, Tamil Nadu"),
    ("Majestic Event Space", 2, "Dehradun, Uttarakhand"),
    ("The Happy Fork", 3, "Faridabad, Haryana"),
    ("City Lights Rooftop", 1, "Nashik, Maharashtra"),
    ("Orchid Elite Hall", 2, "Siliguri, West Bengal"),
    ("Bamboo House Restaurant", 3, "Mangaluru, Karnataka"),
    ("Heavenly Gatherings", 1, "Ranchi, Jharkhand"),
    ("Twilight Tavern", 2, "Guwahati, Assam"),
    ("The Sapphire Room", 3, "Varanasi, Uttar Pradesh"),
    ("Starline Banquets", 1, "Raipur, Chhattisgarh"),
    ("Cinnamon Spice Cafe", 2, "Agartala, Tripura"),
    ("Infinity Lounge & Bar", 3, "Aurangabad, Maharashtra"),
    ("Lotus Grand Events", 1, "Vadodara, Gujarat"),
]


class Command(BaseCommand):
    help = "Seed 40 venues and create admin user"

    def handle(self, *args, **options):
        created_count = 0
        for name, vtype, location in VENUES:
            _, created = Venue.objects.get_or_create(
                name=name,
                defaults={"type": vtype, "location": location},
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {created_count} new venues ({Venue.objects.count()} total)"))
