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
    status = models.CharField(max_length=24)

    def __unicode__(self):
        return u'%s on %s for %s, status: %s' % (self.notification,
            self.backend, self.user, self.status)


def dispatch_notification(sender, instance, created, **kwargs):
    if instance.resource:
        # Don't cry: hopefully, all possible cases are tested ...
        # But any help is appreciated.
        upk = lambda q: q.values_list('user__pk')
        upk_in = lambda q: Q(user__pk__in=upk(q))

        resource_kind = UserSetting.objects.filter(kind=instance.kind,
            resource=instance.resource)

        resource_kind_include = upk(resource_kind.filter(enabled=True))
        resource_kind_exclude = upk(resource_kind.filter(enabled=False))
        include = upk_in(resource_kind_include)
        exclude = upk_in(resource_kind_exclude)

        resource = UserSetting.objects.filter(resource=instance.resource)
        resource_include = upk(resource.filter(enabled=True))
        resource_exclude = upk(resource.filter(enabled=False))
        include |= (upk_in(resource_include) & ~upk_in(resource_kind_exclude))
        exclude |= (upk_in(resource_exclude) & ~upk_in(resource_kind_include))

        kind = UserSetting.objects.filter(kind=instance.kind)
        include |= (upk_in(kind.filter(enabled=True))
            & ~(upk_in(resource_kind_exclude) | upk_in(resource_exclude)))
        exclude |= (upk_in(kind.filter(enabled=False))
            & ~(upk_in(resource_kind_include) | upk_in(resource_include)))

        subscriptions = UserSetting.objects.filter(include).exclude(exclude)
    else:
        subscriptions = UserSetting.objects.filter(kind=instance.kind,
                                                   enabled=True)

    seen = []
    for subscription in subscriptions.distinct():
        if subscription.user_id in seen:
            continue

        UserNotification.objects.create(user=subscription.user,
            backend=subscription.backend, notification=instance)

        seen.append(subscription.user_id)

signals.post_save.connect(dispatch_notification, sender=Notification)
