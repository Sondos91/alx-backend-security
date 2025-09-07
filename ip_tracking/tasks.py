from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from .models import RequestLog, SuspiciousIP


@shared_task
def detect_suspicious_ips():
    """
    Celery task to detect suspicious IP addresses based on:
    1. IPs exceeding 100 requests/hour
    2. IPs accessing sensitive paths (admin, login, etc.)
    
    This task should be run hourly.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Get the time range for the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    # Define sensitive paths
    sensitive_paths = ['/admin/', '/login/', '/sensitive-data/', '/admin-dashboard/']
    
    # 1. Find IPs with more than 100 requests in the last hour
    high_volume_ips = (
        RequestLog.objects
        .filter(timestamp__gte=one_hour_ago)
        .values('ip_address')
        .annotate(request_count=Count('id'))
        .filter(request_count__gt=100)
    )
    
    # 2. Find IPs accessing sensitive paths in the last hour
    sensitive_access_ips = (
        RequestLog.objects
        .filter(
            timestamp__gte=one_hour_ago,
            path__in=sensitive_paths
        )
        .values('ip_address')
        .annotate(sensitive_count=Count('id'))
        .filter(sensitive_count__gt=0)
    )
    
    # Process high volume IPs
    for ip_data in high_volume_ips:
        ip_address = ip_data['ip_address']
        request_count = ip_data['request_count']
        
        # Get the sensitive paths accessed by this IP
        sensitive_paths_accessed = list(
            RequestLog.objects
            .filter(
                ip_address=ip_address,
                timestamp__gte=one_hour_ago,
                path__in=sensitive_paths
            )
            .values_list('path', flat=True)
            .distinct()
        )
        
        reason = f"High volume: {request_count} requests in 1 hour"
        if sensitive_paths_accessed:
            reason += f" + accessed sensitive paths: {', '.join(sensitive_paths_accessed)}"
        
        # Create or update SuspiciousIP record
        suspicious_ip, created = SuspiciousIP.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'reason': reason,
                'request_count': request_count,
                'sensitive_paths': sensitive_paths_accessed,
                'is_active': True
            }
        )
        
        if not created:
            # Update existing record
            suspicious_ip.reason = reason
            suspicious_ip.request_count = request_count
            suspicious_ip.sensitive_paths = sensitive_paths_accessed
            suspicious_ip.detected_at = timezone.now()
            suspicious_ip.is_active = True
            suspicious_ip.save()
    
    # Process IPs accessing sensitive paths (even if not high volume)
    for ip_data in sensitive_access_ips:
        ip_address = ip_data['ip_address']
        sensitive_count = ip_data['sensitive_count']
        
        # Skip if already processed as high volume
        if SuspiciousIP.objects.filter(ip_address=ip_address, is_active=True).exists():
            continue
        
        # Get all paths accessed by this IP in the last hour
        all_paths = list(
            RequestLog.objects
            .filter(
                ip_address=ip_address,
                timestamp__gte=one_hour_ago
            )
            .values_list('path', flat=True)
            .distinct()
        )
        
        # Get the sensitive paths accessed
        sensitive_paths_accessed = [path for path in all_paths if path in sensitive_paths]
        
        reason = f"Accessed sensitive paths: {', '.join(sensitive_paths_accessed)} ({sensitive_count} times)"
        
        # Create SuspiciousIP record
        SuspiciousIP.objects.create(
            ip_address=ip_address,
            reason=reason,
            request_count=sensitive_count,
            sensitive_paths=sensitive_paths_accessed,
            is_active=True
        )
    
    # Log the results
    total_suspicious = SuspiciousIP.objects.filter(is_active=True).count()
    new_suspicious = SuspiciousIP.objects.filter(
        detected_at__gte=one_hour_ago,
        is_active=True
    ).count()
    
    return {
        'status': 'success',
        'total_suspicious_ips': total_suspicious,
        'new_suspicious_ips': new_suspicious,
        'high_volume_count': len(high_volume_ips),
        'sensitive_access_count': len(sensitive_access_ips)
    }


@shared_task
def cleanup_old_suspicious_ips():
    """
    Cleanup task to deactivate old suspicious IP flags.
    Deactivates flags older than 24 hours.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    
    # Deactivate old suspicious IP flags
    deactivated_count = SuspiciousIP.objects.filter(
        detected_at__lt=twenty_four_hours_ago,
        is_active=True
    ).update(is_active=False)
    
    return {
        'status': 'success',
        'deactivated_count': deactivated_count
    }


@shared_task
def generate_security_report():
    """
    Generate a security report with statistics.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    last_24_hours = now - timedelta(hours=24)
    last_hour = now - timedelta(hours=1)
    
    # Get statistics
    total_requests_24h = RequestLog.objects.filter(timestamp__gte=last_24_hours).count()
    total_requests_1h = RequestLog.objects.filter(timestamp__gte=last_hour).count()
    
    active_suspicious = SuspiciousIP.objects.filter(is_active=True).count()
    active_blocked = BlockedIP.objects.filter(is_active=True).count()
    
    # Top countries by request count
    top_countries = (
        RequestLog.objects
        .filter(timestamp__gte=last_24_hours, country__isnull=False)
        .values('country')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Top IPs by request count
    top_ips = (
        RequestLog.objects
        .filter(timestamp__gte=last_24_hours)
        .values('ip_address', 'country', 'city')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    return {
        'status': 'success',
        'report_generated_at': now.isoformat(),
        'statistics': {
            'total_requests_24h': total_requests_24h,
            'total_requests_1h': total_requests_1h,
            'active_suspicious_ips': active_suspicious,
            'active_blocked_ips': active_blocked,
        },
        'top_countries': list(top_countries),
        'top_ips': list(top_ips)
    }
