from tempfile import _TemporaryFileWrapper
from unittest import TestCase, mock

from src.serializers import ScreenshotSerializer
SCREAMSHOT_PARAMETERS = ['width', 'height',
                         'wait_until', 'credentials', 'selector', 'wait_for']

class TestSerializerUnit(TestCase):
    def test_parse_raw_data(self):
        serializer = ScreenshotSerializer('http://fake')
        serializer._parse_raw_data()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {})

        serializer = ScreenshotSerializer('http://fake', raw_data={'width': 100})
        serializer._parse_raw_data()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'width': 100})

        serializer = ScreenshotSerializer('http://fake', raw_data={'width': 100, 'height': 200})
        serializer._parse_raw_data()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'width': 100, 'height': 200})

        serializer = ScreenshotSerializer('http://fake', raw_data={'bad_param': 1})
        serializer._parse_raw_data()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {})
        self.assertEqual(serializer.errors, ['Unknown parameter: "bad_param"'])

        serializer = ScreenshotSerializer('http://fake', raw_data={'width':1, 'bad_param': 1})
        serializer._parse_raw_data()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'width': 1})
        self.assertEqual(serializer.errors, ['Unknown parameter: "bad_param"'])

        serializer = ScreenshotSerializer('http://fake', raw_data={'bad_param': 1, 'width':1})
        serializer._parse_raw_data()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'width': 1})
        self.assertEqual(serializer.errors, ['Unknown parameter: "bad_param"'])

        serializer = ScreenshotSerializer('http://fake', raw_data={'bad_param': 1, 'bad_param_2':1})
        serializer._parse_raw_data()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {})
        self.assertEqual(serializer.errors, ['Unknown parameter: "bad_param"',
                                             'Unknown parameter: "bad_param_2"'])

    def test_is_valid(self):
        serializer = ScreenshotSerializer('http://fake', raw_data={'width': 'coucou'})
        serializer.is_valid()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'width': 'coucou'})
        self.assertEqual(serializer.errors, ['Bad width'])

        serializer = ScreenshotSerializer('http://fake', raw_data={'height': 'coucou'})
        serializer.is_valid()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'height': 'coucou'})
        self.assertEqual(serializer.errors, ['Bad height'])

        serializer = ScreenshotSerializer('http://fake', raw_data={'wait_until': ['OK']})
        serializer.is_valid()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'wait_until': ['OK']})
        self.assertEqual(serializer.errors, ['Bad wait_until value'])

        serializer = ScreenshotSerializer('http://fake', raw_data={'credentials': {'username': 'test'}})
        serializer.is_valid()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'credentials': {'username': 'test'}})
        self.assertEqual(serializer.errors, ['Bad credentials: a password must be specified'])

        serializer = ScreenshotSerializer('http://fake', raw_data={'credentials': {'password': 'test'}})
        serializer.is_valid()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'credentials': {'password': 'test'}})
        self.assertEqual(serializer.errors, ['Bad credentials: a username must be specified'])

        serializer = ScreenshotSerializer('http://fake', raw_data={'credentials': {'token': 'test'}})
        serializer.is_valid()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {'credentials': {'token': 'test'}})
        self.assertEqual(serializer.errors, ['Bad credentials: "token_in_header" must be specified'])

        serializer = ScreenshotSerializer('http://fake', raw_data={})
        serializer.is_valid()
        self.assertEqual(serializer.url, 'http://fake')
        self.assertEqual(serializer.data, {})
        self.assertEqual(serializer.errors, [])
        self.assertTrue(serializer.valid)

    @mock.patch('src.serializers.generate_bytes_img_django_wrap')
    def test_get_object(self, mock_generate_bytes_img_wrap):
        mock_generate_bytes_img_wrap.side_effect = lambda a: a

        serializer = ScreenshotSerializer('http://fake')
        serializer.get_object()
        self.assertEqual(serializer.bytes_img, 'http://fake')

        serializer = ScreenshotSerializer('http://fake')
        serializer.valid = True
        serializer.get_object()
        self.assertEqual(serializer.bytes_img, 'http://fake')

        serializer = ScreenshotSerializer('http://fake')
        serializer.get_object()
        self.assertEqual(serializer.bytes_img, 'http://fake')

    @mock.patch('src.serializers.BytesIO')
    @mock.patch('src.serializers.image_opener')
    @mock.patch('src.serializers.send_file')
    def test_generic_serializer(self, send_file_mock, image_opener_mock, BytesIO_mock):
        class Image():
            def save(self, path):
                return path
        class TempFile():
            def __init__(self, name):
                self.name = name
        def send_file(path, attachment_filename=None):
            return path, attachment_filename
        send_file_mock.side_effect = send_file
        image_opener_mock.side_effect = lambda a: Image()
        BytesIO_mock = lambda a: a
        serializer = ScreenshotSerializer('http://fake')
        temp_f = TempFile('temp file')
        path, attachment_filename = serializer._generic_serializer(temp_f, 'bytes obj')
        self.assertEqual(path, 'temp file')
        self.assertEqual(attachment_filename, 'screenshot.png')

    @mock.patch('src.serializers.jsonify')
    @mock.patch('src.serializers.ScreenshotSerializer.get_object')
    @mock.patch('src.serializers.ScreenshotSerializer._generic_serializer')
    def test_serialize(self, generic_serializer_mock, get_object_mock, jsonify_mock):
        generic_serializer_mock.side_effect = lambda a, b: (a, b)
        get_object_mock.side_effect = None
        jsonify_mock.side_effect = lambda a: a

        serializer = ScreenshotSerializer('http://fake')
        temp_file, bytes_obj = serializer.serialize(bytes_obj='Bytes obj')
        self.assertIsInstance(temp_file, _TemporaryFileWrapper)
        self.assertTrue(bytes_obj, 'Bytes obj')

        serializer = ScreenshotSerializer('http://fake')
        serializer.bytes_img = 'Bytes obj'
        temp_file, bytes_obj = serializer.serialize()
        self.assertIsInstance(temp_file, _TemporaryFileWrapper)
        self.assertTrue(bytes_obj, 'Bytes obj')

        serializer = ScreenshotSerializer('http://fake')
        response, code = serializer.serialize()
        self.assertEqual(code, 400)
        self.assertEqual(response, {'errors': []})
