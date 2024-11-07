import requests
from datetime import datetime, UTC
import threading
import pandas as pd
import random
import time
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
        if "query" in parameters:
            url += f"&{parameters['query']}"
        headers = {"Content-Type": f"application/{content_type}"}
        request_method = getattr(requests, request_method.lower())
        response = request_method(url, data=parameters, headers=headers)  #
        if response.status_code != 200:
            print(f"Error at {endpoint}: {response.status_code}")
            return [datetime.now(UTC), "N/A", endpoint]
        response_time = response.elapsed.total_seconds()
        data = [datetime.now(UTC), response_time, endpoint]
        return data

    except Exception as e:
        print(f"An error occurred: {e}")
        return [datetime.now(UTC), "N/A", endpoint]


def handle_single_endpoint():
    def thread_request():
        barrier.wait()

        response_data = send_request(
            endpoint=path,
            request_method=request_method,
            content_type=content_type,
            parameters=parameters,
        )

        response_datas.append(response_data)

    response_datas = []
    threads = []

    barrier = threading.Barrier(NUMBER_OF_THREADS)

    idx = use_endpoint()
    endpoint = CONFIG["endpoints"][idx]
    path = endpoint["path"]
    parameters = endpoint["parameters"]
    request_method = endpoint["method"]
    content_type = endpoint["content_type"]

    for _ in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=thread_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    raw_data = pd.DataFrame(
        response_datas, columns=["timestamp", "latency", "endpoint"]
    )
    raw_data["test_type"] = f"user_profile_{idx}"
    raw_data["load"] = NUMBER_OF_THREADS

    return raw_data


def handle_user_profile():
    def thread_request():
        barrier.wait()

        for i in endpoints:
            endpoint = CONFIG["endpoints"][i["id"]]
            path = endpoint["path"]
            request_method = endpoint["method"]
            content_type = endpoint["content_type"]
            parameters = endpoint["parameters"]

            for _ in range(i["repeat"]):
                response_data = send_request(
                    endpoint=path,
                    request_method=request_method,
                    content_type=content_type,
                    parameters=parameters,
                )
                response_datas.append(response_data)
                time.sleep(i["delay"] / 10)

    response_datas = []
    threads = []

    barrier = threading.Barrier(NUMBER_OF_THREADS)

    idx = use_user_profile()
    profile = CONFIG["user_profiles"][idx]
    endpoints = profile["endpoints"]

    for _ in range(NUMBER_OF_THREADS):
        thread = threading.Thread(target=thread_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    raw_data = pd.DataFrame(
        response_datas, columns=["timestamp", "latency", "endpoint"]
    )
    raw_data["test_type"] = f"user_profile_{idx}"
    raw_data["load"] = NUMBER_OF_THREADS

    return raw_data


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

    raw_data = pd.DataFrame(
        response_datas, columns=["timestamp", "latency", "endpoint"]
    )
    raw_data["test_type"] = "random"
    raw_data["load"] = NUMBER_OF_THREADS

    return raw_data


if __name__ == "__main__":
    NUMBER_OF_THREADS = get_number_of_threads()
    CONFIG_PATH = get_config_path()
    CONFIG = load_config_file(CONFIG_PATH)

    WORKFLOW_THREADS = [1, 5, 10, 20, 25]

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
    #     12,
    #     14,
    #     16,
    #     18,
    #     20,
    #     25,
    #     30,
    #     35,
    #     40,
    #     45,
    #     50,
    #     60,
    #     70,
    #     90,
    #     100,
    # ]

    BASE_URL = CONFIG["base_url"]
    email = CONFIG["email"]
    password = CONFIG["password"]
    SESSION = get_user_session(email, password)

    df = pd.DataFrame()

    if not use_workflow():
        WORKFLOW_THREADS = [NUMBER_OF_THREADS]

    total_iterations = len(WORKFLOW_THREADS) * get_number_of_loops()

    with tqdm.tqdm(total=total_iterations, desc="Progress") as pbar:
        for threads in WORKFLOW_THREADS:
            NUMBER_OF_THREADS = threads
            for _ in range(get_number_of_loops()):
                if use_endpoint() is not None:
                    data = handle_single_endpoint()
                elif use_user_profile() is not None:
                    data = handle_user_profile()
                elif use_random():
                    data = handle_random_endpoints()
                else:
                    print("Add argument -u or -e or -r")
                    break
                df = pd.concat([df, data], ignore_index=True)
                pbar.update(1)

    if use_csv_file():
        write_to_csv(df)
