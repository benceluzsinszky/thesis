# Zeeguu API Stress Test

## Introduction

The aim of the project is to stress testa React-Flask application. The program sends requests to the API and measures the response time. The program can be run with multiple threads to simulate multiple users. The program can also be run with multiple user profiles to simulate different types of users.

The output of the program are .csv files with the measured averrage response times of the HTTP requests.

## Prerequisites

To run the program you need Python 3 available with the packages listed in `requirements.txt` installed:

```bash
pip install -r requirements.txt
```

## Running the program

The program uses arguments to run. The arguments are as follows:

- `--threads` or `-t`: The number of threads to use. Default is 1.
- `--loops` or `-l`: The number of times the simulation will run. Default is 1.
- `--workflow` or `-w`: The simulator runs multiple times with increasing number of threads. Can be combined with `--loops`.
- `--endpoint` or `-e`: Use a single endpoint. Provide the index of the endpoint from the config file.
- `--user_profile` or `-u`: Use a user profile. Provide the index of the user profile from the config file. Default is 0.
- `--random` or `-r`: Use random endpoints. Default is False.
- `--config_path` or `-c`: The path to the config file. Default is "config.json".
- `--no_save` or `-ns`: Don't save the results to a .csv file.

Example usage (run workflow with random endpoints, 5 loops and 5 threads):

```bash
python src/StressTest.py -w -r -l 5 -t 5
```

Increase the number of threads and observer the change in the outoput .csv files or in the print statements.

## User profiles

In the config file a user profile is an array of maps, with an id, a name and endpoints.
Endpoints is again an array of maps with:

- id: the index of the endpoint in the config file
- repeat: the number of times the endpoint should be called
- delay: the delay after the endpoint is called

The last delay should always be zero.
The indexing of the user profiles starts from 0.

- Profile 0: The Exerciser

  - login
  - sees articles on the homepage but decides that he wants to exercise (1s)
  - selects exercises tab
  - repeats 10 times the following
    - starts looking at the first exercise (~2s)
    - asks for hint; looks at hint for (~1s)
    - asks for solution; looks at it for 1s
    - clicks next

- Profile 1: The Loiterer

  - login
  - goes to /words
  - scrolls three times to get new articles
  - goes to /saved articles
  - opens a saved article
  - goes to /history
  - goes /user_dashboard
  - opens /settings
  - goes to /searches and searches something

(spends 1s between every action)

- Profile 2: The Reader

  - login
  - /scrolls three times past the end of the page
  - opens one article
  - translates 7 words
  - reviews words

(1 - 3s between actions)

- Profile 3: The Reader-Exerciser

  - login
  - goes to the My Searches Page
  - picks an Article that is Available
  - makes Translations of 5 words
  - opens the /words tab
  - goes to exercises and completes an exercise session (some correct some show solution)

(1 - 3s between actions)

## Remark

The project is a work in progress. The program is not yet fully functional, most of the endpoints and the user profiles are not yet implemented.

All the information about the endpoints and the user profiles in the config file are fictional.
