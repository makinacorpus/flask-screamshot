"""
Contains all the views.
"""
from flask import request

from .serializers import ScreenshotSerializer


def take_screenshot_view():
    """
    Takes a screenshot of a web page and returns a png image with a 200 status code if there \
        is no errors or a json with a 400 status code otherwise.

    :param url: mandatory, the website's url
    :type url: str

    :param path: optional, the path to the image output
    :type path: str

    :param width: optionnal, the window's width
    :type width: int

    :param height: optionnal, the window's height
    :type height: int

    :param selector: optionnal, CSS3 selector, item whose screenshot is taken
    :type selector: str

    :param wait_for: optionnal, CSS3 selector, item to wait before taking the screenshot
    :type wait_for: str

    :param wait_until: optionnal, define how long you wait for the page to be loaded should \
        be either load, domcontentloaded, networkidle0 or networkidle2
    :type wait_until: str or list(str)
    """
    data = request.form.to_dict()
    serializer = ScreenshotSerializer(data)
    return serializer.serialize()
