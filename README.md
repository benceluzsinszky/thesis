# Zeeguu API Stress Test

## Introduction

The aim of the project is to stress testa React-Flask application. The program sends requests to the API and measures the response time. The program can be run with multiple threads to simulate multiple users. The program can also be run with multiple user profiles to simulate different types of users.

The output of the program are .csv files with the measured averrage response times of the HTTP requests.

## Prerequisites

To run the program you need Python 3 available with the packages listed in `requirements.txt` installed:

```bash
pip install -r requirements.txt
```

## Running the Stress Test

The program uses arguments to run. The arguments are as follows:

- `--threads` or `-t`: The number of threads to use. Default is 1.
- `--loops` or `-l`: The number of times the simulation will run. Default is 1.
- `--workflow` or `-w`: The simulator runs multiple times with increasing number of threads. Can be combined with `--loops`.
- `--endpoint` or `-e`: Use a single endpoint. Provide the index of the endpoint from the config file.
- `--random` or `-r`: Use random endpoints. Default is False.
- `--config_path` or `-c`: The path to the config file. Default is "config.json".
- `--no_save` or `-ns`: Don't save the results to a .csv file.

Example usage (run workflow with random endpoints, 5 loops and 5 threads):

```bash
cd src
python StressTest.py -w -r -l 5
```

Increase the number of threads and observe the change in the outoput .csv files or in the print statements.

## Running the Visualizer

To run the visualizer:

1. copy the name of the `.csv` file you want to visualize to the `file` variable in `src/Visualizer.py`
2. uncomment the type of visualization you want to use
3. run the visualizer:

```bash
python .src/Visualizer.py
```
