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
        self.start_time = datetime.utcnow().timestamp()
        response = self.http_client.fetch(size, page)

        while self.http_client.is_valid(response) and self.is_in_interval(response):
            print(response.status_code)
            with open('page_{}.json'.format(page), 'w') as fhandle:
                json.dump(response.json(), fhandle)
            page += 1
            response = self.http_client.fetch(size, page)
    
    def is_in_interval(self, response):
        """
        Checks if the first record in responses.json()
        """
        if self.start_time is not None:
            raise TypeError("start_time cannot be of None type")

        in_interval = False

        latest_record_time = response.json()["data"][0]["timestamp"]
        latest_record_time = datetime.strptime(latest_record_time, "%Y-%m-%dT%H:%M:%S")
        latest_record_time = latest_record_time.timestamp()

        if self.start_time - latest_record_time < self.interval:
            in_interval = True

        return in_interval

if __name__ == "__main__":
    producer = Producer('chicago', 'observations', 300)
    producer.fetch_records(300)


    