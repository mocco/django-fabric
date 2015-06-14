# -*- coding: utf8 -*-
import json
import re
import socket
import time

import requests
from fabric import colors


class Notifier(object):
    NICK = 'django-fabric'

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


class IrcNotifyMixin(Notifier):
    SERVER = 'irc.freenode.org'
    PORT = 6667
    ROOMS = []
    TIMEOUT = 25

    def post_deploy_notify(self, instance):
        pass

    def send_notification(self, message):
        irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        irc.settimeout(self.TIMEOUT)
        irc.connect((self.SERVER, self.PORT))
        irc.send("USER %s %s %s :django-fabric\n" % ((self.NICK,) * 3))
        irc.send("NICK %s\n" % self.NICK)
        start = time.time()
        while (time.time() - start) < self.TIMEOUT:
            irc_message = irc.recv(2048).strip('\n\r')
            pong = re.compile(r'^PING\s*:\s*(.*)$').findall(irc_message)

            if pong:
                irc.send("PONG %s\n" % pong)

            if re.findall(' 00[1-4] %s' % self.NICK, irc_message):
                for room in self.ROOMS:
                    irc.send("JOIN %s\n" % room)
                    irc.send("PRIVMSG %s :%s\n" % (room, message))
                    irc.send("PART %s\n" % room)

                break

        irc.send("QUIT\n")
        irc.close()


class SlackNotifyMixin(Notifier):
    CHANNEL = '#general'

    def send_notification(self, message):
        payload = {
            'channel': self.CHANNEL,
            'username': self.NICK,
            'text': message
        }
        data = {'payload': json.dumps(payload)}
        if requests.post(self.URL, data=data).status_code != requests.codes.ok:
            print(colors.yellow('Could not notify Slack'))


class HipChatNotifyMixin(Notifier):
    URL = 'https://api.hipchat.com/v2/room/%s/notification?auth_token=%s'
    COLOR = 'yellow'
    NOTIFY = False

    def send_notification(self, message):
        payload = {
            'message': message,
            'color': self.COLOR,
            'notify': self.NOTIFY
        }
        url = self.URL % (self.ROOM, self.HIPCHAT_TOKEN)
        data = {'payload': json.dumps(payload)}

        if requests.post(url, data=data).status_code != requests.codes.ok:
            print(colors.yellow('Could not notify HipChat'))
