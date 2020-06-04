"""
--producer.py--
A kafka producer that fetches 5 minutes worth sensor measurements (or data 
related to another end point) and puts it in kafka
"""

from api_client import APIClient
from datetime import datetime
import json


class Producer():
    def __init__(self, project, endpoint, interval):
        """
        Create an API client for a specific project and endpoint
        """
        self.http_client = APIClient(project, endpoint)
        self.interval = interval
        self.start_time = None

    def fetch_records(self, size):
        """
        Fetches sensor measurements for 'self.interval' time units.
        :param size: number of records to be fetched in one page
        """
        page = 1
        response = self.http_client.fetch(size, page)
        if self.http_client.is_valid(response):
            self.start_time = response.json()["data"][0]["timestamp"]
            self.start_time = self.to_timestamp(self.start_time,
                                                "%Y-%m-%dT%H:%M:%S")

        while self.http_client.is_valid(response) and self.is_in_interval(
                response):
            print(response.status_code)
            self.write_json(response.json(), page)
            page += 1
            response = self.http_client.fetch(size, page)
        print(response.status_code)

    def is_in_interval(self, response):
        """
        Checks if the first record in responses.json()
        """
        if self.start_time is None:
            raise TypeError("start_time cannot be of None type")

        in_interval = False

        latest_record_time = response.json()["data"][0]["timestamp"]
        latest_record_time = self.to_timestamp(latest_record_time,
                                               "%Y-%m-%dT%H:%M:%S")

        if self.start_time - latest_record_time < self.interval:
            in_interval = True

        return in_interval

    def write_json(self, json_obj, page):
        """
        Write a json object to file.
        """
        with open('{}_page_{}.json'.format(self.start_time, page),
                  'w') as fhandle:
            json.dump(json_obj, fhandle)

    @staticmethod
    def to_timestamp(t, t_format=None):
        """
        Converts time from datetime object or a string to time stamp.
        :param t: time reading to be converted into timestamp. Type should be datetime or str
        :param t_format: optional for str type time format
        """
        if isinstance(t, datetime):
            return t.timestamp()
        elif isinstance(t, str):
            return datetime.strptime(t, t_format).timestamp()


if __name__ == "__main__":
    producer = Producer('chicago', 'observations', 300)
    producer.fetch_records(300)
