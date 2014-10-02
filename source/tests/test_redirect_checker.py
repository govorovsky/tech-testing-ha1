from argparse import Namespace
import mock
import unittest
from source import redirect_checker


def stop_redirect_checker(args):
    redirect_checker.isRunning = False


class RedirectCheckerTestCase(unittest.TestCase):
    def setUp(self):
        redirect_checker.isRunning = True
        self.config = mock.Mock()
        self.config.WORKER_POOL_SIZE = 42
        self.config.SLEEP = 1
        redirect_checker.sleep = mock.Mock(side_effect=stop_redirect_checker)
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

    @mock.patch('source.redirect_checker.check_network_status', mock.Mock(return_value=False))
    def test_run_without_network(self):
        child = mock.Mock()
        child_count = 12
        redirect_checker.active_children = lambda: [child] * child_count
        redirect_checker.main_loop(self.config)
        self.assertEqual(child.terminate.call_count, child_count, 'all childs must terminate')
        assert redirect_checker.sleep.called

    @mock.patch('source.redirect_checker.check_network_status', mock.Mock(return_value=True))
    def test_run_with_network_positive_workers_count(self):
        with mock.patch('source.redirect_checker.spawn_workers') as workers:
            child = mock.Mock()
            redirect_checker.active_children = lambda: [child]
            redirect_checker.main_loop(self.config)
            assert redirect_checker.sleep.called
            self.assertEqual(workers.call_count, 1, 'only one iteration')


    @mock.patch('source.redirect_checker.check_network_status', mock.Mock(return_value=True))
    def test_run_with_network_negative_workers_cnt(self):
        with mock.patch('source.redirect_checker.spawn_workers') as workers:
            self.config.WORKER_POOL_SIZE = 1
            redirect_checker.active_children = lambda: [1, 2, 3]
            redirect_checker.main_loop(self.config)
            assert redirect_checker.sleep.called
            assert not workers.called, 'no workers can be instantiated'


pass














