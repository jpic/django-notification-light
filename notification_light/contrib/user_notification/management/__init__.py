from django.db.models.signals import post_syncdb

import notification_light.models


def notification_types(sender, **kwargs):
    from notification_light.models import Kind

    Kind.objects.get_or_create(name='auth.user.create')
    Kind.objects.get_or_create(name='auth.user.update')
post_syncdb.connect(notification_types, sender=notification_light.models)
