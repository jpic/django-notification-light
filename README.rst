.. image:: https://secure.travis-ci.org/yourlabs/django-notification-light.png?branch=master

django-notification-light attemps to provide a fresh approach on the
notification problem. Although composed of several simple models and relies on
signals, it manages to solves most problems with full flexibility, using model
subclasses. It also provides common features: user notification settings page,
email notification backend, widget (facebook-like) notification backend.

Models
------

Kind
    A notification kind, just has a name.

Backend
    A notification backend, just has a name.

Resource
    An empty model which should be subclasses. Two subclasses are provided:
    ModelResource and URLResource. You could create any subclass you want, with
    relations and fields that you want.

Notification
    Has a Kind, an (automatic) creating date, may have a Resource.

UserNotification
    Has a User, a Notification, a Backend, and booleans "sent" and "read".

UserSetting
    Has a User, a Kind, a Backend, and a boolean "enabled". It may have a
    Resource.

A subscription could be represented by a UserSetting with enabled=True. A
user can thus subscribe to:

- a particular notification kind on a particular resource, has priority
- a particular resource, has less priority
- a particular kind, used if no more precise UserSetting exist.

Workflow
--------

`notification_light.contrib.user_notification` demonstrates how CRUD
notifications would work for the User model. It works as such:

- on User.post_save, create the Notification on the right Kind using
  user.userresource,
- Notification.post_save is recieved by notification_light's dispatcher, and
  creates the appropriate UserNotification objects,
- UserNotification.post_save is recieved by each backend, which may set
  UserNotification.status to whatever value it wants.

Install
-------

- add to INSTALLED_APPS: `'notification_light',`
- add to urls.py: `url(r'notification/$', include('notification_light.urls')),`
- add to your template, after loading jquery: `{% include 'notification_light/static.html' %}`,
- add to your template, where you want: `{% include 'notification_light/widget.html' %}`.
