import requests
from datetime import datetime, UTC
import threading
import json
import csv
import random

from args import (
    get_number_of_threads,
    get_number_of_loops,
    use_endpoint,
    use_user_profile,
    use_random,
    get_config_path,
)

NUMBER_OF_THREADS = get_number_of_threads()
CONFIG_PATH = get_config_path()


def get_user_session(email: str, password: str) -> str:
    url = f"{BASE_URL}/session/{email}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"password": password}
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["session"]


def send_request(
    request_method: str,
    endpoint: str,
    content_type: str,
    parameters: dict,
) -> datetime | None:
    try:
        url = f"{BASE_URL}{endpoint}?session={SESSION}"
        headers = {"Content-Type": f"application/{content_type}"}
        request_method = getattr(requests, request_method.lower())
        response = request_method(url, data=parameters, headers=headers)  #
        if response.status_code != 200:
            return
        response_time = response.elapsed.total_seconds()
        print(f"Respose time for {endpoint}: {response_time} seconds")
        data = [response_time, datetime.now(UTC)]
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return


def calculate_metrics(resonse_datas: list) -> tuple:
    metrics = {}

    elapsed_times = [data[0] for data in resonse_datas]
    timedelta = (resonse_datas[-1][1] - resonse_datas[0][1]).total_seconds()
    print(f"Time elapsed: {timedelta} seconds")

    average_time = sum(elapsed_times) / len(elapsed_times)
    metrics["average_time"] = average_time
    print(f"Average elapsed time: {average_time} seconds")

    median_time = sorted(elapsed_times)[len(elapsed_times) // 2]
    metrics["median_time"] = median_time
    print(f"Median elapsed time: {median_time} seconds")

    if timedelta < 1:
        timedelta = 1

    throughput = len(elapsed_times) / timedelta
    metrics["throughput"] = throughput
    print(f"Throughput: {throughput} transactions per second")

    return metrics


def handle_single_endpoint():
    def thread_request():
        barrier.wait()

        elapsed_time = send_request(
            endpoint=path,
            request_method=request_method,
            content_type=content_type,
            parameters=parameters,
        )
        elapsed_times.append(elapsed_time)

    timestamp = datetime.now(UTC)
    elapsed_times = []
    threads = []
    number_of_threads = get_number_of_threads()
    barrier = threading.Barrier(number_of_threads)

    idx = use_endpoint()
    endpoint = CONFIG["endpoints"][idx]
    path = endpoint["path"]
    parameters = endpoint["parameters"]
    request_method = endpoint["method"]
    content_type = endpoint["content_type"]

    for _ in range(number_of_threads):
        thread = threading.Thread(target=thread_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    metrics = calculate_metrics(elapsed_times)

    with open("results_enpoints.csv", "a", newline="") as csvfile:
        fieldnames = [
            "timestamp_UTC",
            "endpoint",
            "load",
            "average_time",
            "median_time",
            "throughput",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow(
            {
                "timestamp_UTC": timestamp,
                "endpoint": endpoint["path"],
                "load": number_of_threads,
                "average_time": metrics["average_time"],
                "median_time": metrics["median_time"],
                "throughput": metrics["throughput"],
            }
        )


def handle_user_profile():
    def thread_request():
        barrier.wait()

        for idx in endpoints:
            endpoint = CONFIG["endpoints"][idx]
            path = endpoint["path"]
            request_method = endpoint["method"]
            content_type = endpoint["content_type"]
            parameters = endpoint["parameters"]

            elapsed_time = send_request(
                endpoint=path,
                request_method=request_method,
                content_type=content_type,
                parameters=parameters,
            )

            elapsed_times.append(elapsed_time)

    timestamp = datetime.now(UTC)
    elapsed_times = []
    threads = []
    number_of_threads = get_number_of_threads()
    barrier = threading.Barrier(number_of_threads)

    idx = use_user_profile()
    endpoints = CONFIG["user_profiles"][idx]

    for _ in range(number_of_threads):
        thread = threading.Thread(target=thread_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    metrics = calculate_metrics(elapsed_times)

    with open("results_users.csv", "a", newline="") as csvfile:
        fieldnames = [
            "timestamp_UTC",
            "user_profile",
            "load",
            "average_time",
            "median_time",
            "throughput",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow(
            {
                "timestamp_UTC": timestamp,
                "user_profile": idx,
                "load": number_of_threads,
                "average_time": metrics["average_time"],
                "median_time": metrics["median_time"],
                "throughput": metrics["throughput"],
            }
        )


def handle_random_endpoints():
    def thread_request():
        barrier.wait()

        random_idx = random.randint(0, len(CONFIG["endpoints"]) - 1)
        endpoint = CONFIG["endpoints"][random_idx]

        path = endpoint["path"]
        request_method = endpoint["method"]
        content_type = endpoint["content_type"]
        parameters = endpoint["parameters"]

        response_data = send_request(
            endpoint=path,
            request_method=request_method,
            content_type=content_type,
            parameters=parameters,
        )

        if response_data is not None:
            response_datas.append(response_data)

    timestamp = datetime.now(UTC)
    response_datas = []
    threads = []
    number_of_threads = get_number_of_threads()
    barrier = threading.Barrier(number_of_threads)

    for _ in range(number_of_threads):
        thread = threading.Thread(target=thread_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    metrics = calculate_metrics(response_datas)

    with open("results_random_endpoint.csv", "a", newline="") as csvfile:
        fieldnames = [
            "timestamp_UTC",
            "load",
            "average_time",
            "median_time",
            "throughput",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writerow(
            {
                "timestamp_UTC": timestamp,
                "load": number_of_threads,
                "average_time": metrics["average_time"],
                "median_time": metrics["median_time"],
                "throughput": metrics["throughput"],
            }
        )


if __name__ == "__main__":
    with open(CONFIG_PATH) as config_file:
        CONFIG = json.load(config_file)

    BASE_URL = CONFIG["base_url"]
    email = CONFIG["email"]
    password = CONFIG["password"]
    SESSION = get_user_session(email, password)

    for _ in range(get_number_of_loops()):
        if use_endpoint() is not None:
            handle_single_endpoint()
        elif use_user_profile() is not None:
            handle_user_profile()
        elif use_random():
            handle_random_endpoints()
        else:
            print("Add argument -u or -e or -r")
            break
