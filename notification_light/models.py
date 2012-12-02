from django.db import models
from django.db.models import signals
from django.db.models import Q

from model_utils.managers import InheritanceManager


class Notification(models.Model):
    kind = models.ForeignKey('Kind')
    resource = models.ForeignKey('Resource')
    created = models.DateTimeField(auto_now_add=True)

    objects = InheritanceManager()

    def __unicode__(self):
        return u'%s for %s dated %s' % (self.kind, self.resource, self.created)

    class Meta:
        ordering = ('-created',)


class Resource(models.Model):
    objects = InheritanceManager()

    def get_subclass(self):
        return Resource.objects.get_subclass(pk=self.pk)

    def __unicode__(self):
        return unicode(self.get_subclass())


class Kind(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __unicode__(self):
        return self.name


class Backend(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __unicode__(self):
        return self.name


class UserSetting(models.Model):
    user = models.ForeignKey('auth.User')
    backend = models.ForeignKey('Backend')
    kind = models.ForeignKey('Kind', null=True, blank=True)
    resource = models.ForeignKey('Resource', null=True, blank=True)
    enabled = models.BooleanField()

    def __unicode__(self):
        return u'%s for %s on %s: %s' % (self.user, self.kind, self.backend,
                                         self.enabled)


class UserNotification(models.Model):
    user = models.ForeignKey('auth.User')
    notification = models.ForeignKey('Notification')
    backend = models.ForeignKey('Backend')
    sent = models.BooleanField()
    read = models.BooleanField()

    def __unicode__(self):
        return u'%s on %s for %s, sent: %s, read: %s' % (self.notification,
            self.backend, self.user, self.sent, self.read)


def dispatch_notification(sender, instance, created, **kwargs):
    enabled = UserSetting.objects.filter(kind=instance.kind, enabled=True)

    subscriptions_to_kind = UserSetting.objects.filter(
            kind=instance.kind, enabled=True, resource=None)

    if instance.resource:
        subscriptions_to_resource_and_kind = UserSetting.objects.filter(
                kind=instance.kind, resource=instance.resource, enabled=True)
        subscriptions_to_resource = UserSetting.objects.filter(
                resource=instance.resource, enabled=True)

        subscriptions = UserSetting.objects.filter(Q(
            pk__in=subscriptions_to_kind.values_list('pk'))|Q(
            pk__in=subscriptions_to_resource.values_list('pk'))|Q(
            pk__in=subscriptions_to_resource_and_kind.values_list('pk')))
    else:
        subscriptions = subscriptions_to_kind

    for subscription in subscriptions:
        UserNotification.objects.create(user=subscription.user,
                backend=subscription.backend, notification=instance)

signals.post_save.connect(dispatch_notification, sender=Notification)
