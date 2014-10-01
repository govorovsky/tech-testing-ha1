from argparse import Namespace
import mock
import os
import unittest
from source import redirect_checker


class RedirectCheckerTestCase(unittest.TestCase):
    def setUp(self):
        redirect_checker.sleep = mock.Mock()
        redirect_checker.load_config_from_pyfile = mock.Mock()


    @mock.patch('source.redirect_checker.main_loop', mock.Mock())
    @mock.patch('source.redirect_checker.dictConfig', mock.Mock())
    @mock.patch('source.redirect_checker.parse_cmd_args',
                mock.Mock(return_value=Namespace(config='test', daemon=True, pidfile=None)))
    def test_run_daemon_no_pidfile(self):
        with mock.patch('source.redirect_checker.daemonize', mock.Mock()) as daemon:
            with mock.patch('source.redirect_checker.create_pidfile', mock.Mock()) as pid_creator:
                redirect_checker.main([])
                assert daemon.called
                assert not pid_creator.called, 'pid file should not created'

    @mock.patch('source.redirect_checker.main_loop', mock.Mock())
    @mock.patch('source.redirect_checker.dictConfig', mock.Mock())
    @mock.patch('source.redirect_checker.parse_cmd_args',
                mock.Mock(return_value=Namespace(config='test', daemon=True, pidfile='test.pid')))
    def test_run_daemon_with_pidfile(self):
        with mock.patch('source.redirect_checker.daemonize', mock.Mock()) as daemon:
            with mock.patch('source.redirect_checker.create_pidfile', mock.Mock()) as pid_creator:
                redirect_checker.main([])
                assert daemon.called
                assert pid_creator.called, 'pid file should created'

    @mock.patch('source.redirect_checker.main_loop', mock.Mock())
    @mock.patch('source.redirect_checker.dictConfig', mock.Mock())
    @mock.patch('source.redirect_checker.parse_cmd_args',
                mock.Mock(return_value=Namespace(config='test', daemon=False, pidfile='test.pid')))
    def test_run_no_daemon_with_pidfile(self):
        with mock.patch('source.redirect_checker.daemonize', mock.Mock()) as daemon:
            with mock.patch('source.redirect_checker.create_pidfile', mock.Mock()) as pid_creator:
                redirect_checker.main([])
                assert not daemon.called
                assert pid_creator.called, 'pid file should created'

    @mock.patch('source.redirect_checker.main_loop', mock.Mock())
    @mock.patch('source.redirect_checker.dictConfig', mock.Mock())
    @mock.patch('source.redirect_checker.parse_cmd_args',
                mock.Mock(return_value=Namespace(config='test', daemon=False, pidfile=None)))
    def test_run_no_daemon_no_pidfile(self):
        with mock.patch('source.redirect_checker.daemonize', mock.Mock()) as daemon:
            with mock.patch('source.redirect_checker.create_pidfile', mock.Mock()) as pid_creator:
                redirect_checker.main([])
                assert not daemon.called
                assert not pid_creator.called, 'pid file should created'





pass














