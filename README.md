## Introduction
Fire hazard, poor air quality and excessive noise are some of the environmental challenges that have 
become synonimous with large cities.

## Data pipeline design
[pipeline](img/pipeline-architecture.jpg)
## Infrastructure
[infra](img/infrastructure.png)
## How to run the monitoring platform

- 1. Spin up virtual machines as needed. But make sure at least 
kka and the database server have their own machine(s). See 
t [Infrastructure](Infrastructure) section for the recommended setup.
- 2. Install and configure [Kafka](https://kafka.apache.org/)
- 3. Install and configure [PostgreSQL & Timescaledb](https://docs.timescale.com/latest/gting-started/installation)
- 4. Install and configure [Grafana](https://grafana.com/)
- 5. Make sure python 3.X is installed in all machines
- 6. Clone this repository
`git clone https://github.com/mEyob/CityNet`
`cd CityNet`
- 7. Create a virtual environment (optional)
`thon -m venv <virtual-env-name>`
- 8. Activate virtual environmet (optional)
`urce <virtual-env-name>\bin\activate`
- 9. Install necessary packages 
`pip install -r requirements.txt`
- 10. Run Kafka producer and consumers. To check the available options:
`python producer.py --help`
- 11. Connect Grafana to the database and design a dashboard
