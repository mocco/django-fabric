Notifications
=============
It is always great to notify your team that you are deploying. django-fabric makes it easy
to do that automatically.

.. currentmodule:: django_fabric.notifications

Built in notification mixins
----------------------------
There are some built in mixins. To use them add them to your class in your fabfile and make sure you
add the attributes necessary. They should have defaults for values that are not used to authenticate
you with the given service.

.. class:: SlackNotifyMixin

    A mixin that notifies a channel on the `Slack <http://slack.com/>`_. Requires to set the attribute URL.

    .. attribute:: CHANNEL

        Default: '#general'
        The channel to post the notification in.

    .. attribute:: USER_NAME

        Default: 'django-fabric'
        The nick that should appear in Slack when the notification is sent.

    .. attribute:: URL

        The Slack POST URL. Can be found at `slack.com/services/new/incoming-webhook
        <http://slack.com/services/new/incoming-webhook>`_.

Build your own notification mixin
---------------------------------
If we do not support your chat service, bot or whatever you want to notify it should not be
a problem. It is pretty easy to create your own notification mixin. Just create a class that
inherit from the :code:`Notifier` class and overwrite the methods you need to customize.
Remember you must at least override :ref:`send_notification`. If you think your notification
mixin can be useful for others a pull-request is appreciated.

.. class:: Notifier

    .. method:: message_payload(self):

    .. method:: notification_message_context(self, instance):

        Provides the context used in :code:`pre_deploy_notify()` and :code:`post_deploy_notify()`.

    .. method:: pre_deploy_notify(self, instance):

        The method that sends notification before deployment. This should generate the message and
        call :code:`send_notification`.

    .. method:: post_deploy_notify(self, instance):

        The method that sends notification after deployment. This should generate the message and
        call :code:`send_notification`.

    .. method:: send_notification(self, message):

        This method actually sends the notification. The logic that talks to the service should be
        put here. This method needs to be implemented in the subclass or it will raise a
        NotImplementedError.