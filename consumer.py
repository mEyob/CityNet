"""
--consumer.py--
A Kafka consumer that reads Kafka topics (observations,
nodes, or sensors) and sends new messages to the 
database connector.
"""
from kafka import KafkaConsumer
from db_connect import insert_in_db
import argparse
import json
import time
import os

DEFAULT_CONSUMER_CONFIG = {
    "bootstrap_servers": ['10.0.1.16:9092'],
    "value_deserializer": lambda val: json.loads(val.decode('utf-8'))
}

# Max number of records in a batch insertion
DEFAULT_DB_PAGE_SIZE = 100


class Consumer():
    def __init__(self, topic, group_id, config):
        """
        A Kafka consumer.
        :param topic: a topic the consumer subscribes to
        :param group_id: consumer group identifier
        :param config: a dict of kafka consumer config params
        """
        self.topic = topic
        self.group_id = group_id
        self.config = config
        self.connect_kafka()

    def connect_kafka(self):
        """
        Make a Kafka connection as a consumer.
        """
        try:
            self._consumer = KafkaConsumer(self.topic,
                                           group_id=self.group_id,
                                           auto_offset_reset='earliest',
                                           consumer_timeout_ms=10000,
                                           **self.config)
        except Exception as ex:
            print("Exception encountered while trying to connect to Kafka")
            print(str(ex))

    def write_to_db(self, db_pagesize):
        """
        Iteratively write kafka messages into DB.
        :param db_pagesize: Max number of records in a batch insertion
        """
        try:
            for message in self._consumer:
                preprocessed = self.preprocess(message.value)
                if preprocessed:
                    insert_in_db(self.topic, preprocessed, len(message.value),
                                 db_pagesize)
        except Exception as ex:
            print("Exception encountered while trying to read messages")
            print(str(ex))
        finally:
            if self._consumer:
                self._consumer.close()

    def preprocess(self, data):
        """
        Type conversion and discarding records with missing timestamps.
        :param data: a dict of records
        """
        cast = lambda callable, value: callable(value) if value else None
        lat_long = lambda coord: (cast(float, coord[0]), cast(float, coord[1]))

        processed = None

        try:
            if self.topic == "sensors":
                processed = ((row["path"], row["uom"], cast(int, row["min"]),
                              cast(int, row["max"]), row["data_sheet"])
                             for row in data)
            elif self.topic == "observations":
                none_val_removed = filter(
                    lambda row: (row["timestamp"] is not None) and
                    (cast(float, row["value"])), data)
                processed = ((row["sensor_path"], row["timestamp"],
                              cast(float, row["value"]), row["node_vsn"])
                             for row in none_val_removed)
            elif self.topic == "nodes":
                processed = ((row["vsn"], *lat_long(
                    row["location"]["geometry"]["coordinates"]))
                             for row in data if row["address"] != "TBD")
        except Exception as ex:
            print(str(ex))
        return processed


if __name__ == "__main__":

    # Command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--topic", help="A Kafka topic")
    parser.add_argument("-g", "--cgroup", help="Kafka consumer group")
    parser.add_argument(
        "-s",
        "--dbpagesize",
        default=DEFAULT_DB_PAGE_SIZE,
        help="Number of records to be written into database in one batch")
    parser.add_argument("-c",
                        "--conf",
                        default=DEFAULT_CONSUMER_CONFIG,
                        help="Kafka consumer configuration in JSON format")

    args = parser.parse_args()
    consumer = Consumer(args.topic, args.cgroup, args.conf)
    consumer.write_to_db(int(args.dbpagesize))
