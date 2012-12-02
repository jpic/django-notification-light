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
    Has a Kind, a Resource and an (automatic) creating date.

UserNotification
    Has a User, a Notification, a Backend, and booleans "sent" and "read".

UserSetting
    Has a User, a Kind, a Backend, and a boolean "enabled". It may have a
    Resource.

Scenarios
---------

Consider a simple "Announce" model in an external app "announces", which
decided to use URLResource.

- User enables "Email backend" on "New announce" notification Kind.
- User enables "Widget backend" on "New announce" notification Kind.
- On Announce save, the announces app has a post_save receiver for when created=True:
  - URLResource is created with name=Announce.__unicode__() and
      url=Announce.get_absolute_url,
  - Notification is created with kind="New announce" and resource=<resource
      created above>
  - notification_light receives post_save for Notification if created=True:
    - Using defined UserSetting, it creates the right UserNotification instances
      with sent=False and read=False,
    - The "Email backend" has a pre_save receiver for UserNotification, if the
      backend name is "notification_light.contrib.email_backend" and sent=False
      then it will send the email and set sent=True. This backend does not care
      about the "read" attribute of the UserNotification.
    - The widget backend shows all UserNotification, when the user clicks on a
      notification it will set read=True and redirect the user. This backend does
      not care about the "sent" attribute of the UserNotification

Because UserSetting has an optionnal FK to Resource, a user may enable or
disable a notification type for a backend on a specific resource.

Install
-------

- add to INSTALLED_APPS: `'notification_light',`
- add to urls.py: `url(r'notification/$', include('notification_light.urls')),`
- add to your template, after loading jquery: `{% include 'notification_light/static.html' %}`,
- add to your template, where you want: `{% include 'notification_light/widget.html' %}`.
