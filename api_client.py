"""
--api_client.py--
Module for making api requests and placing them in 
a Kafka broker

"""
import time
import requests
import json
import subprocess

BASE_URL = "https://api-of-things.plenar.io/api/"

class APIClient():
    def __init__(self, project, endpoint):
        """Class for fetching sensor and measurement data 
        from API servers at Array of Things.
        :param endpoint: Could be 'observations' or 'sensors'
        """
        self.endpoint = endpoint
        self.project = project
        self.url = BASE_URL + endpoint 
    
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
        filter_str = "?project={}&order=desc%3Atimestamp&size={}&page={}".format(
            self.project, 
            size, 
            page
        )
        return filter_str

    @staticmethod
    def is_valid(response):
        """
        Validate an http request response. Checks the status code 
        and the length of the 'data' field to determine validity.
        :param response: a response object to be validated
        """
        valid = False
        if response.status_code == 200 and len(response.json()["data"]) != 0:
            valid = True
        return valid

        
if __name__ == "__main__":
    api = APIClient("chicago", "observations")
    start_time = int(time.time() - 300)
    page = 1

    response = api.fetch(5, page)
    print(response.json())