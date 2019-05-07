# Flask screamshot server

It is an API that provides access to screen capture functions through an SSL Web connection.

# How to run the server

Gunicorn, a Python WSGI HTTP Server for Unix is recommended

```
>>> gunicorn src:app
```

# Usage

The documentation is accessible here.

## Exemple:

```
>>> from requests import post
>>> req = post('http://127.0.0.1:5000/api/take-screenshot', data={'url': 'https://makina-corpus.com/'})
>>> req
<Response [200]>
>>> from io import BytesIO
>>> buf = BytesIO(req.content)
>>> from PIL import Image
>>> img = Image.open(buf)
>>> img.save('path/nom.png')
```

# How to run the tests

## The first time

1. Launch the web server:
```
>>> pip3 install -r requirements
>>> pip3 install -r dev-requirements
>>> cd tests/server
>>> flask run
```
2. Launch the screamshot server:
```
>>> pip3 install gunicorn
>>> gunicorn src:app
```
3. Launch the tests:
```
>>> pytest --cov=src --cov-report=term-missing -v
```
4. Launch pylint checks:
```
>>> pylint ./src
```

## When it is already setup

1. Launch the web server:
```
>>> cd tests/server
>>> flask run
```
2. Launch the screamshot server:
```
>>> gunicorn src:app
```
3. Launch the tests:
```
>>> pytest --cov=src --cov-report=term-missing -v
```
4. Launch pylint checks:
```
>>> pylint ./src
```
