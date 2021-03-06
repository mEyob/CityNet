"""
--producer.py--
A kafka producer that fetches 5 minutes worth sensor measurements (or data 
related to another end point) and puts it in kafka
"""

import os
import sys
import json
import time
import argparse
from kafka import KafkaProducer

# citynet imports
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from citynet.api_client import APIClient
from citynet.simulator import simulate
from citynet.constants import DEFAULT_INTERVAL, DEFAULT_PAGE_SIZE, SIMULATED_BATCH_SIZE, DEFAULT_PRODUCER_CONFIG


class Producer():
    def __init__(self,
                 topic,
                 project,
                 endpoint,
                 interval,
                 page_size=DEFAULT_PAGE_SIZE,
                 config=DEFAULT_PRODUCER_CONFIG):
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
        self.page_size = page_size
        self.config = config

        self.producer = None

    def fetch_data(self, simulated, batch_size):
        """
        Fetch sensor data in json format using an API client
        """
        records = None

        if simulated:
            records = simulate(batch_size)
        else:
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

    def publish(self, records, key=None):
        """
        Publish messages to a kafka topic
        """
        start = time.perf_counter()
        if key:
            self.producer.send(self.topic,
                               key=bytes(key, encoding='utf-8'),
                               value=records)
        else:
            self.producer.send(self.topic, value=records)
        self.producer.flush()
        end = time.perf_counter()
        with open("logs/producer.log", "a") as log:
            log.write("{},{}\n".format(len(records), end - start))

    def publish_records(self, simulated, batch_size):
        """
        Make a kafka connection as a producer and publish a list 
        of records. Each record is a json formatted sensor data.
        """
        while True:
            records = self.fetch_data(simulated, batch_size)
            self.connect_kafka()

            if (records is not None) and (self.producer is not None):
                if self.topic == "observations" and not simulated:
                    keys = set(map(lambda d: d['sensor_path'], records))
                    for key in keys:
                        sensor_specific_records = list(
                            filter(lambda d: d['sensor_path'] == key, records))
                        self.publish(sensor_specific_records, key)
                else:
                    self.publish(records)
            time.sleep(295)


if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--topic", help="A Kafka topic")
    parser.add_argument("-p",
                        "--proj",
                        default="chicago",
                        help="Array of Things project (e.g. chicago)")
    parser.add_argument("-e",
                        "--endpoint",
                        help="API endpoint in Array of Things")
    parser.add_argument("-m",
                        "--sim",
                        help="Simulate datapoints",
                        action='store_true')
    parser.add_argument("-b",
                        "--batch",
                        help="Number of datapoints to be simulated in a batch",
                        default=SIMULATED_BATCH_SIZE,
                        type=int)
    parser.add_argument("-i",
                        "--interval",
                        default=DEFAULT_INTERVAL,
                        help="Time interval of interest")
    parser.add_argument(
        "-s",
        "--pagesize",
        default=DEFAULT_PAGE_SIZE,
        help="Number of records in a single page of paginated response")
    parser.add_argument("-c",
                        "--conf",
                        default=DEFAULT_PRODUCER_CONFIG,
                        help="Kafka producer configuration in JSON format")

    args = parser.parse_args()
    producer = Producer(args.topic, args.proj, args.endpoint, args.interval,
                        args.pagesize, args.conf)
    producer.publish_records(args.sim, args.batch)
