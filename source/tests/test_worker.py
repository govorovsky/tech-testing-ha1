import unittest
import mock

import lib.worker

class GetRedirectHitoryFromTaskTestCase(unittest.TestCase):
	class Task():
		def __init__(self, recheck, suspicious=None):
			self.data = {}
			self.data['url'] = 'url'
			self.data['recheck'] = recheck
			self.data['url_id'] = 1
			self.task_id = 1
			self.suspicious = suspicious

	def setUp(self):
		lib.utils.logger = mock.Mock()

	@mock.patch('lib.worker.get_redirect_history', 
				mock.Mock(return_value=(
						['ERROR'], 'url', 'counters'
					)
				))
	@mock.patch('lib.worker.to_unicode', mock.Mock())
	def test_isnt_reschecked(self):
		ret = lib.worker.get_redirect_history_from_task(
			task=self.Task(recheck=False), 
			timeout = 1,
		)
		self.assertTrue(ret[0])

	@mock.patch('lib.worker.get_redirect_history', 
				mock.Mock(return_value=(
						['ERROR'], 'url', 'counters'
					)
				))
	@mock.patch('lib.worker.to_unicode', mock.Mock())
	def test_is_rechecked(self):
		ret = lib.worker.get_redirect_history_from_task(
			task=self.Task(recheck=True, suspicious=True), 
			timeout = 1,
		)
		self.assertFalse(ret[0])


class WorkerTestCase(unittest.TestCase):
	def setUp(self):
		lib.worker.logger = mock.Mock()
		self.logger = lib.worker.logger

	@mock.patch('lib.worker.get_tube', mock.MagicMock())
	@mock.patch('lib.worker.os.path.exists', mock.Mock(return_value=False))
	def test_parent_stopped(self):
		config = mock.Mock()
		parent_pid = 1
		lib.worker.worker(config, parent_pid)
		self.logger.info.assert_called_with('Parent is dead. exiting')

	@mock.patch('lib.worker.os.path.exists', mock.Mock(return_value=True))
	@mock.patch('lib.worker.get_redirect_history_from_task', 
					mock.Mock(return_value=(True, 'data') 
				))
	def test_parent_run_is_input(self):
		config = mock.Mock()
		parent_pid = 1

		class WorkerTestException(Exception):
			pass

		m_input = mock.MagicMock()
		m_input.put = mock.Mock(side_effect=WorkerTestException())

		m_tube = mock.MagicMock(side_effect=[
			m_input, mock.MagicMock(name='output')
			]
		)

		with mock.patch('lib.worker.get_tube', m_tube):
			with self.assertRaises(WorkerTestException) :
				lib.worker.worker(config, parent_pid)

				
	@mock.patch('lib.worker.os.path.exists', mock.Mock(return_value=True))
	@mock.patch('lib.worker.get_redirect_history_from_task', 
					mock.Mock(return_value=(False, 'data') 
				))
	def test_parent_run_is_output(self):
		config = mock.Mock()
		parent_pid = 1

		class WorkerTestException(Exception):
			pass

		m_output = mock.MagicMock()
		m_output.put = mock.Mock(side_effect=WorkerTestException())

		m_tube = mock.MagicMock(side_effect=[
			mock.MagicMock(name='input'), m_output
			]
		)

		with mock.patch('lib.worker.get_tube', m_tube):
			with self.assertRaises(WorkerTestException):
				lib.worker.worker(config, parent_pid)


	@mock.patch('lib.worker.os.path.exists', mock.Mock(return_value=True))
	@mock.patch('lib.worker.get_redirect_history_from_task', 
					mock.Mock(return_value=False)
				)
	@mock.patch('lib.worker.get_tube')
	def test_task_acknoledge_succes(self, m_tube):
		config = mock.Mock()
		parent_pid = 1

		class WorkerTestException(Exception):
			pass

		def raise_exception(*args, **kwargs):
			raise WorkerTestException()

		m_tube().take = mock.Mock()
		m_tube().take().ack = raise_exception

		with self.assertRaises(WorkerTestException):
			lib.worker.worker(config, parent_pid)


	@mock.patch('lib.worker.os.path.exists', mock.Mock(return_value=True))
	@mock.patch('lib.worker.get_redirect_history_from_task', 
					mock.Mock(return_value=False)
				)
	@mock.patch('lib.worker.get_tube')
	def test_task_acknoledge_fail(self, m_tube):
		config = mock.Mock()
		parent_pid = 1

		from tarantool.error import DatabaseError
		def raise_exception(*args, **kwargs):
			raise DatabaseError()

		m_tube().take = mock.Mock()
		m_tube().take().ack = raise_exception

		class WorkerTestException(Exception):
			pass

		self.logger.exception = mock.Mock(side_effect=WorkerTestException())

		with self.assertRaises(WorkerTestException):
			lib.worker.worker(config, parent_pid)

