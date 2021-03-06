"""
--api_client.py--
Module for making api requests to https://api-of-things.plenar.io/api/
"""

import sys
import os
import json
import requests

# citynet imports
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from citynet.utils import write_json, to_timestamp, is_valid, flatten_reverse
from citynet.nodes import create_node_filter
from citynet.constants import BASE_URL


class APIClient():
    def __init__(self, project, endpoint, interval):
        """Class for fetching sensor and measurement data 
        from API servers at Array of Things.
        :param endpoint: Could be 'observations' or 'sensors'
        """
        self.project = project
        self.endpoint = endpoint
        self.url = BASE_URL + endpoint
        self.interval = interval
        self.start_time = None

    def fetch(self, size=300, page=1):
        """Fetch a 'page' with 'size' records in it where all 
        records should be newer than 'start_time'
        :param size: the number of records to fetch in one API call
        :param page: The page to be fetched
        :param start_time: used to filter out older records
        """
        filter_str = self.filter(size, page)
        response = requests.get(self.url + filter_str)
        return response

    def filter(self, size, page):
        """
        Set the filter for an API call.
        :param size: number of records per page
        :param page: page to be fetched  
        """
        if self.endpoint == "observations":
            filter_str = "?project={}{}order=desc%3Atimestamp&size={}&page={}".format(
                self.project, create_node_filter(), size, page)
        else:
            filter_str = "?size={}&page={}".format(size, page)
        return filter_str

    def fetch_records(self, size, write_to_file=False):
        """
        Fetches sensor measurements for 'self.interval' time units.
        :param size: number of records to be fetched in one page
        """
        page = 1
        responses = []
        response = self.fetch(size, page)

        if self.endpoint == "observations":
            if is_valid(response):
                self.start_time = response.json()["data"][0]["timestamp"]
                self.start_time = to_timestamp(self.start_time,
                                               "%Y-%m-%dT%H:%M:%S")
            while is_valid(response) and self.is_in_interval(response):
                responses.append(response.json()["data"])
                page += 1
                response = self.fetch(size, page)
        else:
            while is_valid(response):
                responses.append(response.json()["data"])
                page += 1
                response = self.fetch(size, page)
        responses = flatten_reverse(responses)
        if write_to_file:
            write_json(self.start_time, responses, page)
        return responses

    def is_in_interval(self, response):
        """
        Checks if the first record in responses.json()
        """
        if self.start_time is None:
            raise TypeError("start_time cannot be of None type")

        in_interval = False

        latest_record_time = response.json()["data"][0]["timestamp"]
        latest_record_time = to_timestamp(latest_record_time,
                                          "%Y-%m-%dT%H:%M:%S")

        if self.start_time - latest_record_time < self.interval:
            in_interval = True

        return in_interval


if __name__ == "__main__":
    # Check module by fetching the latest 5 minutes long
    # sensor 'obervations' for the 'chicago' project
    api = APIClient("chicago", "observations", 300)

    responses = api.fetch_records(200, True)
    print(responses)
