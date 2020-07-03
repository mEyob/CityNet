#!/usr/bin/env python
"""
--monitor.py--
A module for collecting summary statistics and 
outliers for a given sensor device.
"""

import sys
import os
import argparse
import psycopg2
import multiprocessing
import numpy as np
from datetime import datetime
from tabulate import tabulate

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

# citynet imports
from citynet.consumer import Consumer
from citynet.utils import to_timestamp
from citynet.constants import DEFAULT_CONSUMER_CONFIG, DEFAULT_MONITORING_PERIOD, CONNECTION


class Monitor(Consumer):
    def __init__(self, topic, group_id, config):
        Consumer.__init__(self, topic, group_id, config=config)

    def ingest_records(self, duration, data_list):
        """
        A method for fetching sensor reading records for a given duration.
        :param duration: time period of interest
        """
        start = None
        ts_format = "%Y-%m-%dT%H:%M:%S"
        start = datetime.utcnow().timestamp()

        for message in self._consumer:
            preprocessed_data = self.preprocess(message.value)
            data_list.extend(preprocessed_data)

    def from_db(self, duration, sensor_name=None):
        """
        Fetch sensor data from database.
        """

        if sensor_name:
            query = """SELECT sensor_path, value 
            FROM aot.observations 
            WHERE ts > NOW() - INTERVAL '{} second' AND
            sensor_path = '{}'
            """.format(duration, sensor_name)
        else:
            query = """SELECT sensor_path, value 
            FROM aot.observations 
            WHERE ts > NOW() - INTERVAL '{} second'
            """.format(duration)

        connection = None
        rows = None

        try:
            connection = psycopg2.connect(**CONNECTION)
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        except psycopg2.DatabaseError as e:
            print(e)
            sys.exit(1)
        finally:
            if connection:
                connection.close()

        if rows:
            self.make_dict(rows)

        return self.make_dict(rows)

    def make_dict(self, data):

        data_dict = {}
        for tupl in data:
            if tupl[0] in data_dict:
                data_dict[tupl[0]].append(tupl[1])
            else:
                data_dict[tupl[0]] = [tupl[1]]
        return data_dict

    def collect_stats(self, duration, source="historical"):
        """
        A method for monitoring sensor readings.
        :param duration: length of monitoring time
        """
        data = {}
        stat = {}
        outliers = []
        stats_list = []
        num_of_observations = 0
        max_execution_time = 1.05 * duration

        if source == "live":
            data_list = multiprocessing.Manager().list()
            control_process = multiprocessing.Process(
                target=self.ingest_records, args=(duration, data_list))
            control_process.start()
            control_process.join(timeout=max_execution_time)

            data = [(entry[0], entry[2]) for entry in data_list]
            data = self.make_dict(data)
            control_process.terminate()
            if self._consumer:
                self._consumer.close()

        elif source == "historical":
            data = self.from_db(duration)

        if data:
            for sensor_name in data.keys():
                num_of_observations = len(data[sensor_name])
                stat = self.stats(data[sensor_name])
                outliers = self.outlier(data[sensor_name])
                stats_list.append({
                    "sensor_name": sensor_name,
                    "num_of_observations": num_of_observations,
                    "mean": stat["mean"],
                    "standard_dev": stat["std"],
                    "IQR": stat["iqr"],
                    "outlier_count": len(outliers)
                })

        # stats_list.sort(reverse=True, key = lambda x: x["outlier_count"])
        time = datetime.utcnow()
        time_str = time.strftime("%Y-%m-%dT%H:%M:%S")
        return {
            "Current time": time_str,
            "Monitoring duration": str(duration) + ' seconds',
            "stats": stats_list
        }

    @staticmethod
    def display(data):
        """
        Display key statistics in table format
        """
        print("\n**** SUMMARY TABLE ****")
        stat_table = [[key, value] for key, value in data.items()]

        print(tabulate(stat_table, tablefmt="grid"))

    @staticmethod
    def stats(data):
        """
        Collect mean, standard deviation and percentile statistics. 
        """

        q75, q25 = np.percentile(data, [75, 25])
        return {
            "mean": round(np.mean(data), 2),
            "std": round(np.std(data), 2),
            "iqr": round(q75 - q25, 2)
        }

    @staticmethod
    def outlier(data, cutoff=3):
        """
        Outlier detecting function.
        :param data: array-like data points
        :cutoff: determines how far (relative to the mean) datapoints should 
        be to be labeled outlier
        """
        mean = np.mean(data)
        std = np.std(data)
        tail_cases = lambda x: x > mean + cutoff * std or x < mean - cutoff * std
        outliers = list(filter(tail_cases, data))
        return outliers

    @staticmethod
    def get_location(sensor_path):
        """
        Get the location(s) of a sensor
        """
        query = """SELECT long, lat
        FROM aot.nodes
        WHERE vsn IN (
            SELECT node_vsn
            FROM aot.observations
            WHERE ts > NOW() - INTERVAL '24 hours'
            AND sensor_path = '{}'
        )
        LIMIT 1
        """.format(sensor_path)
        rows = None

        try:
            connection = psycopg2.connect(**CONNECTION)
            cursor = connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
        except psycopg2.DatabaseError as e:
            print(e)
            sys.exit(1)
        finally:
            if connection:
                connection.close()
        return rows


if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--topic", help="A Kafka topic")
    parser.add_argument("-g", "--cgroup", help="Kafka consumer group")
    parser.add_argument("-p",
                        "--period",
                        help="Monitoring period in seconds",
                        type=int)
    parser.add_argument("-c",
                        "--conf",
                        default=DEFAULT_CONSUMER_CONFIG,
                        help="Kafka consumer configuration in JSON format")

    args = parser.parse_args()
    detector = Monitor(args.topic, args.cgroup, args.conf)
    data = detector.collect_stats(args.period, "live")
    if data:
        detector.display(data)
