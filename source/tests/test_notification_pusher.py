import unittest
import mock

from mock import Mock
from notification_pusher import *


class NotificationPusherTestCase(unittest.TestCase):
	def test_create_pidfile(self):
		pid = 42
		m_open = mock.mock_open()
		with mock.patch('notification_pusher.open', m_open, create=True):
			with mock.patch('os.getpid', mock.Mock(return_value=pid)):
				create_pidfile('/file/path')

		m_open.assert_called_once_with('/file/path', 'w')
		m_open().write.assert_called_once_with(str(pid))


#TODO: exception no file?
class LoadConfigFromPyFileTestCase(unittest.TestCase):
	
	def setUp(self):
		self.mock_exec = Mock()

	def test_invoke_execfile(self):
		filepath = "/file/path"
		variables = {}

		with mock.patch('__builtin__.execfile', self.mock_exec):
			load_config_from_pyfile(filepath)

		self.mock_exec.assert_called_once_with(filepath, variables)

	def test_set_attr(self):
		def fill_variables(filepath, variables):
			variables["KEY1"] = 'val1'
			variables["key2"] = 'val2'
		
		with mock.patch('__builtin__.execfile', fill_variables):
			cfg = load_config_from_pyfile('/path/file')

		self.assertEqual(getattr(cfg, 'KEY1'), 'val1')
		#khuevo
		with self.assertRaises(Exception):
			getattr(cfg, 'key2')

#TODO: setup for fork branches
class DaemonizeTestCase(unittest.TestCase):
	@mock.patch('notification_pusher.os')
	def test_fork_exception(self, mock_os):
		def raise_oserror():
			raise OSError(1, 'test message')

		mock_os.fork = raise_oserror

		with self.assertRaises(Exception) as exc:
			daemonize()

		self.assertIn('test message [1]', str(exc.exception))
	

	@mock.patch('notification_pusher.os')
	def test_child_is_daemon(self, mock_os):
		count = [0]
		def call_fork():
			count[0] += 1
			return 0

		mock_os.fork.side_effect = call_fork

		daemonize()

		mock_os.setsid.assert_called_once()
		self.assertEqual(count[0], 2)

	#side_effect = [0, 42]
	@mock.patch('notification_pusher.os')
	def test_child_is_failed(self, mock_os):
		count = [0]
		def call_fork():
			if (count[0] == 0):
				count[0] += 1
				return 0
			else:
				raise OSError(1, 'test message')

		mock_os.fork.side_effect = call_fork

		with self.assertRaises(Exception) as exc:
			daemonize()

		self.assertIn('test message [1]', str(exc.exception))


	@mock.patch('notification_pusher.os')
	def test_grandpa_exit(self, mock_os):
		mock_os.fork.return_value = 42
		daemonize()
		mock_os._exit.assert_called_once_with(0)


	@mock.patch('notification_pusher.os')
	def test_parent_is_failed(self, mock_os):
		count = [0]
		def call_fork():
			if (count[0] == 0):
				count[0] += 1
				return 0
			else:
				return 42

		mock_os.fork.side_effect = call_fork
		daemonize()
		mock_os._exit.assert_called_once_with(0)


class ParseCMDArgsTestCase(unittest.TestCase):

	@mock.patch("notification_pusher.argparse")
	def test_params(self, mock_argparse):
		parse_cmd_args("args")
		mock_argparse.ArgumentParser.assert_called_once()


class MainLoopTestCase(unittest.TestCase):

	@mock.patch("notification_pusher.run_application")
	@mock.patch("notification_pusher.logger")
	def test_main_path(self, mock_run, mock_log):
		mock_run = False

		mock_config = Mock()
		mock_config.QUEUE_PORT = 0

		main_loop(mock_config)
		mock.log.info.assert_called_once_with('Stop application loop.')


		