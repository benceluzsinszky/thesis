import requests
import json

def get_user_session(url, password):
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        data = {
            'password': password
        }
        response = requests.post(url, data=data, headers=headers)
        
        if response.status_code >= 200 and response.status_code < 300:
            response_json = response.json()
            session = response_json.get('session', None)
            return session
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def upload_user_activity_data(url, session, endpoint, utc_timestamp):
    try:
        json_body = {
            "time": utc_timestamp,
            "event": endpoint,
            "value": "300s",
            "extra_data": {
                "article_source": 2
            }
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        # Send POST request with the session key as a query parameter
        response = requests.post(f"{url}?session={session}", json=json_body, headers=headers)

        # Check the response code
        print(f"Response Code: {response.status_code}")

        # Print response content
        print("Response Text:", response.text)

        if response.status_code >= 200 and response.status_code < 300:
            response_json = response.json()
            print("Response JSON:", response_json)  # If the response is in JSON format

            # Extract average from response if it exists
            average = response_json.get('average', 'N/A')
            result = f"UTC Timestamp: {utc_timestamp}, Endpoint: {endpoint}, Average: {average}"
            return result
        else:
            print("Error:", response.text)
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # URL to fetch session
    url = "https://api.maxitwit.tech/session/bluz@itu.dk"
    password = "password"
    
    # Get user session key
    session = get_user_session(url, password)
    
    if session:
        # URL to upload activity data
        activity_url = "https://api.maxitwit.tech/upload_user_activity_data"
        endpoint = "User Read Article"
        utc_timestamp = "2016-05-05T10:11:12"
        result = upload_user_activity_data(activity_url, session, endpoint, utc_timestamp)
        if result:
            print(result)
    else:
        print("Failed to get session key")