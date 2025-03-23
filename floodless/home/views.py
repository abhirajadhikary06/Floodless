from django.template.loader import get_template
from django.template.exceptions import TemplateDoesNotExist
from django.shortcuts import render, redirect

def home(request):
    try:
        # Debug: Check where Django is looking for the template
        template = get_template('home/home.html')
        print(f"Template found: {template.origin}")
    except TemplateDoesNotExist as e:
        print(f"Template not found: {e}")
        raise e

    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            if request.user.profile.role == 'citizen':
                return redirect('report_list')
            elif request.user.profile.role == 'authority':
                return redirect('authority_dashboard')
        return redirect('report_list')
    return render(request, 'home/home.html')