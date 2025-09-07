import logging
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from ipgeolocation import IPGeolocationAPI
from .models import RequestLog, BlockedIP


logger = logging.getLogger(__name__)


class IPLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log IP address, timestamp, and path of every incoming request.
    Also blocks requests from IPs in the blacklist.
    """
    
    def process_request(self, request):
        """
        Process the request and log IP address, timestamp, path, and geolocation data.
        Also check if the IP is blacklisted and block if necessary.
        This method is called for each request before the view is processed.
        """
        try:
            # Get the client's IP address
            ip_address = self.get_client_ip(request)
            
            # Check if IP is blacklisted
            if self.is_ip_blocked(ip_address):
                logger.warning(f"Blocked request from blacklisted IP: {ip_address}")
                return HttpResponseForbidden(
                    "Access denied. Your IP address has been blocked.",
                    content_type="text/plain"
                )
            
            # Get the request path
            path = request.path
            
            # Get geolocation data
            country, city = self.get_geolocation_data(ip_address)
            
            # Create and save the request log entry
            RequestLog.objects.create(
                ip_address=ip_address,
                path=path,
                country=country,
                city=city
            )
            
            # Also log to Django's logging system for debugging
            location_info = f" ({city}, {country})" if city and country else ""
            logger.info(f"Request logged: {ip_address}{location_info} - {path}")
            
        except Exception as e:
            # Log the error but don't break the request processing
            logger.error(f"Error processing request: {e}")
    
    def get_client_ip(self, request):
        """
        Get the real IP address of the client making the request.
        Handles cases where the request goes through proxies or load balancers.
        """
        # Check for forwarded IP first
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            ip = x_forwarded_for.split(',')[0].strip()
            return ip
        
        # Check for real IP header
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip.strip()
        
        # Fall back to REMOTE_ADDR
        return request.META.get('REMOTE_ADDR', '127.0.0.1')
    
    def is_ip_blocked(self, ip_address):
        """
        Check if the given IP address is in the blacklist.
        Returns True if the IP is blocked, False otherwise.
        """
        try:
            return BlockedIP.objects.filter(
                ip_address=ip_address,
                is_active=True
            ).exists()
        except Exception as e:
            logger.error(f"Error checking IP blacklist: {e}")
            return False
    
    def get_geolocation_data(self, ip_address):
        """
        Get geolocation data (country and city) for the given IP address.
        Uses caching to avoid repeated API calls for the same IP.
        Returns tuple of (country, city) or (None, None) if not available.
        """
        # Skip geolocation for local/private IPs
        if self.is_private_ip(ip_address):
            return None, None
        
        # Check cache first
        cache_key = f"geolocation_{ip_address}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            logger.debug(f"Using cached geolocation data for {ip_address}")
            return cached_data.get('country'), cached_data.get('city')
        
        try:
            # Initialize IPGeolocationAPI
            ip_geolocation = IPGeolocationAPI()
            
            # Get geolocation data
            geolocation_data = ip_geolocation.get_geolocation(ip_address)
            
            if geolocation_data and geolocation_data.get('status') == 'success':
                country = geolocation_data.get('country_name', '')
                city = geolocation_data.get('city', '')
                
                # Cache the result for 24 hours
                cache_data = {'country': country, 'city': city}
                cache.set(cache_key, cache_data, 86400)  # 24 hours
                
                logger.debug(f"Fetched geolocation data for {ip_address}: {city}, {country}")
                return country, city
            else:
                logger.warning(f"Failed to get geolocation data for {ip_address}")
                return None, None
                
        except Exception as e:
            logger.error(f"Error fetching geolocation data for {ip_address}: {e}")
            return None, None
    
    def is_private_ip(self, ip_address):
        """
        Check if the IP address is a private/local IP that doesn't need geolocation.
        """
        try:
            import ipaddress
            ip = ipaddress.ip_address(ip_address)
            return ip.is_private or ip.is_loopback or ip.is_link_local
        except ValueError:
            return True  # Invalid IP, treat as private
