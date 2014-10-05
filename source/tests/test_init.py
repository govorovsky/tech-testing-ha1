# coding=utf-8
from bs4 import BeautifulSoup
import mock
import re
import unittest
from lib import to_unicode, to_str, get_counters, fix_market_url, GOOGLE_MARKET_URL, prepare_url, check_for_meta, \
    make_pycurl_request, get_url, ERROR_GET_URL, OK_REDIRECT, REDIRECT_HTTP, REDIRECT_META


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
        with mock.patch('lib.BeautifulSoup.find', mock.Mock(return_value=result)):
            with mock.patch('lib.re.search', mock.Mock(return_value=None)) as re_search:
                self.assertEqual(check_for_meta('test', 'test'), None)
                self.assertTrue(re_search.called, 'search for url pattern')

    def test_check_for_meta_with_httpequiv_and_content_url_search_ok(self):
        result = mock.Mock()
        url = 'test?ok=go'
        content = '423432;url=' + url
        result.__getitem__ = mock.Mock(return_value=content)
        result.attrs = {'http-equiv': 'refresh', 'content': content}
        with mock.patch('lib.BeautifulSoup.find', mock.Mock(return_value=result)):
            self.assertEqual(check_for_meta('test', 'test'), url)


    def test_check_for_meta_full(self):
        base_url = 'http://l33t.com'
        url = '/h3r3c0ms3v1l.exe'
        content = '<html> <meta http-equiv="refresh" content="5; url=' + url + '"> </html>'
        self.assertEqual(check_for_meta(content, base_url), base_url + url, 'meta find and concat')

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


class MakePyCurlTester(unittest.TestCase):
    def setUp(self):
        self.m_buff = mock.Mock()
        self.m_curl = mock.Mock()
        self.response = 'test response'
        self.uagent = 'test'
        self.redirurl = 'test.gov'
        self.timeout = 999

    def test_make_pycurl_req_no_redirect_no_uagent(self):
        with mock.patch('lib.pycurl.Curl', mock.Mock(return_value=self.m_curl)):
            with mock.patch('lib.StringIO', mock.Mock(return_value=self.m_buff)):
                self.m_buff.getvalue = lambda: self.response
                self.m_curl.getinfo = lambda ignore: None
                self.assertEqual(make_pycurl_request('test', self.timeout, None), (self.response, None))
                self.m_curl.setopt.assert_any_call(self.m_curl.TIMEOUT, self.timeout)

    def test_make_pycurl_req_with_redirect_with_uagent(self):
        with mock.patch('lib.pycurl.Curl', mock.Mock(return_value=self.m_curl)):
            with mock.patch('lib.StringIO', mock.Mock(return_value=self.m_buff)):
                self.m_buff.getvalue = lambda: self.response
                self.m_curl.getinfo = lambda ignore: self.redirurl
                self.assertEqual(make_pycurl_request('test', self.timeout, self.uagent), (self.response, self.redirurl))
                self.m_curl.setopt.assert_any_call(self.m_curl.TIMEOUT, self.timeout)
                self.m_curl.setopt.assert_any_call(self.m_curl.USERAGENT, self.uagent)


class GetUrlTester(unittest.TestCase):
    def setUp(self):
        self.url = "test.com"
        self.timeout = 777
        self.uagent = None
        self.errormsg = 'ERROR'
        self.content = 'test content'
        self.meta_url = 'http://meta.com'
        self.content_with_meta = '<html> <meta http-equiv="refresh" content="5; url=' + self.meta_url + '"> </html>'
        self.ok_redir_url = 'http://www.odnoklassniki.ru/43243st.redirect'
        self.http_redir = 'http://p3wnth4t.gov/redir'
        self.market_prefix = 'market://'
        self.market_url = 'test?=infoapp404'
        self.market_redir = self.market_prefix + self.market_url

    @mock.patch('lib.make_pycurl_request', mock.Mock(side_effect=ValueError()))
    def test_get_url_with_error(self):
        self.assertEqual(get_url(self.url, self.timeout, None), (self.url, ERROR_GET_URL, None), 'error should occur')


    def test_get_url_odnoklassniki_redirect(self):
        with mock.patch('lib.make_pycurl_request', mock.Mock(return_value=(self.content, self.ok_redir_url))):
            self.assertEqual(get_url(self.url, self.timeout, None), (None, None, self.content),
                             'ignore ok login redirects')


    def test_get_url_http_redirect(self):
        with mock.patch('lib.make_pycurl_request', mock.Mock(return_value=(self.content, self.http_redir))):
            with mock.patch('lib.prepare_url', mock.Mock(return_value=self.http_redir)) as prepare:
                self.assertEqual(get_url(self.url, self.timeout, None), (self.http_redir, REDIRECT_HTTP, self.content),
                                 'simple http redir')
                prepare.assert_called_once_with(self.http_redir)


    def test_get_url_with_meta_redirect(self):
        with mock.patch('lib.make_pycurl_request', mock.Mock(return_value=(self.content_with_meta, None))):
            with mock.patch('lib.prepare_url', mock.Mock(return_value=self.meta_url)) as prepare:
                self.assertEqual(get_url(self.url, self.timeout, None),
                                 (self.meta_url, REDIRECT_META, self.content_with_meta),
                                 'meta redirect')
                prepare.assert_called_once_with(self.meta_url)


    def test_get_url_with_market_redirect(self):
        with mock.patch('lib.make_pycurl_request', mock.Mock(return_value=(self.content, self.market_redir))):
            self.assertEqual(get_url(self.url, self.timeout, None),
                             (GOOGLE_MARKET_URL + self.market_url, REDIRECT_HTTP, self.content),
                             ' market redirect')














