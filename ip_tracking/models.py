from django.db import models
from django.utils import timezone


class RequestLog(models.Model):
    """
    Model to store request logging information including IP address,
    timestamp, path, and geolocation data for every incoming request.
    """
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the client making the request"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the request was made"
    )
    path = models.CharField(
        max_length=255,
        help_text="URL path of the request"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Country of the IP address"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City of the IP address"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Request Log'
        verbose_name_plural = 'Request Logs'
    
    def __str__(self):
        location = f" ({self.city}, {self.country})" if self.city and self.country else ""
        return f"{self.ip_address}{location} - {self.path} - {self.timestamp}"


class BlockedIP(models.Model):
    """
    Model to store blocked IP addresses that should be denied access.
    """
    ip_address = models.GenericIPAddressField(
        unique=True,
        help_text="IP address to block"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this IP was added to the blacklist"
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Reason for blocking this IP (optional)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this block is currently active"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blocked IP'
        verbose_name_plural = 'Blocked IPs'
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason or 'No reason provided'}"


class SuspiciousIP(models.Model):
    """
    Model to store IP addresses flagged as suspicious by anomaly detection.
    """
    ip_address = models.GenericIPAddressField(
        unique=True,
        help_text="IP address flagged as suspicious"
    )
    reason = models.CharField(
        max_length=255,
        help_text="Reason for flagging this IP as suspicious"
    )
    detected_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this IP was flagged as suspicious"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this flag is currently active"
    )
    request_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of requests that triggered the flag"
    )
    sensitive_paths = models.JSONField(
        default=list,
        blank=True,
        help_text="List of sensitive paths accessed by this IP"
    )
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = 'Suspicious IP'
        verbose_name_plural = 'Suspicious IPs'
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason} ({self.request_count} requests)"
