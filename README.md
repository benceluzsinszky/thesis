# Zeeguu API Stress Test

## Introduction

The aim of the project is to stress testa React-Flask application. The program sends requests to the API and measures the response time. The program can be run with multiple threads to simulate multiple users. The program can also be run with multiple user profiles to simulate different types of users.

The output of the program are .csv files with the measured averrage response times of the HTTP requests.

## Prerequisites

To run the program you need Python 3 available with the requests package installed:

```bash
pip install requests
```

## Running the program

The program uses arguments to run. The arguments are as follows:

- `--threads` or `-t`: The number of threads to use. Default is 1.
- `--endpoint` or `-e`: Use a single endpoint. Provide the index of the endpoint from the config file.
- `--user_profile` or `-u`: Use a user profile. Provide the index of the user profile from the config file. Default is 0.
- `--config_path` or `-c`: The path to the config file. Default is "config.json".

Example usage:

```bash
python ZeeguuApi.py -u 0 -t 1
```

Increase the number of threads and observer the change in the outoput .csv files or in the print statements.

## User profiles

TODO:
Add description to user profiles here.

## Remark

The project is a work in progress. The program is not yet fully functional, most of the endpoints and the user profiles are not yet implemented.

All the information about the endpoints and the user profiles in the config file are fictional.
