# coding=utf-8
from bs4 import BeautifulSoup
import mock
import re
import unittest
from lib import to_unicode, to_str, get_counters, fix_market_url, GOOGLE_MARKET_URL, prepare_url, check_for_meta


class LibInitTestCase(unittest.TestCase):
    def setUp(self):
        pass


    def test_to_unicode_with_unicode_source(self):
        src = u'te12kiooщщщйраloe'
        assert isinstance(to_unicode(src), unicode)

    def test_to_unicode_with_str_source(self):
        src = 'tes12314l'
        assert isinstance(to_unicode(src), unicode)

    def test_to_str_with_str_source(self):
        src = 'testkjlsa'
        assert isinstance(to_str(src), str)

    def test_to_str_with_unicode_source(self):
        src = u'рщырыщрызtestkjlsa'
        assert isinstance(to_str(src), str)


    def test_counters_non_empty(self):
        counter_name = ['DOUBLECLICK']
        content = 'https://googleads.g.doubleclick.net/pagead/viewthroughconversion?=blbla14342'
        self.assertEqual(get_counters(content), counter_name)

    def test_counters_empty(self):
        content = 'https://goog!@leads.g.doubleclick.net/pagead/viewthroughconversion?=blbla14342'
        self.assertEqual(get_counters(content), [])


    def test_fix_market_url(self):
        prefix = 'market://'
        source = 'details?test.com'
        self.assertEqual(fix_market_url(prefix + source), GOOGLE_MARKET_URL + source)

    def test_prepare_url_empty_src(self):
        self.assertEqual(prepare_url(None), None)

    def test_prepare_url_non_empty_src(self):
        url_part = mock.MagicMock()
        with mock.patch('lib.urlparse', mock.Mock(return_value=[url_part] * 6)) as parser:
            prepare_url('test_url')
            assert parser.called
            assert url_part.encode.called


    def test_check_for_meta_without_meta_tag(self):
        result = mock.Mock()
        result.attrs = {}
        with mock.patch.object(BeautifulSoup, 'find', mock.Mock(return_value=result)):
            self.assertEqual(check_for_meta('test', 'test'), None)


    def test_check_for_meta_with_incorrect_meta_tag(self):
        result = mock.Mock()
        result.attrs = {'content': 10}
        with mock.patch.object(BeautifulSoup, 'find', mock.Mock(return_value=result)):
            self.assertEqual(check_for_meta('test', 'test'), None)


    def test_check_for_meta_with_httpequiv_and_bad_content(self):
        result = mock.Mock()
        content = '423432'
        result.__getitem__ = mock.Mock(return_value=content)
        result.attrs = {'http-equiv': 'refresh', 'content': 10}
        with mock.patch.object(BeautifulSoup, 'find', mock.Mock(return_value=result)):
            self.assertEqual(check_for_meta('test', 'test'), None)

    def test_check_for_meta_with_httpequiv_and_content_url_search_fail(self):
        result = mock.Mock()
        content = '423432;url=blabla'
        result.__getitem__ = mock.Mock(return_value=content)
        result.attrs = {'http-equiv': 'refresh', 'content': content}
        with mock.patch.object(BeautifulSoup, 'find', mock.Mock(return_value=result)):
            with mock.patch.object(re, 'search', mock.Mock(return_value=None)) as re_search:
                self.assertEqual(check_for_meta('test', 'test'), None)
                self.assertTrue(re_search.called, 'search for url pattern')

    def test_check_for_meta_with_httpequiv_and_content_url_search_ok(self):
        result = mock.Mock()
        url = 'test?ok=go'
        content = '423432;url=' + url
        result.__getitem__ = mock.Mock(return_value=content)
        result.attrs = {'http-equiv': 'refresh', 'content': content}
        with mock.patch.object(BeautifulSoup, 'find', mock.Mock(return_value=result)):
            self.assertEqual(check_for_meta('test', 'test'), url)



