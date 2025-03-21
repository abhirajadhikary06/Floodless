import os
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings

def api_docs(request):
    return render(request, 'apidocs/api_docs.html')

def download_dataset(request):
    # Path to the dataset CSV file
    dataset_path = os.path.join(os.path.dirname(__file__), 'disaster_dataset.csv')

    if not os.path.exists(dataset_path):
        return HttpResponse("Dataset file not found.", status=404)

    # Read the file and create a response
    with open(dataset_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="disaster_dataset.csv"'
        return response