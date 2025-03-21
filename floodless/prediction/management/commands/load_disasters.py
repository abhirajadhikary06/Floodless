import pandas as pd
from django.core.management.base import BaseCommand
from predication.models import Disaster
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Load disaster data from dataset.csv and geocode locations'

    def handle(self, *args, **kwargs):
        # Path to dataset.csv (assumed to be in predication directory)
        dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dataset.csv')

        # Check if the file exists
        if not os.path.exists(dataset_path):
            self.stdout.write(self.style.ERROR('dataset.csv not found in predication directory.'))
            return

        # Read the CSV file
        try:
            df = pd.read_csv(dataset_path)
            self.stdout.write(self.style.SUCCESS(f'Loaded dataset.csv with {len(df)} rows.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading dataset.csv: {str(e)}'))
            return

        # Initialize the geocoder with rate limiting
        geolocator = Nominatim(user_agent="floodless_predication")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)  # 1-second delay to respect Nominatim's usage policy

        # Clear existing data (optional, comment out if you want to append)
        Disaster.objects.all().delete()
        self.stdout.write(self.style.WARNING('Cleared existing Disaster records.'))

        # Process each row
        for index, row in df.iterrows():
            location = row['Location']
            self.stdout.write(f'Processing {location} ({index + 1}/{len(df)})')

            # Geocode the location
            try:
                # Combine location, region, and country for better geocoding accuracy
                full_location = f"{location}, {row['Region']}, {row['Country']}"
                location_data = geocode(full_location)

                if location_data:
                    latitude = location_data.latitude
                    longitude = location_data.longitude
                    self.stdout.write(self.style.SUCCESS(f'Geocoded {full_location}: ({latitude}, {longitude})'))
                else:
                    latitude = None
                    longitude = None
                    self.stdout.write(self.style.WARNING(f'Could not geocode {full_location}.'))
            except Exception as e:
                latitude = None
                longitude = None
                self.stdout.write(self.style.WARNING(f'Error geocoding {full_location}: {str(e)}'))

            # Create and save the Disaster object
            disaster = Disaster(
                year=row['Year'],
                disaster_type=row['Disaster Type'],
                country=row['Country'],
                region=row['Region'],
                location=row['Location'],
                latitude=latitude,
                longitude=longitude
            )
            disaster.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {len(df)} disaster records into the database.'))