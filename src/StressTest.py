import requests
from datetime import datetime, UTC
import threading
import pandas as pd
import csv
import random
import tqdm

from Args import (
    get_number_of_threads,
    get_number_of_loops,
    use_workflow,
    use_endpoint,
    use_user_profile,
    use_random,
    get_config_path,
    use_csv_file,
)

from FileIO import load_config_file, write_to_csv

from Visualizer import visualize


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
        data = [response_time, datetime.now(UTC)]
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return


def calculate_metrics(response_datas: list, test_type: str) -> pd.DataFrame:
    metrics = pd.DataFrame(
        columns=[
            "timestamp",
            "test_type",
            "load",
            "average_latency",
            "median_latency",
            "throughput",
        ]
    )

    elapsed_times = [data[0] for data in response_datas]
    timedelta = (response_datas[-1][1] - response_datas[0][1]).total_seconds()

    average_latency = sum(elapsed_times) / len(elapsed_times)

    median_latency = sorted(elapsed_times)[len(elapsed_times) // 2]

    if timedelta < 1:
        timedelta = 1

    throughput = len(elapsed_times) / timedelta

    metrics.loc[0] = [
        pd.Timestamp.now(),
        test_type,
        NUMBER_OF_THREADS,
        average_latency,
        median_latency,
        throughput,
    ]

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

    response_datas = []
    threads = []

    barrier = threading.Barrier(NUMBER_OF_THREADS)

    for _ in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=thread_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    metrics = calculate_metrics(response_datas=response_datas, test_type="random")

    return metrics


if __name__ == "__main__":
    NUMBER_OF_THREADS = get_number_of_threads()
    CONFIG_PATH = get_config_path()
    CONFIG = load_config_file(CONFIG_PATH)

    WORKFLOW_THREADS = [1, 5, 10]

    # WORKFLOW_THREADS = [
    #     1,
    #     2,
    #     3,
    #     4,
    #     5,
    #     6,
    #     7,
    #     8,
    #     9,
    #     10,
    #     11,
    #     12,
    #     13,
    #     14,
    #     15,
    #     16,
    #     17,
    #     18,
    #     19,
    #     20,
    #     21,
    #     22,
    #     23,
    #     24,
    #     25,
    #     30,
    #     35,
    #     40,
    #     45,
    #     50,
    #     60,
    #     70,
    #     80,
    #     90,
    #     100,
    #     125,
    #     150,
    # ]

    BASE_URL = CONFIG["base_url"]
    email = CONFIG["email"]
    password = CONFIG["password"]
    SESSION = get_user_session(email, password)

    df = pd.DataFrame()

    if not use_workflow():
        WORKFLOW_THREADS = [NUMBER_OF_THREADS]

    total_iterations = len(WORKFLOW_THREADS) * get_number_of_loops()

    with tqdm.tqdm(total=total_iterations, desc="Progress:") as pbar:
        for threads in WORKFLOW_THREADS:
            NUMBER_OF_THREADS = threads
            for _ in range(get_number_of_loops()):
                if use_endpoint() is not None:
                    handle_single_endpoint()
                elif use_user_profile() is not None:
                    handle_user_profile()
                elif use_random():
                    data = handle_random_endpoints()
                    df = pd.concat([df, data], ignore_index=True)
                else:
                    print("Add argument -u or -e or -r")
                    break
                pbar.update(1)

    if use_csv_file():
        write_to_csv(df)

    visualize(df)
