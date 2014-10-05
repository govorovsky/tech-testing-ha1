import unittest
import mock

import lib.utils


class DaemonizeTestCase(unittest.TestCase):
	@mock.patch('lib.utils.os.fork', mock.Mock(side_effect=OSError()))
	def test_fork_exception(self):
		with self.assertRaises(Exception):
			lib.utils.daemonize()

	@mock.patch('lib.utils.os.setsid', mock.Mock())
	@mock.patch('lib.utils.os.fork')
	def test_child_child(self, m_fork):
		m_fork.return_value = 0
		lib.utils.daemonize()
		self.assertEqual(m_fork.call_count, 2)

	@mock.patch('lib.utils.os.setsid', mock.Mock())
	@mock.patch('lib.utils.os.fork', mock.Mock(side_effect=[0,1]))
	@mock.patch('lib.utils.os')
	def test_child_child(self, m_os):
		m_os._exit = mock.Mock();
		lib.utils.daemonize()
		m_os._exit.assert_called_once_with(0)

	
	@mock.patch('lib.utils.os.fork', mock.Mock(side_effect=[0, OSError()]))
	@mock.patch('lib.utils.os.setsid', mock.Mock())
	def test_child_exception(self):
		with self.assertRaises(Exception):
			lib.utils.daemonize()
		

	@mock.patch('lib.utils.os.fork', mock.Mock(return_value=1))
	@mock.patch('lib.utils.os')
	def test_parent(self, m_os):
		m_os._exit = mock.Mock();
		lib.utils.daemonize()
		m_os._exit.assert_called_once_with(0)


class CreatePidFileTestCase(unittest.TestCase):
	def test_create_pidfile(self):
		pid = 1
		filepath = '/file/path'

		m_open = mock.mock_open()
		with mock.patch('lib.utils.open', m_open, create=True):
			with mock.patch('lib.utils.os.getpid', mock.Mock(return_value=pid)):
				lib.utils.create_pidfile(filepath)

		m_open.assert_called_once_with(filepath, 'w')
		m_open().write.assert_called_once_with(str(pid))


class ParseCMDArgsTestCase(unittest.TestCase):
	@mock.patch("lib.utils.argparse")
	def test_params(self, m_argparse):
		lib.utils.parse_cmd_args("args")
		m_argparse.ArgumentParser.assert_called_once()


class GetTubeTestCase(unittest.TestCase):
	@mock.patch('lib.utils.tarantool_queue.Queue')
	def test_return(self, m_queue):
		m_queue.tube = mock.Mock()
		lib.utils.get_tube(host='host', port=1, space=1, name="name")
		m_queue.tube.assert_called_once()

class SpawnWorkerTestCase(unittest.TestCase):
	@mock.patch('lib.utils.Process')
	def test_start(self, m_process):
		num = 10
		lib.utils.spawn_workers(num, 'target', 'args', 'pid')
		self.assertEqual(m_process().start.call_count, num)


class CheckNetworkStatusTestCase(unittest.TestCase):
	@mock.patch('lib.utils.urllib2.urlopen', mock.Mock())
	def test_is_connected(self):
		self.assertTrue(lib.utils.check_network_status('url', 'timeout'))
	
	@mock.patch('lib.utils.urllib2.urlopen', mock.Mock(side_effect=ValueError()))
	def test_is_connected(self):
		self.assertFalse(lib.utils.check_network_status('url', 'timeout'))


class LoadConfigFromPyFileTestCase(unittest.TestCase):

	@mock.patch('lib.utils.Config', mock.Mock())
	def test_invoke_execfile(self):
		filepath = "/file/path"
		variables = {}
		with mock.patch('__builtin__.execfile', mock.Mock()) as m_exec:
			lib.utils.load_config_from_pyfile(filepath)
			m_exec.assert_called_once_with(filepath, variables)

	def test_set_attr(self):
		def fill_variables(filepath, variables):
			variables["KEY1"] = 'val1'
			variables["key2"] = 'val2'
	
		with mock.patch('__builtin__.execfile', fill_variables):
			cfg = lib.utils.load_config_from_pyfile('/path/file')
			self.assertEqual(getattr(cfg, 'KEY1'), 'val1')

		with self.assertRaises(Exception):
			getattr(cfg, 'key2')