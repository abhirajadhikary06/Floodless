from django.core.management.base import BaseCommand
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from dashboard.models import Calamity
import os

class Command(BaseCommand):
    help = 'Loads calamity data from dataset.csv into the database'

    def handle(self, *args, **options):
        file_path = os.path.join(os.path.dirname(__file__), '../../dataset_5y.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found at {file_path}"))
            return

        df = pd.read_csv(file_path)
        self.stdout.write("Dataset loaded: " + str(df.head()))
        df.columns = ['Year', 'Disaster Type', 'Country', 'Region', 'Location']

        df = df[(df['Year'] >= 2000) & (df['Year'] <= 2025)]

        geolocator = Nominatim(user_agent="floodless_dashboard")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

        Calamity.objects.all().delete()

        calamities_to_save = []
        for _, row in df.iterrows():
            location_str = row['Location'
            '']
            location = geocode(location_str)
            latitude = location.latitude if location else None
            longitude = location.longitude if location else None
            self.stdout.write(f"Geocoded {location_str}: Lat={latitude}, Long={longitude}")

            if not Calamity.objects.filter(
                year=row['Year'],
                calamity_type=row['Disaster Type'],
                country=row['Country'],
                region=row['Region'],
                location=row['Location']
            ).exists():
                calamities_to_save.append(
                    Calamity(
                        year=row['Year'],
                        calamity_type=row['Disaster Type'].lower(),
                        country=row['Country'],
                        region=row['Region'],
                        location=row['Location'],
                        latitude=latitude,
                        longitude=longitude
                    )
                )

        if calamities_to_save:
            Calamity.objects.bulk_create(calamities_to_save)
            self.stdout.write(self.style.SUCCESS(f"Saved {len(calamities_to_save)} calamities"))