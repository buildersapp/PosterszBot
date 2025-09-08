from openai import OpenAI
from base import ResponseFormatter
import os
from dotenv import load_dotenv
from caching import redisClient,REDIS_TTL
import json
from service import postersz_post
from utils import normalize_post_payload


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

INTENT_LIST = [
    "create_post",
    "create_listing",
    "upgrade_post_to_ad",
    "resume_payment",
    "boost_ad",
    "search_inventory",
    "ask_analytics",
    "smalltalk",
    "admin_add_example",
    "admin_list_low_conf",
    "admin_retrain",
    "admin_test_query"
]

# Conversation memory
conversation_history = [
    {"role": "system", "content": "You are a Postersz Chatbot engine that help user with their request. Respond in JSON only."}
]

tools = [{
    "type": "function",
        "name": "postersz_post",
        "description": "Send a post payload to the postersz API. The payload contains information. about a company or business, such as images, company details, contacts,categories, locations, and other relevant metadata. For now, this function just prints the JSON argument.",
        "parameters": {
            "type": "object",
            "properties": {
                "json_data": {
                    "type": "string",
                    "description": "A stringified JSON object containing all the business information to be sent to the postersz API."
                },
            },
            "required": ["json_data"],
        },
},
]


def route_function_call(session_id,function_name, function_args):
    if function_name == "postersz_post":
        function = postersz_post(function_args,session_id)
        return function


def extract_intent_entities(user_text: str, session_id: str):
    """
    Uses an LLM (GPT) to extract intent and entities from user input
    and keeps track of conversation history stored in Redis.
    """

    redis_key = f"conversation:{session_id}"

    # Load history if exists
    cached = redisClient.get(redis_key)
    if cached:
        conversation_history = json.loads(cached)
    else:
        conversation_history = [
            {
                "role": "system",
                "content": (
                    "You are a Postersz Chatbot engine that helps users with their request. "
                    "Maintain conversation history and use it to recall what the user said earlier."
                )
            }
        ]

    # Add latest user message
    conversation_history.append({"role": "user", "content": user_text})

# )
    # 2. Prompt the model with tools defined
    response = client.responses.parse(
        model="gpt-4o",
        tools=tools,
        input=conversation_history,
        text_format=ResponseFormatter
    )

    needs_function_call = any(item.type == "function_call" for item in response.output)

    if needs_function_call:
        for item in response.output:
            if item.type == "function_call":
                func_name = item.name
                func_args = json.loads(item.arguments)  # parse JSON string
                # if json_data is itself stringified JSON, parse it again
                if "json_data" in func_args:
                    try:
                        func_args["json_data"] = json.loads(func_args["json_data"])
                        normalized_payload = normalize_post_payload(func_args["json_data"])

                    except json.JSONDecodeError:
                        pass  # keep as string if it’s not valid JSON


                result = route_function_call(session_id,func_name, normalized_payload)

                return {
                    "needs_function_call": True,
                    "function_name": result["func_name"],
                    "arguments": func_args,
                    "result":result,
                    "bot_message": result["message"],
                    "status_code":result["status"],
                    "session_id":result["session_id"]
                }



    # Parse structured response
    event = response.output[0].content[0].text
    event_dict = json.loads(event)
    # event_dict["intent"] = event["intent"]
    event_dict["session_id"] = session_id

    # Save assistant reply (not the raw JSON dump)
    conversation_history.append({"role": "assistant", "content": event_dict["bot_message"]})

    # Store back to Redis
    redisClient.setex(redis_key, REDIS_TTL, json.dumps(conversation_history))

    return event_dict



# api from citilytic
def get_business_data(json_data: dict, session_id: str):
    """
    Ask the user in natural language to confirm business details
    (name, phone, address) from the citilytic API response.
    Keeps history in Redis.
    """

    redis_key = f"conversation:{session_id}"

    # Load history if exists
    cached = redisClient.get(redis_key)
    if cached:
        conversation_history = json.loads(cached)
    else:
        conversation_history = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "Your job is to confirm business information with the user. "
                    "Always reply in polite, natural language. "
                    "1. Politely ask the user to confirm if each field is correct.\n"
                    "   Example: \"I have your business name as 'ABC Store', "
                    "phone number '123-456-7890', and address '123 Main Street, New York'. "
                    "Is that correct?\"\n"
                    "2. If the user says something is wrong, update ONLY that field.\n"
                    "3. There is no need to use json in this"
                ),
            }
        ]

    # Add user-like clarification to history
    conversation_history.append({"role": "user", "content": str(json_data)})

    # Call the model
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        messages=conversation_history,
    )

    bot_message = response.choices[0].message.content

    # Save updated history in Redis (5 minutes)
    conversation_history.append({"role": "assistant", "content": bot_message})
    redisClient.setex(redis_key, REDIS_TTL, json.dumps(conversation_history))
    return bot_message
