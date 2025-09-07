# ALX Backend Security - IP Logging Middleware

This Django project implements a basic IP logging middleware that tracks and logs every incoming request with its IP address, timestamp, and path.

## Features

- **IP Logging Middleware**: Automatically logs every request with IP address, timestamp, and path
- **IP Geolocation**: Automatically detects and logs country and city for each request
- **IP Blacklisting**: Block requests from blacklisted IP addresses with 403 Forbidden response
- **Rate Limiting**: Configurable rate limits for different user types and endpoints
- **Anomaly Detection**: Automated detection of suspicious IP behavior using Celery
- **Geolocation Caching**: 24-hour cache for geolocation data to reduce API calls
- **Database Storage**: Stores logs, blocked IPs, and suspicious IPs in SQLite database
- **Admin Interface**: Comprehensive admin interface for all security data
- **Management Commands**: Command-line tools to manage IP blacklist and Celery tasks
- **Real IP Detection**: Handles forwarded IPs from proxies and load balancers

## Project Structure

```
alx_backend_security/
├── manage.py
├── requirements.txt
├── alx_backend_security/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── ip_tracking/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── middleware.py
    ├── views.py
    ├── urls.py
    ├── tasks.py
    ├── management/
    │   └── commands/
    │       ├── __init__.py
    │       ├── block_ip.py
    │       ├── unblock_ip.py
    │       ├── list_blocked_ips.py
    │       └── setup_celery_tasks.py
    └── templates/
        └── ip_tracking/
            ├── logs.html
            ├── login.html
            └── admin_dashboard.html
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Create Superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```

5. **Set up Celery Tasks** (optional):
   ```bash
   python manage.py setup_celery_tasks
   ```

6. **Run Celery Worker** (for anomaly detection):
   ```bash
   celery -A alx_backend_security worker --loglevel=info
   ```

7. **Run Celery Beat** (for scheduled tasks):
   ```bash
   celery -A alx_backend_security beat --loglevel=info
   ```

### Geolocation Configuration

The system uses the free ipapi service for geolocation data. For production use, you may want to:

1. **Use a paid service** for better reliability and rate limits
2. **Add API key** in `settings.py`:
   ```python
   IPGEOLOCATION_SETTINGS = {
       'BACKEND_API_KEY': 'your-api-key-here',
       'BACKEND_API': 'ipstack',  # or other service
   }
   ```
3. **Configure different services** like ipstack, ipinfo, etc.

## Usage

- **Test the middleware**: Visit `http://127.0.0.1:8000/test/`
- **View logs**: Visit `http://127.0.0.1:8000/logs/`
- **Login**: Visit `http://127.0.0.1:8000/login/`
- **Admin dashboard**: Visit `http://127.0.0.1:8000/admin-dashboard/` (requires login)
- **Sensitive data**: Visit `http://127.0.0.1:8000/sensitive-data/` (requires login)
- **Django admin**: Visit `http://127.0.0.1:8000/admin/`

### IP Blacklisting Commands

- **Block an IP**: `python manage.py block_ip 192.168.1.100 --reason "Suspicious activity"`
- **Unblock an IP**: `python manage.py unblock_ip 192.168.1.100`
- **List blocked IPs**: `python manage.py list_blocked_ips`
- **List only active blocks**: `python manage.py list_blocked_ips --active-only`
- **Deactivate instead of delete**: `python manage.py unblock_ip 192.168.1.100` (keeps record but makes inactive)

## Implementation Details

### Middleware (`ip_tracking/middleware.py`)
- `IPLoggingMiddleware`: Logs every request with IP address, timestamp, path, and geolocation
- **IP Geolocation**: Automatically fetches country and city data for each request
- **Geolocation Caching**: 24-hour cache to reduce API calls and improve performance
- **IP Blacklisting**: Checks if request IP is in blacklist and returns 403 Forbidden
- Handles real IP detection from forwarded headers
- Skips geolocation for private/local IP addresses
- Graceful error handling to prevent request failures

### Models (`ip_tracking/models.py`)
- `RequestLog`: Stores IP address, timestamp, path, country, and city for each request
- `BlockedIP`: Stores blocked IP addresses with reason and active status
- Uses `GenericIPAddressField` for proper IP address storage
- Geolocation fields (country, city) with null/blank support
- Ordered by timestamp (newest first)

### Management Commands
- `block_ip`: Add IP addresses to blacklist with optional reason
- `unblock_ip`: Remove or deactivate IP addresses from blacklist
- `list_blocked_ips`: Display all blocked IPs with filtering options

### Admin Interface (`ip_tracking/admin.py`)
- Read-only interface for viewing logs
- Full management interface for blocked IPs
- Search and filter capabilities for both models

## Task Requirements Completed

### Task 0: Basic IP Logging Middleware
✅ Created `ip_tracking/middleware.py` with middleware class  
✅ Created `ip_tracking/models.py` with RequestLog model (ip_address, timestamp, path)  
✅ Registered middleware in `settings.py`  
✅ Implemented proper IP address detection  
✅ Added admin interface for log management  
✅ Created test views and templates

### Task 1: IP Blacklisting
✅ Added `BlockedIP` model to `ip_tracking/models.py` with ip_address field  
✅ Modified `ip_tracking/middleware.py` to block blacklisted IPs with 403 Forbidden  
✅ Created `ip_tracking/management/commands/block_ip.py` to add IPs to blacklist  
✅ Added admin interface for BlockedIP management  
✅ Created additional management commands (unblock_ip, list_blocked_ips)  
✅ Added IP validation and error handling

### Task 2: IP Geolocation Analytics
✅ Installed django-ipgeolocation package  
✅ Extended `RequestLog` model with country and city fields  
✅ Updated `ip_tracking/middleware.py` to fetch geolocation data  
✅ Implemented 24-hour caching for geolocation data  
✅ Added geolocation settings to Django configuration  
✅ Updated admin interface to display geolocation fields  
✅ Enhanced logs template to show location information  
✅ Added private IP detection to skip geolocation for local addresses

### Task 3: Rate Limiting by IP
✅ Installed django-ratelimit package  
✅ Configured rate limits in `settings.py`  
✅ Created login view with 5 requests/minute for POST, 10 requests/minute for GET  
✅ Created admin dashboard with 10 requests/minute for authenticated users  
✅ Created sensitive data view with rate limiting  
✅ Added comprehensive rate limiting configuration  

### Task 4: Anomaly Detection
✅ Created `SuspiciousIP` model in `ip_tracking/models.py`  
✅ Created Celery tasks in `ip_tracking/tasks.py` for hourly anomaly detection  
✅ Implemented detection for IPs exceeding 100 requests/hour  
✅ Implemented detection for IPs accessing sensitive paths  
✅ Added Celery configuration and periodic task setup  
✅ Created management command to set up Celery tasks  
✅ Updated admin interface for SuspiciousIP management  
✅ Added comprehensive anomaly detection with JSONField for sensitive paths
