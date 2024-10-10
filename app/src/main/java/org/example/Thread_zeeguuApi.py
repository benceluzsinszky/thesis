import threading
from ZeeguuApi import ZeeguuApi
import statistics

def thread_zeeguu(api, endpoint, body, barrier,elapsed_times, lock):
    # Wait for all threads to be ready
    barrier.wait()
    elapsed_time = api.send_http_request(endpoint, body)
    print(f"Elapsed Time: {elapsed_time} microseconds")
    
    # Safely append the elapsed time to the shared list
    elapsed_times.append(elapsed_time)

if __name__ == "__main__":
    base_url = "https://api.maxitwit.tech"
    email = "bluz@itu.dk"
    password = "password"
    endpoint = "/upload_user_activity_data"

    # Create an instance of ZeeguuApi
    api = ZeeguuApi(base_url, email, password)

    json_body = {
        "time": "2016-05-05T10:11:12",
        "event": "User Read Article",
        "value": "300s",
        "extra_data": {
            "article_source": 2
        }
    }
    number_of_threads = 1000
    # Create a barrier for 4 threads
    barrier = threading.Barrier(number_of_threads)
    
    # Shared list to store elapsed times
    elapsed_times = []
    # Lock for thread-safe access to the shared list
    lock = threading.Lock()

    # Create and start 4 threads
    threads = []
    for i in range(number_of_threads):
        thread = threading.Thread(target=thread_zeeguu, args=(api, endpoint, json_body, barrier, elapsed_times, lock))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Calculate and print the median of the elapsed times
    if elapsed_times:
        median_elapsed_time = statistics.median(elapsed_times)/1000000
        print(f"Median Elapsed Time: {median_elapsed_time} seconds")
        print(len(elapsed_times))