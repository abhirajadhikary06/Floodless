from django.shortcuts import render
from django.core.cache import cache
import pandas as pd
import requests
import json
from .models import Calamity
import os

def load_and_process_data():
    file_path = os.path.join(os.path.dirname(__file__), 'dataset.xls')
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return []

    df = pd.read_excel(file_path)
    print("Dataset loaded:", df.head())
    df.columns = ['Year', 'Disaster Type', 'Country', 'Region', 'Location']

    df = df[(df['Year'] >= 2000) & (df['Year'] <= 2025)]

    Calamity.objects.all().delete()

    calamities_to_save = []
    GOOGLE_MAPS_API_KEY = "AIzaSyB4y-YKK1KxniUfZC2PfFTlhjfCmi_tMuw"
    GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

    for _, row in df.iterrows():
        location_str = f"{row['Location']}, {row['Region']}, {row['Country']}"
        response = requests.get(GEOCODING_URL, params={
            "address": location_str,
            "key": GOOGLE_MAPS_API_KEY
        })

        latitude, longitude = None, None
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK":
                latitude = data["results"][0]["geometry"]["location"]["lat"]
                longitude = data["results"][0]["geometry"]["location"]["lng"]
                print(f"Geocoded {location_str}: Lat={latitude}, Long={longitude}")
            else:
                print(f"Failed to geocode {location_str}: {data['status']}")
        else:
            print(f"Failed to geocode {location_str}: HTTP {response.status_code}")

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
        print(f"Saved {len(calamities_to_save)} calamities")

    cached_calamities = list(Calamity.objects.all().values(
        'year', 'calamity_type', 'country', 'region', 'location', 'latitude', 'longitude'
    ))
    print("Cached calamities:", cached_calamities)
    cache.set('calamity_data', cached_calamities, 900)
    return cached_calamities

def dashboard(request):
    cached_calamities = cache.get('calamity_data')
    if cached_calamities is None:
        print("Cache miss, loading data...")
        cached_calamities = load_and_process_data()
    else:
        print("Cache hit, using cached data")

    calamity_type_filter = request.GET.get('calamity_type', 'all')
    year_filter = request.GET.get('year', 'all')

    calamities = Calamity.objects.all()
    if calamity_type_filter != 'all':
        calamities = calamities.filter(calamity_type=calamity_type_filter)
    if year_filter != 'all':
        calamities = calamities.filter(year=year_filter)

    calamity_types = ['drought', 'earthquake', 'flood', 'storm', 'volcanic activity', 'wildfire']
    years = range(2000, 2026)

    # Pass calamities as a JSON string for JavaScript
    context = {
        'calamities': json.dumps(list(calamities.values(
            'year', 'calamity_type', 'country', 'region', 'location', 'latitude', 'longitude'
        ))),
        'calamity_types': calamity_types,
        'years': years,
        'selected_type': calamity_type_filter,
        'selected_year': year_filter,
        'google_maps_api_key': "AIzaSyB4y-YKK1KxniUfZC2PfFTlhjfCmi_tMuw"  # Pass API key to template
    }
    return render(request, 'dashboard/dashboard.html', context)

'''def dashboard(request):
    cached_calamities = cache.get('calamity_data')
    if cached_calamities is None:
        cached_calamities = load_and_process_data()

    calamity_type_filter = request.GET.get('calamity_type', 'all')
    year_filter = request.GET.get('year', 'all')

    calamities = Calamity.objects.all()
    if calamity_type_filter != 'all':
        calamities = calamities.filter(calamity_type=calamity_type_filter)
    if year_filter != 'all':
        calamities = calamities.filter(year=year_filter)

    calamity_types = ['drought', 'earthquake', 'flood', 'storm', 'volcanic activity', 'wildfire']
    years = range(2000, 2026)

    context = {
        'calamities': json.dumps(list(calamities.values(
            'year', 'calamity_type', 'country', 'region', 'location', 'latitude', 'longitude'
        ))),
        'calamity_types': calamity_types,
        'years': years,
        'selected_type': calamity_type_filter,
        'selected_year': year_filter,
    }
    return render(request, 'dashboard/dashboard.html', context)'''