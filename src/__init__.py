"""
Initializes the application and the routes.
"""
from flask import Flask

from .views import take_screenshot_view


app = Flask('Screamshot')


# Routes
app.add_url_rule('/api/take-screenshot',
                 'take_screenshot', view_func=take_screenshot_view, methods=['POST'])
