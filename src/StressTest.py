import requests
from datetime import datetime, timezone
import threading
from threading import Lock
import pandas as pd
import logging
import copy
from Args import (
    use_endpoint,
    use_skip,
    get_config_path,
    get_number_of_loops,
    get_number_of_threads,
)

from FileIO import load_config_file, write_to_csv

REQUEST_COUNTER = {"value": 0}
LOCK = Lock()

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

        # if "value" in parameters:
        #     REQUEST_COUNTER["value"] += 1
        #     parameters["value"] = f"{REQUEST_COUNTER['value']}s"
        if "session_update" in endpoint:
            parameters["id"] = RW_SESSION_ID
        request_method = getattr(requests, request_method.lower())
        response = request_method(url, data=parameters, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Error at {endpoint}: {response.status_code}")
            return [datetime.now(timezone.utc), "N/A", endpoint]
        response_time = response.elapsed.total_seconds()
        LOGGER.debug(f"Request to {endpoint} completed in {response_time} seconds")

        data = [datetime.now(timezone.utc), response_time, endpoint]
        return data

    except Exception as e:
        LOGGER.error(f"An error occurred during sending request: {e}")
        return [datetime.now(timezone.utc), "N/A", endpoint]



def handle_single_endpoint(idx) -> dict:
    def thread_request():
        try:
            barrier.wait()

            thread_parameters = copy.deepcopy(parameters)

            # ✅ Safe increment using lock
            with LOCK:
                REQUEST_COUNTER["value"] += 1
                thread_parameters["value"] = f"{REQUEST_COUNTER['value']}s"

            response_data = send_request(
                endpoint=path,
                request_method=request_method,
                content_type=content_type,
                parameters=thread_parameters,
            )

            response_datas.append(response_data)
        except Exception as e:
            LOGGER.error(f"An error occurred during sending threaded request: {e}")

    response_datas = []
    threads = []

    barrier = threading.Barrier(NUMBER_OF_USERS)

    endpoint = CONFIG["endpoints"][idx]
    path = endpoint["path"]
    parameters = endpoint["parameters"]
    request_method = endpoint["method"]
    content_type = endpoint["content_type"]

    LOGGER.debug(f"Handling endpoint: {path} with {NUMBER_OF_USERS} users")

    for _ in range(NUMBER_OF_USERS):
        thread = threading.Thread(target=thread_request)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    data = pd.DataFrame(response_datas, columns=["timestamp", "latency", "endpoint"])
    data["load"] = NUMBER_OF_USERS

    return data


def check_latency(df: pd.DataFrame) -> bool:
    try:
        df = df[df["latency"].notna() & (df["latency"] != "N/A")]
        if df.empty:
            LOGGER.info("No valid latency data available, stopping test")
            return False

        median_latency = df["latency"].median()
        LOGGER.info(f"Median latency: {median_latency}")
        is_median_latency_ok = median_latency < MAX_LATENCY
        if not is_median_latency_ok:
            LOGGER.info(
                f"Median latency {median_latency} is over the threshold, stopping test"
            )
        return is_median_latency_ok
    except Exception as e:
        LOGGER.error(f"An error occurred during checking latency: {e}")
        return True


if __name__ == "__main__":
    MAX_LATENCY = 2

    CONFIG_PATH = get_config_path()
    CONFIG = load_config_file(CONFIG_PATH)

    BASE_URL = CONFIG["base_url"]
    email = CONFIG["email"]
    password = CONFIG["password"]
    SESSION = get_user_session(email, password)

    RW_SESSION_ID = prepare_sessions()

    if use_endpoint():
        endpoints = [CONFIG["endpoints"][use_endpoint()]]
    else:
        endpoints = CONFIG["endpoints"]

    LOGGER = logging.getLogger("StressTestLogger")
    LOGGER.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    is_skip = use_skip()

    LOGGER.info("Starting stress test")
    for i in endpoints:
        running = True
        users = get_number_of_threads()
        endpoint_id = i["id"]
        path = i["path"]
        file_name_path = path[1:].replace("/", "_")
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"{file_name_path}_{now}.csv"
        LOGGER.info(f"Starting test for endpoint: {path}")
        
        while running:
            # for users in range(1, 4):
            LOGGER.info(f"Testing {path} with {users} users")
            NUMBER_OF_USERS = users

            df = pd.DataFrame()

            for _ in range(get_number_of_loops()):
                try:
                    data_df = handle_single_endpoint(endpoint_id)
                    df = pd.concat([df, data_df], ignore_index=True)
                except Exception as e:
                    LOGGER.error(f"An error occurred during loop: {e}")
                    continue

            try:
                write_to_csv(df, output_file_name)
            except Exception as e:
                LOGGER.error(f"Could not write to csv: {e}")
            LOGGER.info(f"Finished testing {path} with {users} users")
            running = check_latency(df)
            if is_skip:
                if users == 1:
                    users = 10
                else:
                    users += 10
            else:
                users += 1

            if get_number_of_threads() > 1:
                break

        LOGGER.info(f"Finished test for endpoint: {path}")

    LOGGER.info("Stress test finished")
