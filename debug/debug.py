import sys

class Debug(object):
    def __init__(self, level=3):
        self.level = level
        self._pv = {
            'log': 3,
            'debug': 2,
            'error': 1,
        }

    def log(self, msg='log'):
        self._pr(sys._getframe().f_code.co_name, msg)

    def debug(self, msg='debug'):
        self._pr(sys._getframe().f_code.co_name, msg)

    def error(self, msg='error'):
        self._pr(sys._getframe().f_code.co_name, msg)

    def _pr(self, func, msg):
        if self.level >= self._pv[func]:
            print '[{0}] {1}'.format(func.upper(), repr(msg))




