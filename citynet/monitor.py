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
from multiprocessing import Process
import numpy as np
from datetime import datetime
from tabulate import tabulate

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

# citynet imports
from citynet.consumer import Consumer
from citynet.utils import to_timestamp
from citynet.constants import DEFAULT_CONSUMER_CONFIG, DEFAULT_MONITORING_PERIOD, CONNECTION


class Monitor(Consumer):
    def __init__(self, topic, group_id, config, device):
        Consumer.__init__(self, topic, group_id, config=config)
        self.device_name = device.lower()
        self.records = []

    def ingest_records(self, duration):
        """
        A method for fetching sensor reading records for a given duration.
        :param duration: time period of interest
        """
        start = None
        ts_format = "%Y-%m-%dT%H:%M:%S"
        start = datetime.utcnow().timestamp()

        for message in self._consumer:
            for record in message.value:
                latest = to_timestamp(record.get("timestamp"), ts_format)
                if latest < start:
                    continue
                if latest - start < duration:
                    if record.get("sensor_path").lower() == self.device_name:
                        self.records.append(record)
                else:
                    if self._consumer:
                        self._consumer.close()

    def from_db(self, duration):
        """
        Fetch sensor data from database.
        """
        query = """SELECT value 
        FROM aot.observations 
        WHERE sensor_path = '{}' AND
        ts > NOW() - INTERVAL '{} second'
        """.format(self.device_name, duration)

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
            rows = [entry[0] for entry in rows]
        return rows

    def collect_stats(self, duration, source=None):
        """
        A method for monitoring sensor readings.
        :param duration: length of monitoring time
        """
        data = {}
        stat = {}
        outliers = None
        num_of_observations = 0
        max_execution_time = 2 * duration

        if source is None or source == "live":

            control_process = Process(target=self.ingest_records,
                                      args=(duration, ))
            control_process.start()
            control_process.join(timeout=max_execution_time)
            control_process.terminate()
            if self._consumer:
                self._consumer.close()

            data = self.records
            if data:
                data = list(map(lambda x: float(x.get("value")), data))
        elif source == "historical":
            data = self.from_db(duration)

        if data:
            num_of_observations = len(data)
            stat = self.stats(data)
            outliers = self.outlier(data)

        time = datetime.now()
        time_str = time.strftime("%Y-%m-%dT%H:%M:%S")
        return {
            "Device:": self.device_name,
            "Current time:": time_str,
            "Monitoring duration:": str(duration) + ' seconds',
            "Num. of observations:": num_of_observations,
            "Mean:": stat.get("mean", "No data"),
            "Standard dev:": stat.get("std", "No data"),
            "Percentiles:": stat.get("percentiles", ["No data"] * 4),
            "Outliers:": outliers
        }

    @staticmethod
    def display(data):
        """
        Display key statistics in table format
        """
        print("\n**** SUMMARY TABLE ****")
        stat_table = [["Device", data.get("Device:")],
                      ["Current time",
                       data.get("Current time:")],
                      [
                          "Monitoring duration",
                          data.get("Monitoring duration:")
                      ], ["Num of observ.",
                          data.get("Num. of observations:")],
                      ["Mean", data.get("Mean:")],
                      ["STD", data.get("Standard dev:")],
                      ["25th", data.get("Percentiles:")[0]],
                      ["50th", data.get("Percentiles:")[1]],
                      ["75th", data.get("Percentiles:")[2]],
                      ["95th", data.get("Percentiles:")[3]]]

        print(tabulate(stat_table, tablefmt="grid"))

        outliers = data.get("outliers")
        if outliers:
            outliers = [[entry] for entry in outliers]
            print(tabulate(outliers, ["Outliers"], tablefmt="grid"))
        else:
            print("\n**** NO OUTLIERS DETECTED FOR DEVICE {}! ****\n".format(
                data.get("Device:")))

    @staticmethod
    def stats(data):
        """
        Collect mean, standard deviation and percentile statistics. 
        """
        return {
            "mean": np.mean(data),
            "std": np.std(data),
            "percentiles": np.percentile(data, [25, 50, 75, 95])
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


if __name__ == "__main__":
    # Command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--topic", help="A Kafka topic")
    parser.add_argument("-g", "--cgroup", help="Kafka consumer group")
    parser.add_argument("-d", "--device", help="sensor device to be monitored")
    parser.add_argument("-p",
                        "--period",
                        help="Monitoring period in seconds",
                        type=int)
    parser.add_argument("-c",
                        "--conf",
                        default=DEFAULT_CONSUMER_CONFIG,
                        help="Kafka consumer configuration in JSON format")

    args = parser.parse_args()
    detector = Monitor(args.topic, args.cgroup, args.conf, args.device)
    data = detector.collect_stats(args.period)
    if data:
        detector.display(data)
