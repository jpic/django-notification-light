import unittest

from django.contrib.auth.models import User

from notification_light.contrib.user_notification.models import UserResource
from models import Notification, Backend, UserSetting, UserNotification, Kind


class NotificationTestCase(unittest.TestCase):
    def tearDown(self):
        User.objects.all().delete()

    def setUp(self):
        self.create, c = Kind.objects.get_or_create(
                name='auth.user.create')
        self.update, c = Kind.objects.get_or_create(
                name='auth.user.update')
        self.backend, c = Backend.objects.get_or_create(name='dummy')

        self.watch_all = User.objects.create(username='watch_all')
        UserSetting.objects.create(user=self.watch_all, kind=self.create,
                backend=self.backend, enabled=True)
        UserSetting.objects.create(user=self.watch_all, kind=self.update,
                backend=self.backend, enabled=True)

        self.watch_create = User.objects.create(username='watch_create')
        UserSetting.objects.create(user=self.watch_create, kind=self.create,
                backend=self.backend, enabled=True)

        self.watch_update = User.objects.create(username='watch_update')
        UserSetting.objects.create(user=self.watch_update, kind=self.update,
                backend=self.backend, enabled=True)

        self.parent = User.objects.create(username='parent')
        self.child = User.objects.create(username='child')
        UserSetting.objects.create(user=self.parent, kind=self.update,
                backend=self.backend, enabled=True,
                resource=self.child.userresource)

        # clean notifications create by setUp
        Notification.objects.all().delete()

    def test_create_kind_subscription(self):
        u = User.objects.create(username='foo')

        self.assertEqual(2, UserNotification.objects.count())

        UserNotification.objects.get(user=self.watch_all,
                backend=self.backend,
                notification__resource=u.userresource,
                notification__kind__name='auth.user.create',
                read=False, sent=False)

        UserNotification.objects.get(user=self.watch_create,
                backend=self.backend,
                notification__resource=u.userresource,
                notification__kind__name='auth.user.create',
                read=False, sent=False)

    def test_update_kind_subscription(self):
        self.parent.save()

        self.assertEqual(2, UserNotification.objects.count())

        UserNotification.objects.get(user=self.watch_all,
                backend=self.backend,
                notification__resource=self.parent.userresource,
                notification__kind__name='auth.user.update',
                read=False, sent=False)

        UserNotification.objects.get(user=self.watch_update,
                backend=self.backend,
                notification__resource=self.parent.userresource,
                notification__kind__name='auth.user.update',
                read=False, sent=False)

    def test_update_resource_subscription(self):
        self.child.save()

        self.assertEqual(3, UserNotification.objects.count())

        UserNotification.objects.get(user=self.parent,
                backend=self.backend,
                notification__resource=self.child.userresource,
                notification__kind__name='auth.user.update',
                read=False, sent=False)

        UserNotification.objects.get(user=self.watch_all,
                backend=self.backend,
                notification__resource=self.child.userresource,
                notification__kind__name='auth.user.update',
                read=False, sent=False)

        UserNotification.objects.get(user=self.watch_update,
                backend=self.backend,
                notification__resource=self.child.userresource,
                notification__kind__name='auth.user.update',
                read=False, sent=False)
