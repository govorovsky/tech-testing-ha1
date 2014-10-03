#!/usr/bin/env python2.7

import os
import socket
import sys
import unittest

source_dir = os.path.join(os.path.dirname(__file__), 'source')
sys.path.insert(0, source_dir)

from tests.test_notification_pusher import *
from tests.test_redirect_checker import RedirectCheckerTestCase
from tests.test_init import *


if __name__ == '__main__':
    suite = unittest.TestSuite((
        unittest.makeSuite(NotificationPusherTestCase),
        unittest.makeSuite(LoadConfigFromPyFileTestCase),
        unittest.makeSuite(DaemonizeTestCase),
        unittest.makeSuite(MakePyCurlTester),
        # unittest.makeSuite(ParseCMDArgs),
        #
        unittest.makeSuite(GetUrlTester),
        unittest.makeSuite(LibInitTestCase),
        unittest.makeSuite(RedirectCheckerTestCase),
    ))
    result = unittest.TextTestRunner().run(suite)
    sys.exit(not result.wasSuccessful())
