"""
Contains all the serializers.
"""
from tempfile import NamedTemporaryFile
from io import BytesIO

from flask import jsonify, send_file

from pyppeteer.errors import NetworkError

from PIL.Image import open as image_opener

from screamshot import generate_bytes_img_django_wrap


AUTHORIZED_WAIT_UNTIL_VALUE = [
    'load', 'domcontentloaded', 'networkidle0', 'networkidle2']
SCREAMSHOT_PARAMETERS = ['url', 'width', 'height',
                         'wait_until', 'credentials', 'selector', 'wait_for']


class ScreenshotSerializer():
    """
    Serializer linked to screenshot.

    :attributes:
    * raw_data (**dict**): the data given to initialize the serializer
    * data (**dict**): the parse and validated data
    * errors (**list**): all the errors
    * bytes_img (**bytes**): the screenshot

    .. warning:: ``data = dict()`` before calling ``is_valid``
    .. warning:: ``bytes_img = None`` before calling ``get_object``
    """
    def __init__(self, raw_data):
        # Public attributes
        self.raw_data = raw_data
        self.data = dict()
        self.errors = []
        self.bytes_img = None

        # Private attributes
        self._is_valid_accessed = False
        self._valid = False
        self._get_object_accessed = False

    def _parse_raw_data(self):
        for key, val in self.raw_data.items():
            if key in SCREAMSHOT_PARAMETERS:
                if key == 'url':
                    self.data[key] = val
                else:
                    self.data['opt_param'][key] = val
            else:
                self.errors.append('Unknown parameter: "{0}"'.format(key))

    def _validate_url(self):
        if 'url' not in self.data:
            self.errors.append('No url')

    def _validate_window_sizes(self):
        str_width = self.data.get('width')
        if str_width:
            try:
                self.data['opt_param']['width'] = int(str_width)
            except ValueError as _:
                self.errors.append('Bad width')

        str_height = self.raw_data.get('height')
        if str_height:
            try:
                self.data['opt_param']['height'] = int(str_height)
            except ValueError as _:
                self.errors.append('Bad height')

    def _validate_wait_until(self):
        wait_until = self.data.get('wait_until')
        if wait_until:
            valid_wait_until = all(
                [e in AUTHORIZED_WAIT_UNTIL_VALUE for e in wait_until])
            if not valid_wait_until:
                self.errors.append('Bad wait_until value')

    def _validate_credentials(self):
        credentials = self.data.get('credentials')
        if credentials:
            if 'username' in credentials and 'password' not in credentials:
                self.errors.append(
                    'Bad credentials: a password must be specified')
            elif 'password' in credentials and 'username' not in credentials:
                self.errors.append(
                    'Bad credentials: a username must be specified')
            elif ('username' not in credentials and 'password' not in credentials
                  and 'token_in_header' not in credentials):
                self.errors.append(
                    'Bad credentials: "token_in_header" must be specified')

    def is_valid(self):
        """
        This class method parses the data and checks wether the given parameters are valid.

        :return: ``True`` if there is no error and ``False`` otherwise

        .. info:: After calling this method, the parsed and validated data can be retrieved or \
            defined in the ``data`` dict attribute
        .. info:: The ``data`` attribute has the following structure: \
            ``{'url': ..., 'opt_param': {...}}``
        """
        self._parse_raw_data()
        self._validate_url()
        self._validate_window_sizes()
        self._validate_credentials()
        self._validate_wait_until()
        self._is_valid_accessed = True
        if not self.errors:
            self._valid = True
        return self._valid

    def get_object(self):
        """
        This class method calls ``generate_bytes_img_django_wrap`` function

        :return: an image in the ``bytes`` object format if ``data`` is valid and ``None`` otherwise

        .. info:: If ``is_valid`` was not called, it will call it first
        .. info:: The image is saved in the ``bytes_img`` attribute
        """
        if not self._is_valid_accessed:
            self.is_valid()
        if self._valid:
            url = self.data['url']
            opt_param = self.data.get('opt_param', {})
            try:
                self.bytes_img = generate_bytes_img_django_wrap(url, **opt_param)
            except NetworkError as exc:
                self.errors.append(exc.args)
        self._get_object_accessed = True
        return None

    @staticmethod
    def _generic_serializer(temp_file, bytes_obj):
        img_buf = BytesIO(bytes_obj)
        img = image_opener(img_buf)
        img.save(temp_file)
        return send_file(temp_file.name, attachment_filename='screenshot.png')

    def serialize(self, bytes_obj=None):
        """
        This class method creates a ``Response`` object

        :param bytes_obj: optional, the image to send
        :type bytes_obj: bytes

        :return: a png image with 200 status code if there is no errors or a json with a 400 \
            status code otherwise

        .. info:: If there are any errors, the JSON has the following structure: \
            ``{'errors': [...]}``
        .. info:: If ``get_object`` was not called, it will call it first \
            (if no ``bytes_object`` was given)
        """
        temp_file = NamedTemporaryFile(suffix='.png')
        if bytes_obj:
            return self._generic_serializer(temp_file, bytes_obj)
        if not self._get_object_accessed:
            self.get_object()
        if self.bytes_img:
            return self._generic_serializer(temp_file, self.bytes_img)
        return jsonify({'errors': self.errors}), 400
