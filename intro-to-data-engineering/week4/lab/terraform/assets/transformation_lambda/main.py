import base64
import json
import logging
import os
import random
from typing import Any

import urllib3

URL_LAMBDA_INFERENCE = os.getenv(
    "URL_LAMBDA_INFERENCE",
    "",
)

ITEM_LIMIT = os.getenv(
    "ITEM_LIMIT",
    5,
)

RANDOM_SEED = os.getenv("RANDOM_SEED", 42)

random.seed(RANDOM_SEED)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def decode_record(record: bytes) -> dict:
    """Decodes the code read from kinesis data stream

    Args:
        record (bytes): Record read from kinesis data stream

    Returns:
        dict: Decoded data
    """
    string_data = base64.b64decode(record).decode("utf-8")
    return json.loads(string_data)


def get_user_embedding(
    url: str,
    data: list[dict],
) -> Any:
    """Calls the Inference lambda with user embedding endpoint to get the
    embedding for a user

    Args:
        url (str): URL for Inference Lambda
        data (list[dict]): List with users data

    Returns:
        Any: dictionary with the vector embedding of the requested user
    """

    url_call = f"{url}/user_embeddings"

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    http = urllib3.PoolManager()

    response = http.request(
        "POST",
        url_call,
        headers=headers,
        body=json.dumps(data).encode("utf-8"),
    )

    return json.loads(response.data)


def get_item_from_user(url: str, data: dict, item_limit: int) -> Any:
    """Receives an user embedding and calls the item_from_user endpoint of the inference lambda to return a list of recommended items

    Args:
        url (str): URL for Inference Lambda
        data (dict): Dictionary with user embedding vector
        item_limit (int): Maximum number of items to recommend

    Returns:
        Any: List of dictionaries with item recommendations. Format for each item is id and score.
    """

    url_call = f"{url}/items_from_user?limit={item_limit}"

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    http = urllib3.PoolManager()

    response = http.request(
        "POST",
        url_call,
        headers=headers,
        body=json.dumps(data).encode("utf-8"),
    )

    return json.loads(response.data)


def get_item_from_item(url: str, item_id: str, item_limit: int) -> Any:
    """Using an item id, recommends the most similar ones

    Args:
        url (str): URL for Inference Lambda
        data (list[dict]): _description_
        item_limit (int): _description_

    Returns:
        Any: _description_
    """

    url_call = f"{url}/items_from_item?item_id={item_id}&limit={item_limit}"

    headers = {
        "accept": "application/json",
    }

    http = urllib3.PoolManager()

    response = http.request("GET", url_call, headers=headers)

    decoded_response = json.loads(response.data)

    return decoded_response


def lambda_handler(event, context):
    logger.info(
        f"Orders Transform Handler Invoked with Records {event['records'][:2]}"
    )

    output = []
    for record in event["records"]:
        payload = decode_record(record["data"])

        usr_dict = [
            {
                "city": payload.get("city"),
                "country": payload.get("country"),
                "creditlimit": payload.get("credit_limit"),
            }
        ]

        # Getting the embedding of the user
        usr_emb = get_user_embedding(url=URL_LAMBDA_INFERENCE, data=usr_dict)

        # Recommending item for the user
        recommended_items = get_item_from_user(
            url=URL_LAMBDA_INFERENCE,
            data=usr_emb[0],
            item_limit=int(ITEM_LIMIT),
        )

        # Choosing one of the items that the user has in his history and find similar items to it to recommend
        selected_item = random.choice(payload["browse_history"])

        similar_items = get_item_from_item(
            url=URL_LAMBDA_INFERENCE,
            item_id=selected_item["product_code"],
            item_limit=int(ITEM_LIMIT),
        )

        payload["recommended_items"] = recommended_items
        payload["similar_items"] = {
            "product_code": selected_item["product_code"],
            "similar_items": similar_items,
        }

        output_record = {
            "recordId": record["recordId"],
            "result": "Ok",
            "data": base64.b64encode(json.dumps(payload).encode("utf-8")),
        }
        output.append(output_record)

    logger.info(f"Processed Records {output[:2]}")

    return {"records": output}
