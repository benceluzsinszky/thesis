import requests
from datetime import datetime, timedelta, UTC
import threading
import json


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
    barrier.wait()

    try:
        url = f"{base_url}{endpoint}?session={session}"
        headers = {"Content-Type": f"application/{content_type}"}
        time = datetime.now(UTC)

        request_method = getattr(requests, request_method.lower())
        request_method(url, data=parameters, headers=headers)

        elapsed_time = datetime.now(UTC) - time
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print(f"Elapsed Time: {elapsed_time} seconds")
    elapsed_times.append(elapsed_time)


if __name__ == "__main__":
    with open("config.json") as config_file:
        config = json.load(config_file)

    base_url = config["base_url"]
    email = config["email"]
    password = config["password"]

    session = get_user_session(base_url, email, password)

    elapsed_times = []

    number_of_threads = 100
    barrier = threading.Barrier(number_of_threads)

    threads = []

    endpoint = config["endpoints"][0]

    path = endpoint["path"]
    parameters = endpoint["parameters"]
    request_method = endpoint["method"]
    content_type = endpoint["content_type"]

    for i in range(number_of_threads):
        thread = threading.Thread(
            target=thread_request,
            args=(
                barrier,
                session,
                request_method,
                content_type,
                base_url,
                path,
                parameters,
                elapsed_times,
            ),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    average_elapsed_time = sum(elapsed_times, timedelta()) / len(elapsed_times)
    print(f"Average elapsed time: {average_elapsed_time} seconds")
    median_elapsed_time = sorted(elapsed_times)[len(elapsed_times) // 2]
    print(f"Median elapsed time: {median_elapsed_time} seconds")
