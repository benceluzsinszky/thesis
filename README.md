# REST API Stress Test

## Introduction

This project focuses on stress testing a virtual machine (VM) running a target application. The stress tests must be executed from a separate VM to ensure the testing environment itself doesn't become a bottleneck in the workflow.

## Prerequisites

### Set up of config file

The user must first create a configuration file that defines the request structure for the application under test. The expected format is as follows:

```JSON
{
  "base_url": "http://IP:PORT/",
  "email": "email@provider.com",
  "password": "{password}",
  "endpoints": [
        {
        "id": 0,
        "path": "/path",
        "method": "METHOD",
        "content_type": "content_type",
        "parameters": {
            "key": "value",
            }
        },
    ]
}
```

For the test to run, the API must have a /session endpoint, where a POST request can be made to authenticate the user with "email" and "password" in the body of the request. The response must contain a session id, that can be added to the requests by the stress test.

To run the program you need Python 3 available with the packages listed in `requirements.txt` installed:

```bash
pip install -r requirements.txt
```

## Running the stress tests

Define the scope of the stress tests—specifically, the number of threads (representing users) and the number of request loops. This is done via command-line arguments:

### Available Arguments

- `--loops` or `-l`: The number of times the simulation will run for each load level. Default is 1.
- `--endpoint` or `-e`: Use a single endpoint. Provide the index of the endpoint from the config file. Without this argument, the test will run with all endpoints.
- `--threads` or `-t`: The number of threads to use. Without this argument, the test will run, until the median response time exceeds 2 seconds.
- `--skip` or `-s`: Increment user count by 10 instead of 1 in each iteration.

### Example Usage

To run a stress test on all the endpoints, with increasing number of threads and 20 loops use this command:

```bash
python src/StressTest.py -l 20
```

### Running in the Background

The stress test can take a long time to complete, so it is recommended to run it in the background. To do this, use the following command:

```bash
nohup python StressTest.py -w -r -l 5 > stress_log.txt 2>&1 &
```

## Visualizing the Results

Once the stress tests complete, you can visualize the output data using Visualizer.py. Choose from several graph types depending on what you want to analyze, uncomment the desired function in the main block of the script, and run it.

```Python
if __name__ == "__main__":
    file = "./results/example.csv"
    df = pd.read_csv(file)
    throughput(df)
    # latency_histogram_of_load(df, 277)
    # latency_histogram_sum(df)
    latency_curve(df)
    histogram_3d(df)
```

To Run the Visualizer:

1. Copy the name of the `.csv` file you want to visualize to the `file` variable in `src/Visualizer.py`
2. Uncomment the type of visualization you want to use
3. Run the visualizer:

```bash
python .src/Visualizer.py
```

## Resource Logging

With the stress test test, an additional resource logging script is provided. This script logs the CPU, Memory and Network usage of the VM running the stress test.

To run the script in the background, clone the repository to the VM under test and run the following command:

```bash
nohup ./resource_logger.sh &
```

The script saves into `resource_log.txt` in the same directory.

The script needs to be stopped manually once the stress test is complete!
