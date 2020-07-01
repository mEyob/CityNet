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
    def __init__(self, topic, group_id, config):
        Consumer.__init__(self, topic, group_id, config=config)
        self.data_dict = {}

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
                    sensor_name = record.get("sensor_path")
                    if sensor_name in self.data_dict:
                        self.data_dict[sensor_name].append(record.get("value"))
                    else:
                        self.data_dict[sensor_name] = [record.get("value")]
                else:
                    if self._consumer:
                        self._consumer.close()

    def from_db(self, duration):
        """
        Fetch sensor data from database.
        """
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
        outliers = None
        stats_list = []
        num_of_observations = 0
        max_execution_time = 2 * duration

        if source == "live":

            control_process = Process(target=self.ingest_records,
                                      args=(duration, ))
            control_process.start()
            control_process.join(timeout=max_execution_time)
            control_process.terminate()
            if self._consumer:
                self._consumer.close()

            data = self.data_dict

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
    data = detector.collect_stats(args.period, "historical")
    if data:
        detector.display(data)
