# Zeeguu API Stress Test

## Introduction

The aim of the project is to stress test a React-Flask application. The program sends requests to the API and measures the response time. The program can be run with multiple threads to simulate multiple users. The program can also be run with multiple user profiles to simulate different types of users.

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


## Introduction Master thesis, Stress tests

This project focuses on stress testing a virtual machine (VM) running a target application. Ideally, the stress tests will be executed from a separate VM to ensure the testing environment itself doesn't become a bottleneck in the workflow. After deploying the application and confirming it's running correctly, we shift our attention to configuring and executing the stress tests. Identifying performance bottlenecks involves several steps:

## 1. Set up of config file

The user must first create a configuration file that defines the request structure for the application under test. The expected format is as follows:

    {
      "id": 0,
      "path": "/upload_user_activity_data",
      "method": "POST",
      "content_type": "json",
      "parameters": {
        "time": "2016-05-05T10:11:12",
        "event": "User Read Article",
        "value": "300s",
        "extra_data": {
          "article_source": 2
        }
      }
    },

## 2. Prerequisites

To run the program you need Python 3 available with the packages listed in `requirements.txt` installed:

    ```bash
    pip install -r requirements.txt
    ```
## 3. Running the stress tests

Define the scope of the stress tests—specifically, the number of threads (representing users) and the number of request loops. This is done via command-line arguments:

Available Arguments:
    - `--threads` or `-t`: The number of threads to use. Default is 1.
    - `--loops` or `-l`: The number of times the simulation will run. Default is 1.
    - `--workflow` or `-w`: The simulator runs multiple times with increasing number of threads. Can be combined with `--loops`.
    - `--endpoint` or `-e`: Use a single endpoint. Provide the index of the endpoint from the config file.
    - `--random` or `-r`: Use random endpoints. Default is False.
    - `--config_path` or `-c`: The path to the config file. Default is "config.json".
    - `--no_save` or `-ns`: Don't save the results to a .csv file.

Example Usage:
    To run a stress test using the workflow mode with random endpoints, 5 loops, and 5 threads

    ```bash
    cd src
    python StressTest.py -w -r -l 5
    ```
Running in the Background (Recommended for VMs)

   If you're running this on a VM and want the test to continue after closing your terminal session, you can use either & or nohup. The latter is recommended for longer tests.

    Option 1: Using & (runs in the background until session ends)
        ```bash
            python StressTest.py -w -r -l 5 &
        ```

    Option 2: Using nohup (runs in the background and survives logout)
        ```bash
        nohup python StressTest.py -w -r -l 5 > stress_log.txt 2>&1 &
        ```
    Explanation:
        - nohup: ignores hangup signals

        - > stress_log.txt: writes output to a log file

        - 2>&1: redirects errors to the same file

        - &: runs in the background


## 4. Visualizing the Results

Once the stress tests complete, you can visualize the output data using Visualizer.py. Choose from several graph types depending on what you want to analyze.

    if __name__ == "__main__":
        file = "./results/1.csv"
        df = pd.read_csv(file)
        # throughput(df)
        # latency_histogram_of_load(df, 13)
        # latency_histogram_sum(df)
        # latency_curve(df)
        histogram_3d(df)

To Run the Visualizer:

    1. copy the name of the `.csv` file you want to visualize to the `file` variable in `src/Visualizer.py`
    2. uncomment the type of visualization you want to use
    3. run the visualizer:

    ```bash
    python .src/Visualizer.py
    ```




## Introduction Master thesis, Logger set up 

To identify the application's bottleneck, proper logging must be set up for each layer of the system. While the exact configuration depends on the system architecture, the key goal is to ensure that logs are collected from all critical components and stored outside of the Docker containers for easy analysis.In our case, the system architecture is as follows:

    Nginx - Gunicorn - Flask Api - MySQL 

To trace performance issues and locate potential bottlenecks, we configured logging for each component. Nginx runs directly on the VM, while Gunicorn and Flask API are containerized and managed via docker-compose.yaml.

## Nginx Custom Log Format
To pinpoint whether a bottleneck occurs in Gunicorn, Nginx, or due to network latency, we needed detailed timing information in the logs—specifically:

    When a request arrived at Nginx (from the stress test VM)

    When Gunicorn responded back through Nginx

We customized Nginx’s logging format accordingly:

    log_format custom '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '$request_time $upstream_response_time';

This format allowed us to track both the total request duration ($request_time) and the time taken by Gunicorn ($upstream_response_time).

For our use case, access logs and error logs were sufficient to detect issues and analyze performance patterns across the stack.

    access_log /var/log/nginx/access.log custom;
    error_log /var/log/nginx/error.log;

## Gunicorn log set up

To persist logs outside the container, we configured Gunicorn via the Dockerfile. This setup ensures that both access and error logs from Gunicorn are written to mounted volumes, making them accessible from the host machine for further inspection and visualization.

# Expose Gunicorn port
EXPOSE 8080

# Command to run Gunicorn
CMD gunicorn -w 4 -b 0.0.0.0:8080 start:application \
    --access-logfile access.log \
    --access-logformat "%(U)s %(t)s %(M)sms"
