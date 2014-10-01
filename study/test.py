import unittest

import mock
from mock import *

import main

class MainTestCases(unittest.TestCase):
	
	#@patch('main.func')
	#def test_func(self, m_func):
	#	m_func.return_value = "0";
	#	self.assertEqual(func(), 0)

	@patch('main.func')
	def test_func(self, m_func):
		m_func.return_value = 0
		self.assertEqual(main.func(), 0)


if __name__ == '__main__':
	unittest.main()