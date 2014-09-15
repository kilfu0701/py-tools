import sys

class Debug(object):
    def __init__(self, level=3):
        self.level = level
        self._pv = {
            'log': 3,
            'debug': 2,
            'error': 1,
        }

    def log(self, msg='', *args, **kwargs):
        self._pr(sys._getframe().f_code.co_name, msg, *args)

    def debug(self, msg='', *args, **kwargs):
        self._pr(sys._getframe().f_code.co_name, msg, *args)

    def error(self, msg='', *args, **kwargs):
        self._pr(sys._getframe().f_code.co_name, msg, *args)

    def _pr(self, func, msg, *args):
        if self.level >= self._pv[func]:
            print '[{0}] {1} {2}'.format(func.upper(), repr(msg), ' '.join(map(repr, args)))


