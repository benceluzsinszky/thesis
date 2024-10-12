import requests
from datetime import datetime, timedelta, UTC
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from args import get_number_of_threads, use_endpoint, use_user_profile, get_config_path

NUMBER_OF_THREADS = get_number_of_threads()
CONFIG_PATH = get_config_path()

def get_user_session(base_url: str, email: str, password: str) -> str:
    url = f"{base_url}/session/{email}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"password": password}
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["session"]

def thread_request(
    barrier: threading.Barrier,
    session: str,
    request_method: str,
    content_type: str,
    base_url: str,
    endpoint: str,
    parameters: dict,
    elapsed_times: list,
):
    # Ensure threads wait for each other before starting
    barrier.wait()

    try:
        url = f"{base_url}{endpoint}?session={session}"
        headers = {"Content-Type": f"application/{content_type}"}
        start_time = datetime.now(UTC)

        # Make the HTTP request using the provided method
        request_function = getattr(requests, request_method.lower())
        request_function(url, data=parameters, headers=headers)

        # Calculate the elapsed time for the request
        elapsed_time = datetime.now(UTC) - start_time
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print(f"Elapsed Time: {elapsed_time} seconds")
    elapsed_times.append(elapsed_time)

if __name__ == "__main__":
    with open(CONFIG_PATH) as config_file:
        config = json.load(config_file)

    base_url = config["base_url"]
    email = config["email"]
    password = config["password"]

    # Obtain the session
    session = get_user_session(base_url, email, password)

    elapsed_times = []

    number_of_threads = NUMBER_OF_THREADS
    barrier = threading.Barrier(number_of_threads)

    # Extract the necessary endpoint information
    endpoint_idx = use_endpoint()
    if endpoint_idx is not None:
        endpoint = config["endpoints"][endpoint_idx]
        path = endpoint["path"]
        parameters = endpoint["parameters"]
        request_method = endpoint["method"]
        content_type = endpoint["content_type"]

        # Use ThreadPoolExecutor to handle the threads
        with ThreadPoolExecutor(max_workers=number_of_threads) as executor:
            futures = [
                executor.submit(
                    thread_request,
                    barrier,
                    session,
                    request_method,
                    content_type,
                    base_url,
                    path,
                    parameters,
                    elapsed_times
                )
                for _ in range(number_of_threads)
            ]

            # Ensure all threads complete execution
            for future in futures:
                future.result()

        # Calculate and display the average and median elapsed times
        average_elapsed_time = sum(elapsed_times, timedelta()) / len(elapsed_times)
        print(f"Average elapsed time: {average_elapsed_time} seconds")
        median_elapsed_time = sorted(elapsed_times)[len(elapsed_times) // 2]
        print(f"Median elapsed time: {median_elapsed_time} seconds")
    else:
        print("No endpoint specified.")
