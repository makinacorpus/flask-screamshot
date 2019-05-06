from unittest import TestCase, mock
from unittest.mock import MagicMock

from src.views import take_screenshot_view


class Form():
    def to_dict(self):
        return {'wait_until': 'load'}
class GetRequest():
    def __init__(self):
        self.args = {'url': 'http://fake'}
        self.method = 'GET'
        self.form = Form()
class PostRequest():
    def __init__(self):
        self.args = {'url': 'http://fake'}
        self.method = 'POST'
        self.form = Form()
class NoUrlRequest():
    def __init__(self):
        self.args = {}
        self.method = 'POST'
        self.form = Form()


class ScreenshotSerializer():
    def __init__(self, url, raw_data=None):
        self.url = url
        self.raw_data = raw_data
    def serialize(self):
        return self.url, self.raw_data


class TestViewUnit(TestCase):
    @mock.patch('src.views.jsonify')
    @mock.patch('src.views.request', GetRequest())
    @mock.patch('src.views.ScreenshotSerializer', ScreenshotSerializer)
    def test_view_get_request(self, jsonify_mock):
        jsonify_mock.side_effect = lambda a: a
        url, raw_data = take_screenshot_view()
        self.assertEqual(url, 'http://fake')
        self.assertEqual(raw_data, None)

    @mock.patch('src.views.jsonify')
    @mock.patch('src.views.request', PostRequest())
    @mock.patch('src.views.ScreenshotSerializer', ScreenshotSerializer)
    def test_view_post_request(self, jsonify_mock):
        jsonify_mock.side_effect = lambda a: a
        url, raw_data = take_screenshot_view()
        self.assertEqual(url, 'http://fake')
        self.assertEqual(raw_data, {'wait_until': 'load'})

    @mock.patch('src.views.jsonify')
    @mock.patch('src.views.request', NoUrlRequest())
    @mock.patch('src.views.ScreenshotSerializer', ScreenshotSerializer)
    def test_view_no_url_request(self, jsonify_mock):
        jsonify_mock.side_effect = lambda a: a
        errors, status_code = take_screenshot_view()
        self.assertEqual(errors, {'errors': ['No url']})
        self.assertEqual(status_code, 400)
