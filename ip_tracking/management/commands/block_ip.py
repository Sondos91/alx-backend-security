from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from ip_tracking.models import BlockedIP
import ipaddress


class Command(BaseCommand):
    help = 'Add an IP address to the blacklist'

    def add_arguments(self, parser):
        parser.add_argument(
            'ip_address',
            type=str,
            help='IP address to block'
        )
        parser.add_argument(
            '--reason',
            type=str,
            default='',
            help='Reason for blocking this IP address (optional)'
        )
        parser.add_argument(
            '--inactive',
            action='store_true',
            help='Add the IP as inactive (not blocked)'
        )

    def handle(self, *args, **options):
        ip_address = options['ip_address']
        reason = options['reason']
        is_active = not options['inactive']

        # Validate IP address format
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            raise CommandError(f'Invalid IP address format: {ip_address}')

        # Check if IP is already blocked
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            existing = BlockedIP.objects.get(ip_address=ip_address)
            if existing.is_active == is_active:
                status = "active" if is_active else "inactive"
                self.stdout.write(
                    self.style.WARNING(
                        f'IP {ip_address} is already {status} in the blacklist.'
                    )
                )
            else:
                # Update existing record
                existing.is_active = is_active
                existing.reason = reason or existing.reason
                existing.save()
                status = "activated" if is_active else "deactivated"
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully {status} IP {ip_address} in the blacklist.'
                    )
                )
        else:
            # Create new blocked IP record
            try:
                blocked_ip = BlockedIP.objects.create(
                    ip_address=ip_address,
                    reason=reason,
                    is_active=is_active
                )
                status = "blocked" if is_active else "added as inactive"
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully {status} IP {ip_address} in the blacklist.'
                    )
                )
                if reason:
                    self.stdout.write(f'Reason: {reason}')
            except ValidationError as e:
                raise CommandError(f'Validation error: {e}')
            except Exception as e:
                raise CommandError(f'Unexpected error: {e}')
