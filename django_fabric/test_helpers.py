from fabric import colors


class Response(object):
    failed = False


class TestMixin(object):
    """
    Overrides run to only log to a file
    """

    def run(self, command):
        self.notify(colors.cyan('run(%s)' % command))
        return 'run output'

    def local(self, command, *args, **kwargs):
        self.notify(colors.cyan('local(%s)' % command))
        return Response()

    def exists(self, *args, **kwargs):
        self.notify(colors.cyan('exists(%s, %s)' % (args, kwargs)))

    def get(self, *args, **kwargs):
        self.notify(colors.cyan('get(%s, %s)' % (args, kwargs)))
