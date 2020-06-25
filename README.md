## CityNet: a city-scale environmental monitoring platform

## Table of Contents
1. [Introduction](README.md#introduction)
1. [Data pipeline](README.md#data-pipeline)
1. [Infrastructure](README.md#infrastructure)
1. [How to run the monitoring platform](README.md#how-to-run-the-monitoring-platform)
1. [Assumptions](README.md#assumptions)
1. [Files in Repo](README.md#files-in-repo)
1. [Contact Information](README.md#contact-information)


## Introduction
Fire hazard, poor air quality and excessive noise are some of the environmental challenges that have 
become synonimous with large cities. While these problems are well known to the public, there is still a lack of monitoring platforms, where various stakeholders can monitor the environmental conditions on a block-by-block resolution.

The [Array of Things](https://arrayofthings.github.io/) project aims to tackle this problem by providing real-time information on environmental and air quality conditions by leveraging a city-wide sensor network deployed in Chicago city.

Data pipeline, 
streaming sensor data, 
database, 
visualization,
outlier detection,
further analysis and scientific research

[![Demo](img/demo-screenshot.png)](https://youtu.be/BCmYLDmvXD8 "Demo")

## Data pipeline 

<center><img src="img/pipeline-architecture.jpg" align="middle" style="width: 500px; height: 300px" /></center>

## Infrastructure

<center><img src="img/infrastructure.png" align="middle" style="width: 500px; height: 300px" /></center>

## How to run the monitoring platform

1. Spin up virtual machines as needed. But make sure at least Kafka and the database server have their own machine(s). See the [Infrastructure](README.md#infrastructure) section for the recommended setup.
2. Install and configure [Kafka](https://kafka.apache.org/)
3. Install and configure [PostgreSQL & Timescaledb](https://docs.timescale.com/latest/gting-started/installation)
4. Install and configure [Grafana](https://grafana.com/)
5. Make sure python 3.X is installed in all machines
6. Clone this repository

```bash
git clone https://github.com/mEyob/CityNet`
cd CityNet
```
7. Create a virtual environment (optional)

```bash
python -m venv <virtual-env-name>
```
8. Activate virtual environmet (optional)

```bash
source <virtual-env-name>\bin\activate
```
9. Install necessary packages 

```bash
pip install -r requirements.txt
```

10. Run Kafka producer and consumers. To check the available options:

```python
python producer.py --help
python consumer.py --help
```
11. Connect Grafana to the database and design a dashboard

## Files in repo

## Contact information
