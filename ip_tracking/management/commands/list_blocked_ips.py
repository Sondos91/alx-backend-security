from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP


class Command(BaseCommand):
    help = 'List all blocked IP addresses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active blocked IPs'
        )
        parser.add_argument(
            '--inactive-only',
            action='store_true',
            help='Show only inactive blocked IPs'
        )

    def handle(self, *args, **options):
        active_only = options['active_only']
        inactive_only = options['inactive_only']

        # Build queryset based on options
        queryset = BlockedIP.objects.all()
        
        if active_only and not inactive_only:
            queryset = queryset.filter(is_active=True)
        elif inactive_only and not active_only:
            queryset = queryset.filter(is_active=False)

        blocked_ips = queryset.order_by('-created_at')

        if not blocked_ips.exists():
            self.stdout.write(
                self.style.WARNING('No blocked IPs found.')
            )
            return

        # Display header
        self.stdout.write(
            self.style.SUCCESS(f'Found {blocked_ips.count()} blocked IP(s):')
        )
        self.stdout.write('-' * 80)
        self.stdout.write(
            f'{"IP Address":<15} {"Status":<8} {"Reason":<30} {"Created At"}'
        )
        self.stdout.write('-' * 80)

        # Display each blocked IP
        for blocked_ip in blocked_ips:
            status = "Active" if blocked_ip.is_active else "Inactive"
            reason = blocked_ip.reason or "No reason provided"
            created_at = blocked_ip.created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            self.stdout.write(
                f'{blocked_ip.ip_address:<15} {status:<8} {reason:<30} {created_at}'
            )
