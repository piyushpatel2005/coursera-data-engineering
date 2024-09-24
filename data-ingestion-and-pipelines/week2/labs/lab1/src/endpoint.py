from typing import Callable

import requests
from authentication import get_auth_header


def get_paginated_featured_playlists(
    base_url: str, access_token: str, get_token: Callable, **kwargs
) -> list:
    """Performs paginated calls to the featured playlists endpoint. Manages token refresh when required.

    Args:
        base_url (str): Base URL for API requests
        access_token (str): Access token
        get_token (Callable): Function that requests access token

    Returns:
        list: Request responses stored as a list
    """
    headers = get_auth_header(access_token=access_token)
    request_url = base_url
    featured_playlists_data = []

    try:
        while request_url:
            print(f"Requesting to: {request_url}")
            response = requests.get(url=request_url, headers=headers)

            ### Exercise 4:
            ### START CODE HERE ### (~ 11 lines of code)
            # Create an if condition over the status code of the response
            if None.status_code == 401:  # Unauthorized
                # Handle token expiration and update
                token_response = None(**None)
                if "None" in None:
                    headers = None(
                        access_token=None["None"]
                    )
                    print("Token has been refreshed")
                    continue  # Retry the request with the updated token
                else:
                    print("Failed to refresh token.")
                    return []
            ### END CODE HERE ###

            response_json = response.json()
            featured_playlists_data.extend(response_json["playlists"]["items"])
            request_url = response_json["playlists"]["next"]

        return featured_playlists_data

    except Exception as err:
        print(f"Error occurred during request: {err}")
        return []


def get_paginated_spotify_playlist(
    base_url: str,
    access_token: str,
    playlist_id: str,
    fields: str,
    get_token: Callable,
    **kwargs,
) -> list:
    """Performs paginated requests to the playlist/{playlist_id}/tracks endpoint

    Args:
        base_url (str): Base URL for endpoint requests
        access_token (str): Access token
        playlist_id (str): Id of the playlist to be queried
        fields (str): Fields to be requested for each playlist's item
        get_token (Callable): Function that requests access token

    Returns:
        list: Request responses stored as a list
    """
    ### Exercise 5:
    ### START CODE HERE ### (~ 23 lines of code)
    # Call the get_auth_header() function with the access token.
    headers = None(access_token=None)
    #  Create the requests_url by using the base_url and playlist_id parameters. At the end, you will add tracks to the URL endpoint.
    request_url = f"{None}/{None}/tracks?fields={fields}"
    playlist_data = []

    try:
        while request_url:
            print(f"Requesting to: {request_url}")
            # Perform a GET request using the request_url and headers that you created in the previous steps.
            response = None.None(url=None, headers=None)
            print(f"response {response}")

            if None.status_code == 401:  # Unauthorized
                # Handle token expiration and update.
                token_response = None(**None)
                if "None" in None:
                    # Call get_auth_header() function with the "access_token" from the token_response.
                    headers = None(
                        access_token=None["None"]
                    )
                    print("Token has been refreshed")
                    continue  # Retry the request with the updated token
                else:
                    print("Failed to refresh token.")
                    return []

            # Convert the response to json using the json() method.
            response_json = None.None()
            # Extend the playlist_data list with the value from "items" in response_json.
            playlist_data.None(None["None"])
            # Update request_url with the "next" value from response_json.
            request_url = None["None"]

        return playlist_data
    ### END CODE HERE ###

    except Exception as err:
        print(f"Error occurred during request: {err}")
        return []
