from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django_ratelimit.decorators import ratelimit
from django.utils import timezone
from .models import RequestLog, SuspiciousIP, BlockedIP


def test_view(request):
    """
    Simple test view to demonstrate the IP logging middleware.
    """
    return JsonResponse({
        'message': 'Hello! This request has been logged.',
        'your_ip': request.META.get('REMOTE_ADDR', 'Unknown'),
        'path': request.path
    })


def logs_view(request):
    """
    View to display recent request logs.
    """
    recent_logs = RequestLog.objects.all()[:50]  # Get last 50 logs
    return render(request, 'ip_tracking/logs.html', {'logs': recent_logs})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
@ratelimit(key='ip', rate='10/m', method='GET', block=True)
def login_view(request):
    """
    Login view with rate limiting:
    - 5 requests/minute for POST (login attempts)
    - 10 requests/minute for GET (login page views)
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('ip_tracking:admin_dashboard')
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Please provide both username and password.')
    
    return render(request, 'ip_tracking/login.html')


@login_required
@ratelimit(key='ip', rate='10/m', block=True)
def admin_dashboard(request):
    """
    Admin dashboard view with rate limiting:
    - 10 requests/minute for authenticated users
    """
    # Get recent statistics
    recent_logs = RequestLog.objects.all()[:20]
    suspicious_ips = SuspiciousIP.objects.filter(is_active=True)[:10]
    blocked_ips = BlockedIP.objects.filter(is_active=True)[:10]
    
    context = {
        'recent_logs': recent_logs,
        'suspicious_ips': suspicious_ips,
        'blocked_ips': blocked_ips,
        'total_requests': RequestLog.objects.count(),
        'suspicious_count': SuspiciousIP.objects.filter(is_active=True).count(),
        'blocked_count': BlockedIP.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'ip_tracking/admin_dashboard.html', context)


@login_required
@ratelimit(key='ip', rate='10/m', block=True)
def sensitive_data_view(request):
    """
    Sensitive data view with rate limiting:
    - 10 requests/minute for authenticated users
    """
    return JsonResponse({
        'message': 'This is sensitive data that requires authentication.',
        'user': request.user.username,
        'timestamp': timezone.now().isoformat(),
        'ip': request.META.get('REMOTE_ADDR', 'Unknown')
    })


def logout_view(request):
    """
    Logout view (no rate limiting needed).
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('ip_tracking:login_view')
