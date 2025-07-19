from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        group_name = "managers"

        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Group '{group_name}' created."))
        else:
            self.stdout.write(f"Group '{group_name}' already exists.")

        perms_to_add = [
            ("mail", "BulkMail", "can_disable_mail"),
            ("mail", "BulkMail", "view_bulkmail"),
            ("mail", "Receiver", "view_receiver"),
            ("users", "CustomUser", "can_block_users"),
            ("users", "CustomUser", "view_customuser"),
        ]

        for app_label, model, codename in perms_to_add:
            try:
                model_lower = model.lower()
                content_type = ContentType.objects.get(
                    app_label=app_label, model=model_lower
                )
                perm = Permission.objects.get(
                    content_type=content_type, codename=codename
                )
                group.permissions.add(perm)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Permission '{perm.name}' ({codename}) added to group '{group_name}'."
                    )
                )
            except ContentType.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"ContentType for app '{app_label}', model '{model}' not found."
                    )
                )
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Permission codename '{codename}' for model '{model}' not found."
                    )
                )

        self.stdout.write(self.style.SUCCESS("Done assigning permissions."))
