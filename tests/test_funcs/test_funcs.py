from bookmarker.__main__ import get_app
from bookmarker.utils.common import get_hostname


class TestFuncs:


    def test_get_hostname(self):
        url="http://127.0.0.1"
        assert get_hostname(url) == "127.0.0.1"
        url="http://ya.ru"
        assert get_hostname(url) == "ya.ru"
