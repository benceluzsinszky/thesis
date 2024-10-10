import requests
import json
from datetime import datetime,UTC



def get_user_session(url, password):
    
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        data = {
            'password': password
        }
        response = requests.post(url, data=data, headers=headers)
        return response.json()['session']
        
   

def send_http_request(url, endpoint, session, body):
    # Send POST request with the session key as a query parameter
    response = requests.post(f"{url+endpoint}?session={session}", json=body)
    return  response.elapsed.microseconds
   

if __name__ == "__main__":
    # URL to fetch session/home/robert-sluka/Desktop/ITU/zeeguu-scalability-evaluation/app/src/main/java/org/example/ZeeguuApi.py
    email = "bluz@itu.dk"
    url = f"https://api.maxitwit.tech"
    password = "password"
    endpoint = "/upload_user_activity_data"
    session_endpoint =f"/session/{email}"


    # Get user session key
    session = get_user_session(url + session_endpoint, password)
    print(f"Session Key: {session}")
    json_body = {
            "time": "2016-05-05T10:11:12",
            "event": "User Read Article",
            "value": "300s",
            "extra_data": {
                "article_source": 2
            }
        }
    
    send_http_request(url,endpoint, session, json_body)

  
    
