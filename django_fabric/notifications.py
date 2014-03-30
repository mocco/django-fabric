# -*- coding: utf8 -*-
import json
from fabric import colors
import requests


class Notifier(object):
    def message_payload(self):
        return {}

    def notification_message_context(self, instance):
        return {
            'url': self.urls[instance],
            'status': self.status_code
        }

    def pre_deploy_notify(self, instance):
        self.send_notification('Deploying %(url)s' % self.notification_message_context(instance))

    def post_deploy_notify(self, instance):
        self.send_notification('Finished deploying %(url)s it responds with status %(status)s' %
                               self.notification_message_context(instance))

    def send_notification(self, message):
        raise NotImplemented


class SlackNotifyMixin(Notifier):
    CHANNEL = '#general'
    USER_NAME = 'django-fabric'

    def send_notification(self, message):
        payload = {
            'channel': self.CHANNEL,
            'username': self.USER_NAME,
            'text': message
        }
        if getattr(self, 'ICON', None) is not None:
            payload['icon_emoji'] = ':ghost:'
            data = {'payload': json.dumps(payload)}
            if requests.post(self.URL, data=data).status_code != requests.codes.ok:
                print(colors.yellow('Could not notify Slack'))
