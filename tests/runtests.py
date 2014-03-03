#!/usr/bin/env python

from __future__ import absolute_import, division, print_function, with_statement
import gc
import locale  # system locale module, not tornado.locale
import logging
import operator
import textwrap
import sys
from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from tornado.netutil import Resolver
from tornado.options import define, options, add_parse_callback
from tornado.test.util import unittest

try:
    reduce  # py2
except NameError:
    from functools import reduce  # py3

TEST_MODULES = [
    'tests.test_user',
    'tests.test_group',
    'tests.test_post',
    'tests.test_comment'
]


def all():
    return unittest.defaultTestLoader.loadTestsFromNames(TEST_MODULES)


class ChapStreamTextTestRunner(unittest.TextTestRunner):
    def run(self, test):
        result = super(ChapStreamTextTestRunner, self).run(test)
        if result.skipped:
            skip_reasons = set(reason for (test, reason) in result.skipped)
            self.stream.write(textwrap.fill(
                "Some tests were skipped because: %s" %
                ", ".join(sorted(skip_reasons))))
            self.stream.write("\n")
        return result

def main():
    # The -W command-line option does not work in a virtualenv with
    # python 3 (as of virtualenv 1.7), so configure warnings
    # programmatically instead.
    import warnings
    # Be strict about most warnings.  This also turns on warnings that are
    # ignored by default, including DeprecationWarnings and
    # python 3.2's ResourceWarnings.
    warnings.filterwarnings("error")
    # setuptools sometimes gives ImportWarnings about things that are on
    # sys.path even if they're not being used.
    warnings.filterwarnings("ignore", category=ImportWarning)
    # Tornado generally shouldn't use anything deprecated, but some of
    # our dependencies do (last match wins).
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("error", category=DeprecationWarning,
                            module=r"tornado\..*")
    # The unittest module is aggressive about deprecating redundant methods,
    # leaving some without non-deprecated spellings that work on both
    # 2.7 and 3.2
    warnings.filterwarnings("ignore", category=DeprecationWarning,
                            message="Please use assert.* instead")

    logging.getLogger("tornado.access").setLevel(logging.CRITICAL)

    define('httpclient', type=str, default=None,
           callback=lambda s: AsyncHTTPClient.configure(
               s, defaults=dict(allow_ipv6=False)))
    define('ioloop', type=str, default=None)
    define('ioloop_time_monotonic', default=False)
    define('resolver', type=str, default=None,
           callback=Resolver.configure)
    define('debug_gc', type=str, multiple=True,
           help="A comma-separated list of gc module debug constants, "
           "e.g. DEBUG_STATS or DEBUG_COLLECTABLE,DEBUG_OBJECTS",
           callback=lambda values: gc.set_debug(
               reduce(operator.or_, (getattr(gc, v) for v in values))))
    define('locale', type=str, default=None,
           callback=lambda x: locale.setlocale(locale.LC_ALL, x))

    def configure_ioloop():
        kwargs = {}
        if options.ioloop_time_monotonic:
            from tornado.platform.auto import monotonic_time
            if monotonic_time is None:
                raise RuntimeError("monotonic clock not found")
            kwargs['time_func'] = monotonic_time
        if options.ioloop or kwargs:
            IOLoop.configure(options.ioloop, **kwargs)
    add_parse_callback(configure_ioloop)

    import tornado.testing
    kwargs = {"verbosity": 2}
    if sys.version_info >= (3, 2):
        # HACK:  unittest.main will make its own changes to the warning
        # configuration, which may conflict with the settings above
        # or command-line flags like -bb.  Passing warnings=False
        # suppresses this behavior, although this looks like an implementation
        # detail.  http://bugs.python.org/issue15626
        kwargs['warnings'] = False
    kwargs['testRunner'] = ChapStreamTextTestRunner
    tornado.testing.main(**kwargs)

if __name__ == '__main__':
    main()
