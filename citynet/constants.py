"""
--constants.py--
System-wide constants.
"""
import os
import json

# Default time interval (frequency) of data collection
# Set to every 5 min
DEFAULT_INTERVAL = 300

# Number of records in one page of a multi-page api call,
DEFAULT_PAGE_SIZE = 200

# Number of datapoints to be generaged When sensor readings are simulated
SIMULATED_BATCH_SIZE = 1000

# Default kafka producer config
DEFAULT_PRODUCER_CONFIG = {
    "bootstrap_servers": ['10.0.1.16:9092'],
    "value_serializer": lambda val: json.dumps(val).encode('utf-8')
}

# Default kafka consumer config
DEFAULT_CONSUMER_CONFIG = {
    "bootstrap_servers": ['10.0.1.16:9092'],
    "value_deserializer": lambda val: json.loads(val.decode('utf-8'))
}

CONNECTION = json.loads(os.environ["CONNECTION"])
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

# Base url for array-of-things api call
BASE_URL = "https://api-of-things.plenar.io/api/"

# Max number of records in a batch insertion
DEFAULT_DB_PAGE_SIZE = 1000

# Default monitoring period in seconds (300=5min)
DEFAULT_MONITORING_PERIOD = 300
