import json
from django.shortcuts import render
from django.core.cache import cache
from .models import Calamity

def dashboard(request):
    calamity_type_filter = request.GET.get('calamity_type', 'all')
    year_filter = request.GET.get('year', 'all')
    cache_key = f"calamities_{calamity_type_filter}_{year_filter}"

    cached_calamities = cache.get(cache_key)
    if cached_calamities is None:
        print("Cache miss, querying database...")
        calamities = Calamity.objects.all()
        if calamity_type_filter != 'all':
            calamities = calamities.filter(calamity_type=calamity_type_filter)
        if year_filter != 'all':
            calamities = calamities.filter(year=year_filter)

        cached_calamities = list(calamities.values(
            'year', 'calamity_type', 'country', 'location', 'latitude', 'longitude'
        ))
        cache.set(cache_key, cached_calamities, 900)  # 15-minute cache
        print("Cached calamities:", cached_calamities)
    else:
        print("Cache hit, using cached data")

    calamity_types = ['drought', 'earthquake', 'flood', 'storm', 'volcanic activity', 'wildfire']
    years = range(2020, 2026)

    context = {
        'calamities_json': json.dumps(cached_calamities),  # Serialize properly
        'calamity_types': calamity_types,
        'years': years,
        'selected_type': calamity_type_filter,
        'selected_year': year_filter,
    }
    return render(request, 'dashboard/dashboard.html', context)
