#!/usr/bin/env python2.7

import os
import socket
import sys
import unittest

source_dir = os.path.join(os.path.dirname(__file__), 'source')
sys.path.insert(0, source_dir)

from tests.test_notification_pusher import *
from tests.test_redirect_checker import RedirectCheckerTestCase


if __name__ == '__main__':
    suite = unittest.TestSuite((
        #unittest.makeSuite(NotificationPusherTestCase),
        #unittest.makeSuite(LoadConfigFromPyFileTestCase),
        #unittest.makeSuite(DaemonizeTestCase),
        unittest.makeSuite(ParseCMDArgs),
        
        #unittest.makeSuite(RedirectCheckerTestCase),
    ))
    result = unittest.TextTestRunner().run(suite)
    sys.exit(not result.wasSuccessful())
