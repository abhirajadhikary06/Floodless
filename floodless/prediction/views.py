import pandas as pd
import requests
from django.shortcuts import render
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import os
from datetime import datetime, timedelta

# Path to dataset.csv
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset.csv')

# OpenWeatherMap API key (replace with your API key)
API_KEY = 'YOUR_OPENWEATHERMAP_API_KEY'

def predict_disaster(request):
    # Load the dataset
    df = pd.read_csv(DATASET_PATH)

    # Preprocess the dataset
    # Encode categorical variables (calamity_type, location, country)
    le_calamity = LabelEncoder()
    le_location = LabelEncoder()
    le_country = LabelEncoder()

    df['calamity_type_encoded'] = le_calamity.fit_transform(df['calamity_type'])
    df['location_encoded'] = le_location.fit_transform(df['location'])
    df['country_encoded'] = le_country.fit_transform(df['country'])

    # Features: latitude, longitude, year, and weather data (to be fetched)
    # Target: calamity_type_encoded
    X = df[['latitude', 'longitude', 'year']]
    y = df['calamity_type_encoded']

    # Split the data for training
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train a RandomForest model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Fetch current weather data for each unique location in the dataset
    unique_locations = df[['latitude', 'longitude']].drop_duplicates()
    weather_data = []

    for _, row in unique_locations.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            weather_data.append({
                'latitude': lat,
                'longitude': lon,
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'precipitation': data.get('rain', {}).get('1h', 0)  # Rainfall in the last hour, if available
            })
        else:
            weather_data.append({
                'latitude': lat,
                'longitude': lon,
                'temperature': None,
                'humidity': None,
                'wind_speed': None,
                'precipitation': None
            })

    # Convert weather data to DataFrame
    weather_df = pd.DataFrame(weather_data)

    # Predict the next disaster
    current_year = datetime.now().year
    predictions = []

    for _, row in weather_df.iterrows():
        if row['temperature'] is None:  # Skip if weather data fetch failed
            continue

        # Prepare features for prediction
        features = pd.DataFrame([[
            row['latitude'],
            row['longitude'],
            current_year
        ]], columns=['latitude', 'longitude', 'year'])

        # Predict the disaster type
        pred = model.predict(features)[0]
        calamity_type = le_calamity.inverse_transform([pred])[0]

        # Simple heuristic for time prediction: assume disaster occurs within 30 days if conditions are extreme
        # Example: High precipitation might indicate a flood
        possible_time = datetime.now() + timedelta(days=30)
        if row['precipitation'] > 10 and calamity_type == 'flood':
            possible_time = datetime.now() + timedelta(days=7)  # Flood might happen sooner

        predictions.append({
            'calamity_type': calamity_type,
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'possible_time': possible_time.strftime('%Y-%m-%d'),
            'temperature': row['temperature'],
            'humidity': row['humidity'],
            'wind_speed': row['wind_speed'],
            'precipitation': row['precipitation']
        })

    # Sort predictions by likelihood (simplified: based on precipitation for floods, temperature for wildfires, etc.)
    predictions.sort(key=lambda x: (
        x['precipitation'] if x['calamity_type'] == 'flood' else
        x['temperature'] if x['calamity_type'] == 'wildfire' else
        0
    ), reverse=True)

    # Take the top prediction
    top_prediction = predictions[0] if predictions else None

    return render(request, 'predication/predict.html', {
        'prediction': top_prediction
    })