"""
--simulator.py--
Simulate sensor readings.
"""
from datetime import datetime
from math import sin
import random
import json


def simulate(batch_num):
    """
    A function for simulating sensor readings. API server has rate limits, 
    which makes it impossible to stress test the data pipeline with real sensor
    readings. This function returns a simplified json data that mimics the structure in 
    the real readings.
    :param batch_num: the number of readings to be generated in a batch
    """
    data_points = []
    time = datetime.utcnow()
    time_str = time.strftime("%Y-%m-%dT%H:%M:%S")
    hour = time.hour

    for sensor_idx in range(1, batch_num + 1):
        if sensor_idx <= 1000:
            sensor_number = sensor_idx
        else:
            sensor_number = (sensor_idx % 1000) + 1
        row = {
            "sensor_path": "fake.temperature.sensor{}".format(sensor_number),
            "timestamp": time_str,
            "value": random_periodic(hour),
            "node_vsn": "fake-0C0"
        }
        data_points.append(row)

    return data_points


def random_periodic(hr_of_day, amp=2.5, freq=6, phi=0, bias=18):
    """
    A function for generating a sine wave shaped random process.
    :param hr_of_day: hour of the day (0 to 24)
    :param amp: amplitude of the sine wave
    :param freq: frequency of the sine wave
    :param phi: phase shift 
    :bias: a bias term for moving the sine wave vertically 
    """
    sine_wave = amp * sin(freq * hr_of_day + phi)
    random_temperature = sine_wave + bias + random.normalvariate(0, 0.5)
    return round(random_temperature)
