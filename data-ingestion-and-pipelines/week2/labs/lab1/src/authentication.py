import json
from typing import Any, Dict

import requests


def get_token(client_id: str, client_secret: str, url: str) -> Dict[Any, Any]:
    """Allows to perform a POST request to obtain an access token 

    Args:
        client_id (str): App client id
        client_secret (str): App client secret
        url (str): URL to perform the post request

    Returns:
        Dict[Any, Any]: Dictionary containing the access token
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    try:
        response = requests.post(url=url, headers=headers, data=payload)
        response_json = json.loads(response.content)

        return response_json

    except Exception as err:
        print(f"Error: {err}")
        return {}


def get_auth_header(access_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}
