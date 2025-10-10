from django.core.management.base import BaseCommand, CommandError

from mail.models import BulkMail
from mail.services import send_bulk_mail


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--id", required=True, type=int, help="BulkMail ID")

    def handle(self, *args, **options):
        bulkmail_id = options["id"]
        try:
            bulk_mail = BulkMail.objects.get(pk=bulkmail_id)
        except BulkMail.DoesNotExist:
            raise CommandError(f"BulkMail with id={bulkmail_id} does not exist")

        self.stdout.write(f"Sending BulkMail id={bulkmail_id}...")
        all_success, responses = send_bulk_mail(bulk_mail)

        if all_success:
            self.stdout.write(self.style.SUCCESS("BulkMail sent successfully!"))
        else:
            self.stdout.write(self.style.ERROR("Errors occurred:"))
            for response in responses:
                self.stdout.write(f" - {response}")
