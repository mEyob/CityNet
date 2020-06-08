"""
--producer.py--
A kafka producer that fetches 5 minutes worth sensor measurements (or data 
related to another end point) and puts it in kafka
"""

from api_client import APIClient
from kafka import KafkaProducer
import json

# Number of records in one page of a multi-page api call,
PAGE_SIZE = 200

DEFAULT_PRODUCER_CONFIG = {
    "bootstrap_servers": ['10.0.1.16:9092'],
    "value_serializer": lambda val: json.dumps(val).encode('utf-8')
}


class Producer():
    def __init__(self,
                 topic,
                 project,
                 endpoint,
                 interval,
                 config,
                 page_size=PAGE_SIZE):
        """
        A wrapper class to a Kafka producer. 
        Creates an API client for a specific project and endpoint
        as the source of data and initializes a producer to 
        channel the fetched data into the system.
        :param topic: a Kafka topic
        :param project: the project name to be passed to the APIClient class
        :param endpoint: API endpoint to be passed to APIClient. Possible 
        values: ['projects', 'nodes', 'sensors', 'observations']. See 
        https://arrayofthings.docs.apiary.io/#reference/0/nodes/list-projects
        :param interval: the length of time (in seconds) covered in the api call
        :param config: a dictionary of kafka producer configuration
        :param page_size: number of records in a single page of api call
        """
        self.topic = topic
        self.api = APIClient(project, endpoint, interval)
        self.config = config
        self.page_size = page_size

        self.producer = None

    def fetch_data(self):
        """
        Fetch sensor data in json format using an API client
        """
        records = None
        try:
            records = self.api.fetch_records(self.page_size)
        except Exception as ex:
            print("Exception encountered while trying to fetch records")
            print(str(ex))
        return records

    def connect_kafka(self):
        """
        Make a Kafka connection as a producer.
        """
        try:
            self.producer = KafkaProducer(**self.config)
        except Exception as ex:
            print("Exception encountered while trying to connect to Kafka")
            print(str(ex))

    def publish(self, record):
        """
        Publish messages to a kafka topic
        """
        try:
            self.producer.send(self.topic, value=record)
            self.producer.flush()
        except Exception as ex:
            print("Exception encountered while publishing message")
            print(str(ex))

    def publish_records(self):
        """
        Make a kafka connection as a producer and publish a list 
        of records. Each record is a json formatted sensor data.
        """
        records = self.fetch_data()
        self.connect_kafka()

        if (records is not None) and (self.producer is not None):
            for record in records:
                self.publish(record)


if __name__ == "__main__":
    producer = Producer('observations', 'chicago', 'observations', 300,
                        DEFAULT_PRODUCER_CONFIG)
    producer.publish_records()
