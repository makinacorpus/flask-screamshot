"""
Contains all the serializers.
"""
from sys import exc_info
from tempfile import NamedTemporaryFile
from io import BytesIO

from flask import jsonify, send_file

from PIL.Image import open as image_opener

from screamshot import generate_bytes_img_wrap
from screamshot.errors import BadUrl, BadSelector


AUTHORIZED_WAIT_UNTIL_VALUE = [
    'load', 'domcontentloaded', 'networkidle0', 'networkidle2']
SCREAMSHOT_PARAMETERS = ['width', 'height',
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
    def __init__(self, url, raw_data=None):
        # Public attributes
        self.url = url
        self.raw_data = raw_data if raw_data else {}
        self.data = dict()
        self.errors = []
        self.bytes_img = None
        self.valid = None

    def _parse_raw_data(self):
        for key, val in self.raw_data.items():
            if key in SCREAMSHOT_PARAMETERS:
                self.data[key] = val
            else:
                self.errors.append('Unknown parameter: "{0}"'.format(key))

    def _validate_window_sizes(self):
        str_width = self.data.get('width')
        if str_width:
            try:
                self.data['width'] = int(str_width)
            except ValueError as _:
                self.errors.append('Bad width')

        str_height = self.raw_data.get('height')
        if str_height:
            try:
                self.data['height'] = int(str_height)
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
        self._validate_window_sizes()
        self._validate_credentials()
        self._validate_wait_until()
        if self.errors:
            self.valid = False
        else:
            self.valid = True
        return self.valid

    def get_object(self):
        """
        This class method calls ``generate_bytes_img_wrap`` function

        :return: an image in the ``bytes`` object format if ``data`` is valid and ``None`` otherwise

        .. info:: If ``is_valid`` was not called, it will call it first
        .. info:: The image is saved in the ``bytes_img`` attribute
        """
        if not self.valid:
            self.is_valid()
        if self.valid:
            try:
                self.bytes_img = generate_bytes_img_wrap(self.url, **self.data)
            except (BadUrl, BadSelector) as exc:
                _, ex_value, _ = exc_info()
                self.errors.append(str(ex_value))
        return self.bytes_img

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
        self.get_object()
        if self.bytes_img:
            return self._generic_serializer(temp_file, self.bytes_img)
        return jsonify({'errors': self.errors}), 400
