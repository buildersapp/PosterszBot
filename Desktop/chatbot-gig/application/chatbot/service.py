import requests
from fastapi import UploadFile
from caching import redisClient,REDIS_TTL
from dotenv import load_dotenv
import json
import os

load_dotenv()

POSTERSZ_API_KEY = os.getenv("POSTERSZ_API_KEY")
POSTERSZ_SECURITY_KEY = os.getenv("POSTERSZ_SECURITY_KEY")

async def citilytic_request(image_data:UploadFile):
    endpoint = "https://www.citilytics.net/ads/post_list/"

    image_bytes = await image_data.read()
    files = {"image": (image_data.filename, image_bytes, "image/jpeg")}

    response = requests.post(endpoint, files=files)

    return response.json()


# def postersz_post(json_data, session_id):
#     """
#     Send company data to the real Citilytic API.
#     If upload succeeds (2xx), add a note to Redis conversation history.
#     """
#     endpoint = "https://postersz.com:4003/apis/create-post-with-json"

#     headers = {
#         "Authorization": f"{POSTERSZ_API_KEY}",
#         "security_key":f"{POSTERSZ_SECURITY_KEY}"
#     }

#     redis_key = f"conversation:{session_id}"

#     # try:
#     response = requests.post(endpoint, json=json_data, headers=headers, timeout=120,verify=False)
#     print(response.status_code)
#     print(f"\ntype of json)data\n {type(json_data)}")
#     success = 200 <= response.status_code < 300
#     message = (
#             "Your post has been uploaded successfully ✅"
#             if success else
#             "Failed to upload your post ❌"
#     )

#     result = {
#         "func_name": "citilytic_api",
#         "status": response.status_code,
#         "message": message,
#         "session_id": session_id,
#         "uploaded_data": json_data,
#         }

#         # Try parse JSON response, fallback to text
#     try:
#         result["api_response"] = response.json()
#     except ValueError:
#         result["api_response"] = response.text

#         # ✅ Update Redis conversation if successful
#     if success:
#         print("\npostersz api request is successful\n")
#         cached = redisClient.get(redis_key)
#         if cached:
#             conversation_history = json.loads(cached)
#         else:
#             conversation_history = []

#         conversation_history.append({
#             "role": "system",
#             "content": "User has successfully uploaded company data."
#         })

#         redisClient.setex(redis_key, REDIS_TTL, json.dumps(conversation_history))

#     print("🔧 Postersz API Response:", result)
#     return result


def postersz_post(json_data, session_id):
    """
    Send company data to the Postersz API.
    If upload succeeds (2xx), add a note to Redis conversation history.
    """
    endpoint = "https://postersz.com:4003/apis/create-post-with-json"

    headers = {
        # "Authorization": f"{POSTERSZ_API_KEY}",
        "security_key": f"{POSTERSZ_SECURITY_KEY}"
    }

    redis_key = f"conversation:{session_id}"

    # Postersz expects form-data with key `json_data`
    payload = {
        "json_data": json.dumps(json_data)  # stringify the dict
    }

    response = requests.post(
        endpoint,
        data=payload,          # <- use form-data, not raw JSON
        headers=headers,
        timeout=120,
        verify=False
    )

    success = 200 <= response.status_code < 300
    message = (
        "Your post has been uploaded successfully "
        if success else
        "Failed to upload your post "
    )

    result = {
        "func_name": "citilytic_api",
        "status": response.status_code,
        "message": message,
        "session_id": session_id,
        "uploaded_data": json_data,
    }

    # Try parse JSON response, fallback to text
    try:
        result["api_response"] = response.json()
    except ValueError:
        result["api_response"] = response.text

    # ✅ Update Redis conversation if successful
    if success:
        cached = redisClient.get(redis_key)
        if cached:
            conversation_history = json.loads(cached)
        else:
            conversation_history = []

        conversation_history.append({
            "role": "system",
            "content": "User has successfully uploaded company data."
        })

        redisClient.setex(redis_key, REDIS_TTL, json.dumps(conversation_history))

    return result


    # except requests.RequestException as e:
    #     error_result = {
    #         "func_name": "citilytic_api",
    #         "status": 500,
    #         "message": f"Upload failed due to error: {str(e)}",
    #         "session_id": session_id,
    #         "uploaded_data": json_data
    #     }
    #     print("Postersz API Error:", error_result)
    #     return error_result