import unittest
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from urllib.error import URLError
from bookmarker.utils.bookmark import get_page_title

class TestGetPageTitle(unittest.TestCase):

    @patch('bookmarker.utils.bookmark.get_title.urlopen')
    def test_get_page_title_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'<html><head><title>Mock Page Title</title></head></html>'
        mock_urlopen.return_value = mock_response

        title = get_page_title("http://example.com")

        self.assertEqual(title, "Mock Page Title")

    @patch('bookmarker.utils.bookmark.get_title.urlopen')
    def test_get_page_title_no_title(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'<html><head><p>Mock Page Title</p></head></html>'
        mock_urlopen.return_value = mock_response
        title = get_page_title("http://example.com")

        self.assertEqual(title, "")


    @patch('bookmarker.utils.bookmark.get_title.urlopen')
    def test_get_page_title_failure(self, mock_urlopen):
        mock_urlopen.side_effect = URLError('Error')

        title = get_page_title("http://invalid-url.com")

        self.assertIsNone(title)
