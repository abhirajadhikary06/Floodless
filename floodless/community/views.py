from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.serializers import serialize
from .models import Profile, EmergencyReport, ChatMessage
from django.utils import timezone
import json
from geopy.geocoders import Nominatim
from datetime import timedelta

# Register View
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        # Validate input
        if not username or not password or not confirm_password or not role:
            messages.error(request, "All fields are required.")
            return render(request, 'community/register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'community/register.html')

        if role not in ['citizen', 'authority']:
            messages.error(request, "Invalid role selected.")
            return render(request, 'community/register.html')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'community/register.html')

        # Create user
        user = User.objects.create_user(username=username, password=password)
        user.save()

        # Create user profile
        Profile.objects.create(user=user, role=role)

        messages.success(request, "Registration successful! Please log in.")
        return redirect('login')

    return render(request, 'community/register.html')

# Login View
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"Attempting login for username: {username}")  # Debugging

        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            print(f"Login successful for username: {username}")  # Debugging
            if not user.is_active:
                print(f"User is inactive: {username}")  # Debugging
                messages.error(request, "Your account is inactive. Please contact support.")
                return render(request, 'community/login.html')

            login(request, user)

            # Ensure the user has a Profile
            profile, created = Profile.objects.get_or_create(user=user, defaults={'role': 'citizen'})
            if created:
                print(f"Created profile for username: {username} with role: {profile.role}")  # Debugging

            # Redirect based on role
            if profile.role == 'authority':
                return redirect('report_list')  # Authorities go to report_list
            elif profile.role == 'citizen':
                return redirect('emergency_report')
            else:
                print(f"Invalid role for username: {username}: {profile.role}")  # Debugging
                messages.error(request, "User role is not defined.")
                return render(request, 'community/login.html')
        else:
            print(f"Login failed for username: {username}")  # Debugging
            messages.error(request, "Invalid username or password.")
            return render(request, 'community/login.html')
    return render(request, 'community/login.html')

# Logout View
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

# community/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import EmergencyReport
from geopy.geocoders import Nominatim

@login_required
def emergency_report(request):
    if request.user.profile.role != 'citizen':
        messages.error(request, "Only citizens can access this page.")
        return redirect('authority_dashboard')

    if request.method == 'POST':
        disaster_type = request.POST.get('disaster_type')
        description = request.POST.get('description')
        location = request.POST.get('location')  # Manually entered location
        latitude = request.POST.get('latitude')  # From live location
        longitude = request.POST.get('longitude')  # From live location

        # Validate input
        if not disaster_type or not description:
            messages.error(request, "Disaster type and description are required.")
            return redirect('emergency_report')

        if not location and not (latitude and longitude):
            messages.error(request, "Please provide either a live location or an address.")
            return redirect('emergency_report')

        # Create the emergency report
        report = EmergencyReport(
            user=request.user,
            disaster_type=disaster_type,
            description=description,
            location=location if location else None,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            reported_at=timezone.now()
        )
        report.save()
        messages.success(request, "Emergency reported successfully.")
        return redirect('emergency_report')
    return render(request, 'community/report.html')


@login_required
def report_list(request):
    # Get reports from the last 24 hours that are active
    time_threshold = timezone.now() - timedelta(hours=24)
    active_reports = EmergencyReport.objects.filter(
        reported_at__gte=time_threshold,
        is_active=True
    ).order_by('-reported_at')

    return render(request, 'community/report_list.html', {
        'active_reports': active_reports
    })

# Authority Dashboard View
@login_required
def authority_dashboard(request):
    if request.user.profile.role != 'authority':
        messages.error(request, "Only authorities can access this page.")
        return redirect('emergency_report')

    # Redirect to report_list since authorities should only access that page
    return redirect('report_list')

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import EmergencyReport

@login_required
def disaster_chat(request, report_id):
    report = get_object_or_404(EmergencyReport, id=report_id, is_active=True)
    messages = report.messages.all().order_by('timestamp')
    location_display = report.location if report.location else "Location not provided"

    # Handle JSON request for fetching messages
    if request.GET.get('format') == 'json':
        messages_data = [
            {
                'id': message.id,
                'user': message.user.username,
                'message': message.message,
                'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'is_authority': message.user.profile.role == 'authority'
            }
            for message in messages
        ]
        return JsonResponse({'messages': messages_data})

    return render(request, 'community/disaster_chat.html', {
        'report': report,
        'messages': messages,
        'location_display': location_display,
    })

@login_required
def send_message(request, report_id):
    if request.method == 'POST':
        report = get_object_or_404(EmergencyReport, id=report_id, is_active=True)
        message_content = request.POST.get('message')
        if message_content:
            ChatMessage.objects.create(
                report=report,
                user=request.user,
                message=message_content,
                timestamp=timezone.now()
            )
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Message content cannot be empty'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})