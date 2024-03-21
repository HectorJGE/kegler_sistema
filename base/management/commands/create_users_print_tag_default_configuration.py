from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils.translation import ugettext_lazy as _

from base.models import UserPrintTagConfiguration


class Command(BaseCommand):
    help = _('Command to create print configurations for all users.')

    def handle(self, *args, **options):
        self.stdout.write(_(u'Starting the creation of print configurations for all users.'))
        created = 0
        users = User.objects.all()

        name_x = 100.0
        name_y = 30.0
        last_name_x = 100.0
        last_name_y = 90.0
        date_x = 145.0
        date_y = 150.0

        for user in users:
            user_print_tag_configuration = UserPrintTagConfiguration.objects.filter(user=user).first()
            if user_print_tag_configuration is None:
                user_print_tag_configuration = UserPrintTagConfiguration.objects.create(
                    user=user,
                    name_x=name_x,
                    name_y=name_y,
                    last_name_x=last_name_x,
                    last_name_y=last_name_y,
                    date_x=date_x,
                    date_y=date_y
                )
                self.stdout.write(_(u'Print configuration created:'))
                print(user_print_tag_configuration)
                created = created + 1

        self.stdout.write(_(str(created) + u' new print tag configurations succesfully created!'))
