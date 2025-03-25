from django.shortcuts import render
from prediction.models import DisasterPrediction

# Google Maps API key
GOOGLE_MAPS_API_KEY = 'AIzaSyB4y-YKK1KxniUfZC2PfFTlhjfCmi_tMuw'

def predict_disaster(request):
    # Define filter options
    years = list(range(2026, 2034))
    countries = [
        "Democratic People's Republic of Korea", 'El Salvador', 'Kenya', 'United Republic of Tanzania',
        'Italy', 'Democratic Republic of the Congo', 'Armenia', 'Guinea-Bissau', 'Paraguay', 'Sri Lanka',
        'Türkiye', 'Indonesia', 'Republic of Korea', 'Chile', 'Ecuador', 'Pakistan', 'Rwanda', 'China',
        'Syrian Arab Republic', 'Guatemala', 'Peru', 'Comoros', 'Japan', 'Serbia', 'Greece', 'Croatia',
        'Iran (Islamic Republic of)', 'Viet Nam', 'Austria', 'Montenegro', 'Colombia', 'India', 'Malaysia',
        'Mexico', 'United States of America', 'Nepal', 'Yemen', 'Somalia', 'Philippines', 'Ghana', 'Romania',
        'Algeria', 'Uruguay', 'Sudan', 'South Africa', 'Haiti', 'Panama', 'Honduras', 'Cuba', 'Mozambique',
        'Afghanistan', 'Russian Federation', 'Myanmar', 'Nigeria', 'Argentina', 'Senegal', 'Costa Rica',
        'Côte d’Ivoire', 'Brazil', 'Oman', 'Bangladesh', 'Bulgaria', 'France', 'Madagascar', 'North Macedonia',
        'Guinea', 'Bolivia (Plurinational State of)', 'Iraq', 'Papua New Guinea', 'Bosnia and Herzegovina',
        'Mali', 'Ethiopia', 'Belarus', 'Angola', 'Togo', 'Cyprus', 'Malawi', 'Zambia', 'Slovenia', 'Ireland',
        'Australia', 'Thailand', 'Portugal', 'Taiwan (Province of China)', 'Germany', 'Burundi', 'Vanuatu',
        'Switzerland', 'New Zealand', 'Jamaica', 'Puerto Rico', 'Zimbabwe', 'Lebanon', 'Bhutan', 'Nicaragua',
        'Saint Vincent and the Grenadines', 'Central African Republic', 'Czechia', 'Poland', 'Canada'
    ]
    countries.sort()
    disaster_types = ['Earthquake', 'Drought', 'Volcanic activity', 'Flood', 'Storm', 'Wildfire']

    # Get filter values from the request
    selected_year = request.GET.get('year', None)
    selected_country = request.GET.get('country', None)
    selected_disaster_type = request.GET.get('disaster_type', None)

    # Query the database with filters
    queryset = DisasterPrediction.objects.filter(latitude__isnull=False, longitude__isnull=False)
    if selected_year:
        queryset = queryset.filter(year=int(selected_year))
    if selected_country:
        queryset = queryset.filter(country=selected_country)
    if selected_disaster_type:
        queryset = queryset.filter(disaster_type=selected_disaster_type)

    # Prepare data for the map
    predictions = []
    for prediction in queryset:
        radius = prediction.magnitude * 1000  # Scale radius based on magnitude
        hospitals = prediction.hospitals.all()
        hospital_data = [
            {
                'name': hospital.name,
                'latitude': hospital.latitude,
                'longitude': hospital.longitude,
                'address': hospital.address,
            }
            for hospital in hospitals
        ]
        predictions.append({
            'id': prediction.id,
            'calamity_type': prediction.disaster_type,
            'latitude': prediction.latitude,
            'longitude': prediction.longitude,
            'radius': radius,
            'total_affected': prediction.total_affected,
            'magnitude': prediction.magnitude,
            'year': prediction.year,
            'country': prediction.country,
            'hospitals': hospital_data,
        })

    return render(request, 'prediction/predict.html', {
        'predictions': predictions,
        'google_maps_api_key': GOOGLE_MAPS_API_KEY,
        'years': years,
        'countries': countries,
        'disaster_types': disaster_types,
        'selected_year': selected_year,
        'selected_country': selected_country,
        'selected_disaster_type': selected_disaster_type,
    })