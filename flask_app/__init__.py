from citynet import monitor
from citynet import constants
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_googlemaps import GoogleMaps

device_monitor = monitor.Monitor("observations", "detect",
                                 constants.DEFAULT_CONSUMER_CONFIG)
app = Flask(__name__)
bootstrap = Bootstrap(app)
GoogleMaps(app, key=constants.GOOGLE_API_KEY)

from flask_app import route
