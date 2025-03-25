# prediction/management/commands/load_disaster_data.py
import pandas as pd
import os
import requests
from django.core.management.base import BaseCommand
from prediction.models import DisasterPrediction, Hospital

class Command(BaseCommand):
    help = 'Loads disaster prediction data from final_dataset.csv, geocodes locations, fetches nearby hospitals, and saves to the database'

    def handle(self, *args, **kwargs):
        # Path to the dataset
        dataset_path = os.path.join(os.path.dirname(__file__), '../../final_predictions.csv')
        df = pd.read_csv(dataset_path)

        # Google Maps API key
        GOOGLE_MAPS_API_KEY = 'AIzaSyB4y-YKK1KxniUfZC2PfFTlhjfCmi_tMuw'

        # Clear existing data
        DisasterPrediction.objects.all().delete()

        # Process each row in the dataset
        for index, row in df.iterrows():
            self.stdout.write(f"Processing row {index + 1}/{len(df)}: {row['Location']}")

            # Geocode the location to get latitude and longitude
            location = row['Location']
            geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GOOGLE_MAPS_API_KEY}"
            geocode_response = requests.get(geocode_url)

            latitude = None
            longitude = None
            if geocode_response.status_code == 200:
                geocode_data = geocode_response.json()
                if geocode_data['status'] == 'OK' and geocode_data['results']:
                    latitude = geocode_data['results'][0]['geometry']['location']['lat']
                    longitude = geocode_data['results'][0]['geometry']['location']['lng']
                else:
                    self.stdout.write(self.style.WARNING(f"Geocoding failed for {location}: {geocode_data['status']}"))
            else:
                self.stdout.write(self.style.ERROR(f"Geocoding request failed for {location}"))

            # Create the DisasterPrediction object
            prediction = DisasterPrediction(
                year=row['Year'],
                country=row['Country'],
                location=row['Location'],
                latitude=latitude,
                longitude=longitude,
                total_affected=row['Total Affected'],
                magnitude=row['Magnitude'],
                disaster_type=row['Disaster Type'],
            )
            prediction.save()

            # Fetch nearby hospitals if latitude and longitude are available
            if latitude and longitude:
                places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&radius=5000&type=hospital&key={GOOGLE_MAPS_API_KEY}"
                places_response = requests.get(places_url)

                if places_response.status_code == 200:
                    places_data = places_response.json()
                    if places_data['status'] == 'OK':
                        for place in places_data.get('results', [])[:5]:  # Limit to 5 hospitals per location
                            Hospital.objects.create(
                                disaster_prediction=prediction,
                                name=place['name'],
                                latitude=place['geometry']['location']['lat'],
                                longitude=place['geometry']['location']['lng'],
                                address=place.get('vicinity', ''),
                            )
                    else:
                        self.stdout.write(self.style.WARNING(f"Places API failed for {location}: {places_data['status']}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Places API request failed for {location}"))

        self.stdout.write(self.style.SUCCESS('Successfully loaded and processed disaster prediction data into the database.'))