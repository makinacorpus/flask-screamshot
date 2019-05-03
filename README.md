# Flask screamshot server

It is an API that provides access to screen capture functions through an SSL Web connection.

# How to run the server

## Development

### The first time

```
>>> chmod +x ./run.py
>>> ./run.py
```

### When it is already setup

```
>>> ./run.py
```

## Deployment

The Python WSGI HTTP Server for Unix is recommended

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
