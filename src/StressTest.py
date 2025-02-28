import requests
from datetime import datetime, timezone
import threading
import pandas as pd
import random
import logging

from Args import use_endpoint, get_config_path, get_number_of_loops

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


def prepare_sessions() -> int:
    url = f"{BASE_URL}/exercise_session_start?session={SESSION}"
    response = requests.post(url)
    return response.json()["id"]


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
        if "session_update" in endpoint:
            parameters["id"] = RW_SESSION_ID
        request_method = getattr(requests, request_method.lower())
        response = request_method(url, data=parameters, headers=headers)
        if response.status_code != 200:
            print(f"Error at {endpoint}: {response.status_code}")
            return [datetime.now(timezone.utc), "N/A", endpoint]
        response_time = response.elapsed.total_seconds()
        LOGGER.info(f"Request to {endpoint} completed in {response_time} seconds")

        data = [datetime.now(timezone.utc), response_time, endpoint]
        return data

    except Exception as e:
        LOGGER.error(f"An error occurred: {str(e)}")
        return [datetime.now(timezone.utc), "N/A", endpoint]


def handle_single_endpoint():
    def thread_request():
        try:
            barrier.wait()

            response_data = send_request(
                endpoint=path,
                request_method=request_method,
                content_type=content_type,
                parameters=parameters,
            )

            response_datas.append(response_data)
        except Exception as e:
            LOGGER.error(f"An error occurred: {str(e)}")

    response_datas = []
    threads = []

    barrier = threading.Barrier(NUMBER_OF_USERS)


    idx = use_endpoint()
    endpoint = CONFIG["endpoints"][idx]
    path = endpoint["path"]
    parameters = endpoint["parameters"]
    request_method = endpoint["method"]
    content_type = endpoint["content_type"]

    LOGGER.info(f"Handling endpoint: {path} with {NUMBER_OF_USERS} users")


    for _ in range(NUMBER_OF_USERS):
        thread = threading.Thread(target=thread_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    raw_data = pd.DataFrame(
        response_datas, columns=["timestamp", "latency", "endpoint"]
    )
    raw_data["test_type"] = f"user_profile_{idx}"
    raw_data["load"] = NUMBER_OF_USERS

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

    barrier = threading.Barrier(NUMBER_OF_USERS)

    for _ in range(NUMBER_OF_USERS):
        thread = threading.Thread(target=thread_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    raw_data = pd.DataFrame(
        response_datas, columns=["timestamp", "latency", "endpoint"]
    )
    raw_data["test_type"] = "random"
    raw_data["load"] = NUMBER_OF_USERS

    return raw_data


def check_latency(df: pd.DataFrame) -> bool:
    try:
        median_latency = df["latency"].median()
        is_median_latency_ok = median_latency < MAX_LATENCY
        if not is_median_latency_ok:
            LOGGER.info(f"Median latency {median_latency} is over the threshold")
        return is_median_latency_ok
    except Exception as e:
        LOGGER.error(f"An error occurred: {str(e)}")
        return True


if __name__ == "__main__":
    MAX_LATENCY = 5

    CONFIG_PATH = get_config_path()
    CONFIG = load_config_file(CONFIG_PATH)


    BASE_URL = CONFIG["base_url"]
    email = CONFIG["email"]
    password = CONFIG["password"]
    SESSION = get_user_session(email, password)

    RW_SESSION_ID = prepare_sessions()

    running = True

    endpoint_id = use_endpoint()

    LOGGER = logging.getLogger("CrawlerLogger")
    LOGGER.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    # while running:
    LOGGER.info("Starting stress test")
    for users in range(1, 5):
        LOGGER.info(f"Running with {users} users")
        df = pd.DataFrame()
        NUMBER_OF_USERS = users

        for _ in range(get_number_of_loops()):
            try:
                data = handle_single_endpoint()
                df = pd.concat([df, data], ignore_index=True)
            except Exception as e:
                LOGGER.error(f"An error occurred: {str(e)}")
                continue

        try:
            write_to_csv(df, endpoint_id)
        except Exception as e:
            LOGGER.error(f"Could not write to csv: {str(e)}")
        LOGGER.info(f"Finished running with {users} users")
        running = check_latency(df)
