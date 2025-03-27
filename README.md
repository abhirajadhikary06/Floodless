# Global Alert Network

## Overview

The **Global Alert Network (GAN)** is a comprehensive disaster management platform designed to empower communities, authorities, and individuals by providing real-time tools and resources to predict, monitor, and respond to natural disasters and calamities. Built with a focus on connectivity, accessibility, and transparency, GAN aims to reduce the impact of disasters through proactive measures, community engagement, and advanced technology.

This project leverages modern web technologies, AI-driven predictions, and real-time data to create a robust system for disaster preparedness and response. Below is a detailed breakdown of the features, setup instructions, and API documentation for developers.

---

## Features

### 1. Prediction Map
The Prediction Map is a core feature of GAN, utilizing AI and machine learning to forecast potential natural disasters such as floods, wildfires, hurricanes, and earthquakes. Key aspects include:

- **Disaster Prediction**: The map integrates historical data, weather patterns, and environmental factors to predict the likelihood of disasters in specific regions. For example, it can forecast flood risks based on rainfall data or wildfire risks based on temperature and humidity.
- **Nearest Hospital Locator**: In the event of a predicted or ongoing disaster, the map highlights the nearest hospitals or shelters where users can seek refuge. It uses geolocation to provide real-time directions and estimated travel times.
- **Visual Representation**: The map is interactive, displaying color-coded risk zones (e.g., red for high risk, yellow for moderate risk) and overlays for hospital locations.

### 2. Previous Disasters
This feature provides a historical database of past natural disasters, allowing users to learn from historical events and prepare for future ones.

- **Searchable Database**: Users can search for disasters by location, date, or type (e.g., earthquake, tsunami).
- **Detailed Reports**: Each entry includes details such as the disaster’s impact (casualties, economic loss), response efforts, and lessons learned.
- **Educational Resource**: Helps communities understand recurring disaster patterns in their area, fostering better preparedness.

### 3. Latest News Related to Disasters
Stay informed with real-time news updates on ongoing and recent disasters worldwide.

- **News Aggregation**: GAN pulls in the latest disaster-related news from trusted sources, ensuring users have access to up-to-date information.
- **Localized News**: Users can filter news by region to focus on disasters affecting their area.
- **Alerts**: Push notifications for breaking news about disasters in the user’s vicinity.

### 4. Community Connectivity
The Community Connectivity feature fosters collaboration among citizens during and after disasters, enabling them to support each other.

- **Disaster Reporting**: Users can report disasters directly from their location, including details such as the type of disaster, severity, and current situation. Reports include geolocation data for precise mapping.
- **Communication Platform**: Other users can view these reports, comment, and offer assistance or advice. For example, a user reporting a flood can receive messages from others offering shelter or supplies.
- **Community Forum**: A dedicated space for users to discuss disaster preparedness, share experiences, and build local support networks.

### 5. Authority Login
A separate login portal for disaster management authorities provides a centralized dashboard to monitor and respond to disasters.

- **Disaster Monitoring**: Authorities can view all reported disasters on a single map, with filters for type, severity, and location.
- **Real-Time Updates**: Receive live updates from user reports and prediction models to prioritize response efforts.
- **Coordination Tools**: Send alerts to citizens, coordinate with hospitals, and manage resources efficiently.

### 6. Chatbot for Natural Disasters and Calamities
An AI-powered chatbot provides instant support and information related to natural disasters.

- **Disaster Information**: Users can ask questions like “What should I do during an earthquake?” or “How do I prepare for a hurricane?” The chatbot provides actionable advice based on best practices.
- **Real-Time Assistance**: During a disaster, the chatbot can guide users to the nearest shelter or hospital and provide safety tips.
- **Multilingual Support**: Available in multiple languages to ensure accessibility for diverse communities.

### 7. API Documentation
GAN provides a public API for developers to access previous disaster data, enabling integration with other applications.

- **Endpoint**: `GET /disasters/`
  - **Description**: Fetch a list of previous disasters.
  - **Parameters**:
    - `location` (optional): Filter by location (e.g., "California").
    - `type` (optional): Filter by disaster type (e.g., "earthquake").
    - `date_from` (optional): Filter by start date (e.g., "2023-01-01").
    - `date_to` (optional): Filter by end date (e.g., "2023-12-31").
  - **Response**:
    ```json
    [
          {
        "year": 2020,
        "disaster_type": "Flood",
        "country": "India",
        "region": "Kerala",
        "location": "Alappuzha",
    },
      ...
    ]
    ```
- **Authentication**: Requires an API key, which can be obtained by registering on the GAN developer portal.
- **Rate Limit**: 1000 requests per hour per API key.

---

## Installation

### Prerequisites
- Python 13.1
- Django
- A modern web browser (Chrome, Firefox, Edge)
- API keys for map services (e.g., Google Maps API) and news aggregation (e.g., NewsAPI)

### Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/global-alert-network/gan.git
   cd floodless
   ```

2. **Install Dependencies**:
   ```bash
   pip install django
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory and add the following:
   ```env
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   NEWS_API_KEY=your_news_api_key
   DATABASE_URL=your_database_url
   API_KEY=your_gan_api_key
   ```

4. **Run the Application**:
   ```bash
   python manage.py runserver
   ```
   The app will be available at `http://localhost:8000`.

---

## Usage

1. **Access the Platform**:
   - Open your browser and navigate to `http://localhost:8000` (or the deployed URL if hosted).
   - Register as a user to access community features, or log in as an authority using the separate login portal.

2. **Explore Features**:
   - Use the Prediction Map to view disaster forecasts and locate nearby hospitals.
   - Check the Previous Disasters section to learn about historical events.
   - Stay updated with the Latest News section.
   - Engage with the Community Connectivity feature to report disasters or communicate with others.
   - Authorities can log in to monitor and manage disaster responses.
   - Interact with the Chatbot for disaster-related guidance.
   - Developers can use the API to fetch disaster data for their applications.

---

## Technologies Used

- **Frontend**: HTML, Bulma CSS
- **Backend**: Django
- **Database**: PostgreSQL (for storing disaster data, user reports, etc.)
- **APIs**:
  - Google Maps API (for Prediction Map and hospital locator)
  - NewsAPI (for latest news)
  - OpenWeather (for weather updates)
- **AI/ML**: TensorFlow.js (for disaster prediction models)
- **Chatbot**: Dialogflow (for natural language processing)
- **Styling**: Bulma CSS

---

## Contributing

We welcome contributions to the Global Alert Network! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit them (`git commit -m "Add your feature"`).
4. Push to your branch (`git push origin feature/your-feature`).
5. Open a pull request with a detailed description of your changes.

Please ensure your code follows our coding standards and includes tests where applicable.

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- Inspired by global disaster management initiatives like the United Nations Office for Disaster Risk Reduction (UNDRR).
- Thanks to the open-source community for providing tools and libraries that made this project possible.
- Special thanks to contributors who helped shape the vision of GAN.

---

The Global Alert Network is committed to making the world a safer place by empowering communities with the tools they need to face natural disasters. Join us in building a more resilient future! 🌍