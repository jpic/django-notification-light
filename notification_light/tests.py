import unittest

from django.contrib.auth.models import User

from notification_light.contrib.user_notification.models import UserResource
from models import (Notification, Backend, UserSetting, UserNotification, Kind,
        Resource)


class NotificationTestCase(unittest.TestCase):
    def setUp(self):
        self.kind, c = Kind.objects.get_or_create(name='auth.user.update')
        self.resource, c = Resource.objects.get_or_create(pk=1)
        self.backend, c = Backend.objects.get_or_create(name='dummy')

    def test_matrix(self):
        data = [
        # get notif     kind    res     kind+resource
         (False,        None,   None,   None),
         (True,         None,   None,   True),
         (False,        None,   None,   False),
         (True,         None,   True,   True),
         (False,        None,   True,   False),
         (True,         None,   True,   None),
         (False,        None,   False,  None),
         (True,         None,   False,  True),
         (False,        None,   False,  False),
         (True,         True,   None,   None),
         (True,         True,   None,   True),
         (False,        True,   None,   False),
         (True,         True,   True,   True),
         (False,        True,   True,   False),
         (True,         True,   True,   None),
         (False,        True,   False,  None),
         (True,         True,   False,  True),
         (False,        True,   False,  False),
         (False,        False,  None,   None),
         (True,         False,  None,   True),
         (False,        False,  None,   False),
         (True,         False,  True,   True),
         (False,        False,  True,   False),
         (True,         False,  True,   None),
         (False,        False,  False,  None),
         (True,         False,  False,  True),
         (False,        False,  False,  False),
        ]

        i = 0
        for expected, kind, res, kind_res in data:
            user = User.objects.create(username=u'user%s' % i)

            if kind is not None:
                UserSetting.objects.create(user=user, kind=self.kind,
                    enabled=kind, backend=self.backend)

            if res is not None:
                UserSetting.objects.create(user=user, resource=self.resource,
                    enabled=res, backend=self.backend)

            if kind_res is not None:
                UserSetting.objects.create(user=user, resource=self.resource,
                    kind=self.kind, enabled=kind_res, backend=self.backend)

            i += 1

        notification = Notification.objects.create(kind=self.kind,
            resource=self.resource)

        i = 0
        for expected, kind, res, kind_res in data:
            user = User.objects.get(username=u'user%s' % i)

            result = UserNotification.objects.filter(user=user,
                notification__resource=self.resource,
                notification__kind=self.kind,
                backend=self.backend).count()

            if expected:
                self.assertEqual(1, result)
            else:
                self.assertEqual(0, result)

            i += 1


