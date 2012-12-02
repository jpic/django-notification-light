from django.db.models import signals
from django.db import models
from django.contrib.auth.models import User

from annoying.fields import AutoOneToOneField

from notification_light.models import (Kind, UserNotification, Resource,
                                       Notification)


class UserResource(Resource):
    user = AutoOneToOneField('auth.User')

    def __unicode__(self):
        return unicode(self.user)


def user_notification(sender, instance, created, **kwargs):
    if created:
        name = 'auth.user.create'
    else:
        name = 'auth.user.update'

    kind = Kind.objects.get(name=name)
    notification = Notification.objects.create(kind=kind,
                                               resource=instance.userresource)
signals.post_save.connect(user_notification, sender=User)
