"""
--utils.py--
Utility functions for APIClient and Producer classes
"""

from datetime import datetime
import json
import itertools


def write_json(start_time, json_obj, page):
    """
    Write a json object to file.
    """
    with open('{}_page_{}.json'.format(start_time, page), 'w') as fhandle:
        json.dump(json_obj, fhandle)


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


def flatten_reverse(nested_record):
    """
    Flatten and reverse a nested list.
    """
    return list(itertools.chain.from_iterable(nested_record))[::-1]
