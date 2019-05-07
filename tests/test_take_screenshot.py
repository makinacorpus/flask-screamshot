from os import remove
from unittest import TestCase

from PIL import Image

import numpy as np

from requests import get, post

from screamshot import bytes_to_file


def _rmsd(img1, img2):
    img1 = (img1 - np.mean(img1)) / (np.std(img1))
    img2 = (img2 - np.mean(img2)) / (np.std(img2))
    return np.sqrt(np.mean((img1 - img2) ** 2))


# Usefull for basic tests
def _is_same_image(img1, img2):
    return (img1.size == img2.size) and (abs(_rmsd(img1, img2)) < 0.05)


class TestTakeScreenshot(TestCase):
    def test_simple_get_take_screenshot_request(self):
        request = get('http://127.0.0.1:8000/api/take-screenshot',
                      params={'url': 'http://127.0.0.1:5000/index'})
        self.assertEqual(request.status_code, 200)
        self.assertIsInstance(request.content, bytes)

        bytes_to_file(request.content,
                      'test_simple_get_take_screenshot_request.png')
        screenshot_img = Image.open(
            'test_simple_get_take_screenshot_request.png')
        img = Image.open('tests/server/static/images/600_800_index_page.png')
        self.assertTrue(_is_same_image(screenshot_img, img))
        remove('test_simple_get_take_screenshot_request.png')

    def test_simple_post_take_screenshot_request(self):
        request = post('http://127.0.0.1:8000/api/take-screenshot',
                       params={'url': 'http://127.0.0.1:5000/index'},
                       data={'selector': '#godot'})
        self.assertEqual(request.status_code, 200)
        self.assertIsInstance(request.content, bytes)

        bytes_to_file(request.content,
                      'test_simple_post_take_screenshot_request.png')
        screenshot_img = Image.open(
            'test_simple_post_take_screenshot_request.png')
        img = Image.open(
            'tests/server/static/images/aww_dog.jpg').convert('RGBA')
        self.assertTrue(_is_same_image(screenshot_img, img))
        remove('test_simple_post_take_screenshot_request.png')
