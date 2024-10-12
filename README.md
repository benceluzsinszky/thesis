# Zeeguu API Stress Test Simulator

## Running the simulator

The simulator uses arguments to run. The arguments are as follows:

- `--threads` or `-t`: The number of threads to use. Default is 1.
- `--endpoint` or `-e`: Use a single endpoint. Provide the index of the endpoint from the config file.
- `--user_profile` or `-u`: Use a user profile. Provide the index of the user profile from the config file. Default is 0.
- `--config_path` or `-c`: The path to the config file. Default is "config.json".

Example usage:

```bash
python ZeeguuApi.py -u 0 -t 1
```

Increase the number of threads and observer the change in the outoput .csv files.

## User profiles

Add description to user profiles here.
