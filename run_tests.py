#!/usr/bin/env python2.7

import os
import socket
import sys
import unittest

source_dir = os.path.join(os.path.dirname(__file__), 'source')
sys.path.insert(0, source_dir)

from tests.test_redirect_checker import RedirectCheckerTestCase
from tests.test_init import *

import tests.test_utils
import tests.test_worker
import tests.test_notification_pusher

if __name__ == '__main__':
    suite = unittest.TestSuite((
        unittest.makeSuite(MakePyCurlTester),
        unittest.makeSuite(RedirectHistoryChecker),
        unittest.makeSuite(GetUrlTester),
        unittest.makeSuite(LibInitTestCase),
        unittest.makeSuite(RedirectCheckerTestCase),
        
        unittest.makeSuite(tests.test_notification_pusher.MainLoopTestCase),
        unittest.makeSuite(tests.test_notification_pusher.StopHandlerTestCase),
        unittest.makeSuite(tests.test_notification_pusher.DoneWithProcessedTasks),
        unittest.makeSuite(tests.test_notification_pusher.NotificationWorkeCaseTest),
        unittest.makeSuite(tests.test_notification_pusher.InstallSignalHandlersTestCase),
        unittest.makeSuite(tests.test_notification_pusher.MainTestCase),

        unittest.makeSuite(tests.test_utils.DaemonizeTestCase),
        unittest.makeSuite(tests.test_utils.CreatePidFileTestCase),
        unittest.makeSuite(tests.test_utils.ParseCMDArgsTestCase),
        unittest.makeSuite(tests.test_utils.GetTubeTestCase),
        unittest.makeSuite(tests.test_utils.SpawnWorkerTestCase),
        unittest.makeSuite(tests.test_utils.CheckNetworkStatusTestCase),
        unittest.makeSuite(tests.test_utils.LoadConfigFromPyFileTestCase),
        
        unittest.makeSuite(tests.test_worker.GetRedirectHitoryFromTaskTestCase),
        unittest.makeSuite(tests.test_worker.WorkerTestCase),
        
    ))
    result = unittest.TextTestRunner().run(suite)
    sys.exit(not result.wasSuccessful())
