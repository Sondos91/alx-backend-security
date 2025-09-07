from django.core.management.base import BaseCommand, CommandError
from ip_tracking.models import BlockedIP


class Command(BaseCommand):
    help = 'Remove an IP address from the blacklist or deactivate it'

    def add_arguments(self, parser):
        parser.add_argument(
            'ip_address',
            type=str,
            help='IP address to unblock'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Permanently delete the IP from the blacklist instead of deactivating'
        )

    def handle(self, *args, **options):
        ip_address = options['ip_address']
        delete = options['delete']

        try:
            blocked_ip = BlockedIP.objects.get(ip_address=ip_address)
            
            if delete:
                blocked_ip.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully deleted IP {ip_address} from the blacklist.'
                    )
                )
            else:
                if not blocked_ip.is_active:
                    self.stdout.write(
                        self.style.WARNING(
                            f'IP {ip_address} is already inactive in the blacklist.'
                        )
                    )
                else:
                    blocked_ip.is_active = False
                    blocked_ip.save()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully deactivated IP {ip_address} in the blacklist.'
                        )
                    )
        except BlockedIP.DoesNotExist:
            raise CommandError(f'IP {ip_address} is not in the blacklist.')
        except Exception as e:
            raise CommandError(f'Unexpected error: {e}')
