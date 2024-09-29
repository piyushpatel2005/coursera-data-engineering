# Batch Data Processing from an API

In this lab, you will learn how to interact with the Spotify API and extract data from the API in a batch way. You will explore what pagination means and how to send an API request that requires authorization.

# Table of Contents

- [ 1 - Create a Spotify APP](#1)
- [ 2 - Understand the Basics of APIs](#2)
  - [ 2.1 - Get Token](#2.1)
  - [ 2.2 - Get Featured Playlists](#2.2)
    - [ Exercise 1](#ex01)
  - [ 2.3 - Pagination](#2.3)
    - [ Exercise 2](#ex02)
    - [ Exercise 3](#ex03)
  - [ 2.4 - Optional - API Rate Limits](#2.4)
- [ 3 - Batch pipeline](#3)
  - [ Exercise 4](#ex04)
  - [ Exercise 5](#ex05)
  - [ Exercise 6](#ex06)
- [ 4 - Optional - Spotipy SDK](#4)
  - [ Exercise 7](#ex07)
- [ 5 - Upload the Files for Grading](#5)

<a name='1'></a>
## 1 - Create a Spotify APP

To get access to the API resources, you need to create a Spotify account if you don't already have one. A trial account will be enough to complete this lab.

1. Go to https://developer.spotify.com/, create an account and log in.
2. Click on the account name in the right-top corner and then click on **Dashboard**.
3. Create a new APP using the following details:
   - App name: `dec2w2a1-spotify-app`
   - App description: `spotify app to test the API`
   - Website: leave empty
   - Redirect URIs: `http://localhost:3000`
   - API to use: select `Web API`
4. Click on **Save** button. If you get an error message saying that your account is not ready, you can log out, wait for a few minutes and then repeat again steps 2-4.
5. In the App Home page click on **Settings** and reveal `Client ID` and `Client secret`. Store them in the `src/env` file provided in this lab. Make sure to save the `src/env` file using `Ctrl + S` or `Cmd + S`.


Here's the link to [the Spotify API documentation](https://developer.spotify.com/documentation/web-api/tutorials/getting-started) that you can refer to while you're working on the lab's exercises. The required information to complete the tasks will be given during the lab. You will interact with two resources: 
- Featured playlists in the first and second parts ([endpoint](https://developer.spotify.com/documentation/web-api/reference/get-featured-playlists));
- Playlist items in the second part ([endpoint](https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks)).

<a name='2'></a>
## 2 - Understand the Basics of APIs

Several packages in Python allow you to request data from an API; in this lab, you will use the `requests` package, which is a popular and versatile library to perform HTTP requests. It provides a simple and easy-to-use way to interact with web services and APIs. Let's load the required packages:


```python
import os
import subprocess
from typing import Dict, Any, Callable

from dotenv import load_dotenv
import json
import requests 
```

<a name='2.1'></a>
### 2.1 - Get Token

The first step when working with an API is to understand the authentication process. For that, the Spotify APP generates a Client ID and a Client secret that you will use to generate an access token. The access token is a string that contains the credentials and permissions that you can use to access a given resource. You can find more about it in the [API documentation](https://developer.spotify.com/documentation/web-api/concepts/access-token). Since each API is developed with a particular purpose, it is necessary for you to always read and understand the nuances of each API so you can access the data responsibly. Throughout this lab, you will be provided with several links to the documentation and you are encouraged to read them. (During the lab session, you may quickly skim through the links, but you can always check them in more details after the lab session). 

Let's create some variables to hold the values of the client_id and client_secret that you stored in the src/env file.


```python
load_dotenv('./src/env', override=True)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
```

The `get_token` function below takes a Client ID, Client secret and a URL as input, and performs a POST request to that URL to obtain an access token using the client credentials. Run the following cell to get the access token.


```python
def get_token(client_id: str, client_secret: str, url: str) -> Dict[Any, Any]:
    """Allows to perform a POST request to obtain an access token 

    Args:
        client_id (str): App client id
        client_secret (str): App client secret
        url (str): URL to perform the post request

    Returns:
        Dict[Any, Any]: Dictionary containing the access token
    """
        
    headers = {        
        "Content-Type": "application/x-www-form-urlencoded"            
    }
    
    payload = {
                "grant_type": "client_credentials", 
                "client_id": client_id, 
                "client_secret": client_secret
               }
    
    try: 
        response = requests.post(url=url, headers=headers, data=payload)
        print(type(response))
        response.raise_for_status()
        response_json = json.loads(response.content)
        
        return response_json
        
    except Exception as err:
        print(f"Error: {err}")
        return {}

URL_TOKEN="https://accounts.spotify.com/api/token"
token = get_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, url=URL_TOKEN)

print(token)
```

    <class 'requests.models.Response'>
    {'access_token': 'BQC8OTyzbp9MncZMNB23SKrLkD-c5GxEZu1P1AKqkQV9iWiQ1WaKVeOxOuj-yPiPKUv5qNPjBxnydgz6WySnQ4xoYMMtx29W7pCVMkR_cAp_gT5Ples', 'token_type': 'Bearer', 'expires_in': 3600}


You can see that you are provided with a temporary access token. The `expires_in` field tells you the duration of this token in seconds. When this token expires, your requests will fail and an error object will be returned to you holding a status code of 401. This status code means that the request is unauthorized.

Whenever you send an API request to the spotify API, you need to include in the request the access token, as an authorization header following a certain format. You are provided with the function `get_auth_header`. This function expects the access token and returns the authorization header that can be included in the API request. 

Make sure to run the following cell to declare the function `get_auth_header`, which you will use throughout this lab.


```python
def get_auth_header(access_token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}
```

Now, let's use the token to perform a request to access the first resource, which is the [featured playlists](https://developer.spotify.com/documentation/web-api/reference/get-featured-playlists).

<a name='2.2'></a>
### 2.2 - Get Featured Playlists

<a name='ex01'></a>
### Exercise 1

Follow the instructions to complete the `get_featured_playlists` function:

1. Call the function `get_auth_header`and pass to it the access token (which is specified as input to the `get_featured_playlists` function). Save the output of `get_auth_header` to a variable called `headers`.
2. You are provided with the URL in the `request_url` variable. Use this URL and the header from the previous step to perform a `get()` request. 
3. Request `response` is an object of type `requests.models.Response`. This object has a method named `json()` that allows you to transform the response content into a JSON object or plain Python dictionary. Use this method on the `response` object to return the content as a Python dictionary.

Then you will use the provided `URL_FEATURE_PLAYLISTS` URL or endpoint to perform calls to the API, passing the `access_token` value from the `token` object that you obtained before.


```python
def get_featured_playlists(url: str, access_token: str, offset: int=0, limit: int=20, next: str="") -> Dict[Any, Any]:
    """Perform get() request to featured playlists endpoint

    Args:
        url (str): Base url for the request
        access_token (str): Access token
        offset (int, optional): Page offset for pagination. Defaults to 0.
        limit (int, optional): Number of elements per page. Defaults to 20.
        next (str, optional): Next URL to perform next request. Defaults to "".

    Returns:
        Dict[Any, Any]: Request response
    """

    if next == "":        
        request_url = f"{url}?offset={offset}&limit={limit}"
    else: 
        request_url = f"{next}"

    ### START CODE HERE ### (~ 4 lines of code)
    # Call get_auth_header() function and pass the access token.
    headers = get_auth_header(access_token=access_token)
    
    try: 
        # Perform a get() request using the request_url and headers.
        response = requests.get(url=request_url, headers=headers)
        # Use json() method over the response to return it as Python dictionary.
        return response.json()
    ### END CODE HERE ###
    
    except Exception as err:
        print(f"Error requesting data: {err}")
        return {'error': err}
        
URL_FEATURE_PLAYLISTS = "https://api.spotify.com/v1/browse/featured-playlists"

# Note: the `access_token` value from the dictionary `token` can be retrieved either using `get()` method or dictionary syntax `token['access_token']`
playlists_response = get_featured_playlists(url=URL_FEATURE_PLAYLISTS, access_token=token.get('access_token'))
playlists_response
```




    {'message': 'Popular Playlists',
     'playlists': {'href': 'https://api.spotify.com/v1/browse/featured-playlists?offset=0&limit=20',
      'items': [{'collaborative': False,
        'description': 'The hottest 50. Cover: Tate McRae',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M',
        'id': '37i9dQZF1DXcBWIGoYBM5M',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000029d98b94f343cd13002dedb9b',
          'width': None}],
        'name': 'Today’s Top Hits',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAADhqQafWE+qj88gO0gfJcje',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DXcBWIGoYBM5M'},
       {'collaborative': False,
        'description': "Today's top country hits. Cover: Keith Urban",
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX1lVhptIYRda'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX1lVhptIYRda',
        'id': '37i9dQZF1DX1lVhptIYRda',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000021d653e6a53115413b2ffc5d4',
          'width': None}],
        'name': 'Hot Country',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFC864',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAAAwyHLTutcLwmNj++EmbDFK',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX1lVhptIYRda/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX1lVhptIYRda'},
       {'collaborative': False,
        'description': 'New music from Future, Lil Tecca and GloRilla. ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX0XUsuxWHRQd',
        'id': '37i9dQZF1DX0XUsuxWHRQd',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002e9367d2bc3e15cee50708ec2',
          'width': None}],
        'name': 'RapCaviar',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#F49B23',
        'public': True,
        'snapshot_id': 'ZvHBuQAAAAC3z5zpc8qNG3+6PvhFxEAZ',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX0XUsuxWHRQd/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX0XUsuxWHRQd'},
       {'collaborative': False,
        'description': 'The essential tracks, all in one playlist.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX5KpP2LN299J'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX5KpP2LN299J',
        'id': '37i9dQZF1DX5KpP2LN299J',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f0000000252feef11af8c9d412769ec5a',
          'width': None}],
        'name': 'This Is Taylor Swift',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'ZqsIQAAAAADe3rfnkTpKF5/AovrNituQ',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX5KpP2LN299J/tracks',
         'total': 180},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX5KpP2LN299J'},
       {'collaborative': False,
        'description': "Today's top Latin hits, elevando nuestra música. Cover: Bad Bunny",
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX10zKzsJ2jva'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX10zKzsJ2jva',
        'id': '37i9dQZF1DX10zKzsJ2jva',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002c1f07388b99b45312ad8e6c9',
          'width': None}],
        'name': 'Viva Latino',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'Zuy7AAAAAAA1G9tXanO/u5MOBpDKz0C3',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX10zKzsJ2jva/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX10zKzsJ2jva'},
       {'collaborative': False,
        'description': 'All your favorite Disney hits, including classics from Encanto, Descendants, Moana, Frozen, & The Lion King.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX8C9xQcOrE6T'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX8C9xQcOrE6T',
        'id': '37i9dQZF1DX8C9xQcOrE6T',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000027bdaa8658900f615ec212e73',
          'width': None}],
        'name': 'Disney Hits',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZtFisAAAAABujgn+PJrITkqN+3g2ATKU',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX8C9xQcOrE6T/tracks',
         'total': 111},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX8C9xQcOrE6T'},
       {'collaborative': False,
        'description': 'Gentle Ambient piano to help you fall asleep. ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWZd79rJ6a7lp'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZd79rJ6a7lp',
        'id': '37i9dQZF1DWZd79rJ6a7lp',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002cd17d41419faa97069e06c16',
          'width': None}],
        'name': 'Sleep',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'Zt63/gAAAAAn9oDfil6AhraaIoVjzapY',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZd79rJ6a7lp/tracks',
         'total': 183},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWZd79rJ6a7lp'},
       {'collaborative': False,
        'description': 'New music from Future, Bad Bunny, Bon Iver, Katy Perry, GloRilla, and more!',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX4JAvHpjipBk'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX4JAvHpjipBk',
        'id': '37i9dQZF1DX4JAvHpjipBk',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002cb4876c76b840ff5d773ea5e',
          'width': None}],
        'name': 'New Music Friday',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAABeoXK67XGjky+Sl/e2ZJAR',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX4JAvHpjipBk/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX4JAvHpjipBk'},
       {'collaborative': False,
        'description': 'Ten hours long continuous white noise to help you relax and let go. ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWUZ5bk6qqDSy'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWUZ5bk6qqDSy',
        'id': '37i9dQZF1DWUZ5bk6qqDSy',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000025b4d326fee8531fe32efe166',
          'width': None}],
        'name': 'White Noise 10 Hours',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZqnuAAAAAADY7kNw/2LeeKmMLVe9MAvu',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWUZ5bk6qqDSy/tracks',
         'total': 230},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWUZ5bk6qqDSy'},
       {'collaborative': False,
        'description': 'The hottest tracks in the United States. Cover: Sabrina Carpenter',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX0kbJZpiYdZl'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX0kbJZpiYdZl',
        'id': '37i9dQZF1DX0kbJZpiYdZl',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002c853cf0c309b398aa04e634f',
          'width': None}],
        'name': 'Hot Hits USA',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAACNQVLjaktGmI/aMGhyGCvH',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX0kbJZpiYdZl/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX0kbJZpiYdZl'},
       {'collaborative': False,
        'description': 'Fourth quarter, two minutes left .. get locked in. Cover: Derrick Henry\n\n',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWTl4y3vgJOXW'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWTl4y3vgJOXW',
        'id': '37i9dQZF1DWTl4y3vgJOXW',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000027e645f7152aeac420b004512',
          'width': None}],
        'name': 'Locked In',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZvCi7wAAAAD1fQMtiF0Hci+pZchnTRB1',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWTl4y3vgJOXW/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWTl4y3vgJOXW'},
       {'collaborative': False,
        'description': 'autumn leaves falling down like pieces into place',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXahsxs9xh0fn'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXahsxs9xh0fn',
        'id': '37i9dQZF1DXahsxs9xh0fn',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002dcbea5e236f33008e73e3192',
          'width': None}],
        'name': 'fall feels',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZvHr6gAAAAD+AQKtIzuRvvQHyWj3hBh3',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXahsxs9xh0fn/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DXahsxs9xh0fn'},
       {'collaborative': False,
        'description': 'Peaceful piano to help you slow down, breathe, and relax. ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX4sWSpwq3LiO',
        'id': '37i9dQZF1DX4sWSpwq3LiO',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f0000000283da657fca565320e9311863',
          'width': None}],
        'name': 'Peaceful Piano',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZvF9/gAAAADPtdPFmSIXjwqmwmrlZWia',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX4sWSpwq3LiO/tracks',
         'total': 204},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX4sWSpwq3LiO'},
       {'collaborative': False,
        'description': 'This is Zach Bryan. The essential tracks, all in one playlist.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DZ06evO2llutr'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO2llutr',
        'id': '37i9dQZF1DZ06evO2llutr',
        'images': [{'height': None,
          'url': 'https://thisis-images.spotifycdn.com/37i9dQZF1DZ06evO2llutr-default.jpg',
          'width': None}],
        'name': 'This Is Zach Bryan',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': None,
        'public': True,
        'snapshot_id': 'ZvCvgAAAAAABIKaVr5aychkT8PMgH5vu',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO2llutr/tracks',
         'total': 43},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DZ06evO2llutr'},
       {'collaborative': False,
        'description': 'Soft instrumental Jazz for all your activities.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWV7EzJMK2FUI'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWV7EzJMK2FUI',
        'id': '37i9dQZF1DWV7EzJMK2FUI',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002472120b92edea982b5feb264',
          'width': None}],
        'name': 'Jazz in the Background',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuybGQAAAACn9xZrkMigk0LIjSHPmFLF',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWV7EzJMK2FUI/tracks',
         'total': 786},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWV7EzJMK2FUI'},
       {'collaborative': False,
        'description': 'Keep calm and focus with ambient and post-rock music.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZeKCadgRdKQ',
        'id': '37i9dQZF1DWZeKCadgRdKQ',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000026020f2f6476db518ef747da4',
          'width': None}],
        'name': 'Deep Focus',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuqOmgAAAABj4oPfIm8TJ635GGeoRo7Y',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZeKCadgRdKQ/tracks',
         'total': 162},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWZeKCadgRdKQ'},
       {'collaborative': False,
        'description': 'the beat of your drift',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWWY64wDtewQt'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWY64wDtewQt',
        'id': '37i9dQZF1DWWY64wDtewQt',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000027dc5028b26eb62f22d31bb1f',
          'width': None}],
        'name': 'phonk',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'Zu2O8AAAAABj9nRkASfiLYEB8aMyMY0m',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWY64wDtewQt/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWWY64wDtewQt'},
       {'collaborative': False,
        'description': "Country music's 50 most played songs in the world. Updated weekly. Cover: Post Malone and Morgan Wallen",
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX7aUUBCKwo4Y'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX7aUUBCKwo4Y',
        'id': '37i9dQZF1DX7aUUBCKwo4Y',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000025b07a04dce2d3bdf7b3352e5',
          'width': None}],
        'name': 'Country Top 50',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZusjpgAAAAA4sW9Te9EmTxqVgw76UHJW',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX7aUUBCKwo4Y/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX7aUUBCKwo4Y'},
       {'collaborative': False,
        'description': 'chill beats, lofi vibes, new tracks every week... ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWQRwui0ExPn',
        'id': '37i9dQZF1DWWQRwui0ExPn',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f0000000255be59b7be2929112e7ac927',
          'width': None}],
        'name': 'lofi beats',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAACI+zl4dWMXp+qQ/dUIjDhK',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWQRwui0ExPn/tracks',
         'total': 750},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWWQRwui0ExPn'},
       {'collaborative': False,
        'description': '¡Las más placosas y llegadoras de nuestra música! Al millón con Grupo Firme, Hernan Sepulveda.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX905zIRtblN3'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX905zIRtblN3',
        'id': '37i9dQZF1DX905zIRtblN3',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000028169dfcd53c5fa947ac80bc2',
          'width': None}],
        'name': 'La Reina: Éxitos de la Música Mexicana',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'Zuz1+QAAAAA4i7k9OW/f8fb2zIHZiZfz',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX905zIRtblN3/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX905zIRtblN3'}],
      'limit': 20,
      'next': 'https://api.spotify.com/v1/browse/featured-playlists?offset=20&limit=20',
      'offset': 0,
      'previous': None,
      'total': 100}}



The result you get is a JSON object that was transformed into a python dictionary. You can explore the structure of the response you get:


```python
playlists_response.keys()
```




    dict_keys(['message', 'playlists'])




```python
playlists_response.get('playlists').keys()
```




    dict_keys(['href', 'items', 'limit', 'next', 'offset', 'previous', 'total'])



Each API manages responses in its own way so it is highly recommended to read the documentation and understand the nuances behind the API endpoints you are working with. In this case, you see some fields such as `'href'` under the `'playlists'` field, which tells you the URL used for the request you just sent.


```python
playlists_response.get('playlists').get('href')
```




    'https://api.spotify.com/v1/browse/featured-playlists?offset=0&limit=20'



You can see that there are two parameters: `offset` and `limit` that were added to the endpoint. Those parameters are the base of pagination in this API endpoint. We will take a look at them later. 

You can also explore the returned items using the `'items'` field under `'playlists'`. This will return a list of items, you can take a look at the number of items returned:


```python
len(playlists_response.get('playlists').get('items'))
```




    20



Explore the items:


```python
playlists_response.get('playlists').get('items')[0]
```




    {'collaborative': False,
     'description': 'The hottest 50. Cover: Tate McRae',
     'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M'},
     'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M',
     'id': '37i9dQZF1DXcBWIGoYBM5M',
     'images': [{'height': None,
       'url': 'https://i.scdn.co/image/ab67706f000000029d98b94f343cd13002dedb9b',
       'width': None}],
     'name': 'Today’s Top Hits',
     'owner': {'display_name': 'Spotify',
      'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
      'href': 'https://api.spotify.com/v1/users/spotify',
      'id': 'spotify',
      'type': 'user',
      'uri': 'spotify:user:spotify'},
     'primary_color': '#FFFFFF',
     'public': True,
     'snapshot_id': 'ZuzzQAAAAADhqQafWE+qj88gO0gfJcje',
     'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks',
      'total': 50},
     'type': 'playlist',
     'uri': 'spotify:playlist:37i9dQZF1DXcBWIGoYBM5M'}



<a name='2.3'></a>
### 2.3 - Pagination

At the end of `playlists_response`, you can see the following fields:

```json
{
...,
'limit': 20,
'next': 'https://api.spotify.com/v1/browse/featured-playlists?offset=20&limit=20',
'offset': 0,
'previous': None,
'total': 100
}
```

Although there is a total of 100 available items to be returned, only 20 were returned. This is established by the `limit` parameter and those were the 20 items you just counted before. This limit on the number of elements returned is a common feature of several APIs and although in some cases you can modify such a limit, a good practice is to use it with **pagination** to get all the elements that can be returned. 

Each API handles pagination differently. For Spotify, the requests response provides you with two fields that allowa you to query the different pages of your request: `previous` and `next`. These two fields will return the URL to the previous or next page respectively and they are based on the `offset` and `limit` parameters. In this case, there are two ways for you to explore the rest of the data:

- you can use the value from the next parameter to get the direct URL for the next page of requests, or 
- you can build the URL for the next page from scratch using the offset and limit parameters (make sure to update the offset parameter for the request). 

For the sake of learning, you will use method 2 to build the URL yourself. Then you will also compare it with the result from using the first method just to check that you created the URL correctly.

Before creating a function that will allow you to paginate, let's try to do it manually. If you compare the URLs provided by the `href` and `next` fields, you can see that while the `limit` parameter remains the same, the `offset` parameter has increased with the same value as the one stored in `limit`.

```json
{
...,
'href': 'https://api.spotify.com/v1/browse/featured-playlists?offset=0&limit=20',
...,
'next': 'https://api.spotify.com/v1/browse/featured-playlists?offset=20&limit=20',
...
}
```

So for our next call, let's pass 20 to `offset` and keep `limit` as 20:


```python
next_playlists_response = get_featured_playlists(url=URL_FEATURE_PLAYLISTS, access_token=token.get('access_token'), offset=20, limit=20)
```

Check the values for `href` and `next` in the new response `next_playlists_response`:


```python
next_playlists_response.get('playlists').get('href')
```




    'https://api.spotify.com/v1/browse/featured-playlists?offset=20&limit=20'




```python
next_playlists_response.get('playlists').get('next')
```




    'https://api.spotify.com/v1/browse/featured-playlists?offset=40&limit=20'



Given these results, you can see that the `offset` increases by the value of the `limit`. As the responses show that the `total` value is 100, this means that you can access the last page of responses by using an `offset` of 80, while keeping the `limit` value as 20.


```python
last_playlists_response = get_featured_playlists(url=URL_FEATURE_PLAYLISTS, access_token=token.get('access_token'), offset=80, limit=20)
last_playlists_response
```




    {'message': 'Popular Playlists',
     'playlists': {'href': 'https://api.spotify.com/v1/browse/featured-playlists?offset=80&limit=20',
      'items': [{'collaborative': False,
        'description': 'Warm familiar pop you know and love. Cover: Adele',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWTwnEm1IYyoj'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWTwnEm1IYyoj',
        'id': '37i9dQZF1DWTwnEm1IYyoj',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f0000000242ede53dcaaa172b7bbca101',
          'width': None}],
        'name': 'Soft Pop Hits',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'Zro8rAAAAABPfltrodaQ+UJpJ9wj0oAm',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWTwnEm1IYyoj/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWTwnEm1IYyoj'},
       {'collaborative': False,
        'description': 'The essential tracks from The Weeknd.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX6bnzK9KPvrz'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX6bnzK9KPvrz',
        'id': '37i9dQZF1DX6bnzK9KPvrz',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002256e5fd2d2b6df5b9e98ac4e',
          'width': None}],
        'name': 'This Is The Weeknd',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'ZuO5OAAAAAB1l6nimeaxKyjOiWJGRVXt',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX6bnzK9KPvrz/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX6bnzK9KPvrz'},
       {'collaborative': False,
        'description': 'resurging tracks coming in hot. cover: Bruno Mars in his "When I Was Your Man" era ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWYPhtvsbr1Fn'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWYPhtvsbr1Fn',
        'id': '37i9dQZF1DWYPhtvsbr1Fn',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000027c11da732cb9978fd27b43d8',
          'width': None}],
        'name': 'reheat',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'Ztp+QAAAAACGBKPPtdLMME03pjGd6+ww',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWYPhtvsbr1Fn/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWYPhtvsbr1Fn'},
       {'collaborative': False,
        'description': 'This is Hozier. The essential tracks, all in one playlist.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DZ06evO1xnOx2'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO1xnOx2',
        'id': '37i9dQZF1DZ06evO1xnOx2',
        'images': [{'height': None,
          'url': 'https://thisis-images.spotifycdn.com/37i9dQZF1DZ06evO1xnOx2-default.jpg',
          'width': None}],
        'name': 'This Is Hozier',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': None,
        'public': True,
        'snapshot_id': 'ZvCvgAAAAAA7Px4zcExsy95jk30HjzTU',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO1xnOx2/tracks',
         'total': 38},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DZ06evO1xnOx2'},
       {'collaborative': False,
        'description': 'The best tunes in Jazz history. Cover: Wayne Shorter',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXbITWG1ZJKYt'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXbITWG1ZJKYt',
        'id': '37i9dQZF1DXbITWG1ZJKYt',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002d6717501a3dc7fdef7aa1694',
          'width': None}],
        'name': 'Jazz Classics',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZpepPgAAAACQTqD8QnlVEY8PgBFeVd9g',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXbITWG1ZJKYt/tracks',
         'total': 250},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DXbITWG1ZJKYt'},
       {'collaborative': False,
        'description': 'This is Bruno Mars. The essential tracks, all in one playlist.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DZ06evO03DwPK'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO03DwPK',
        'id': '37i9dQZF1DZ06evO03DwPK',
        'images': [{'height': None,
          'url': 'https://thisis-images.spotifycdn.com/37i9dQZF1DZ06evO03DwPK-default.jpg',
          'width': None}],
        'name': 'This Is Bruno Mars',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': None,
        'public': True,
        'snapshot_id': 'ZvCvgAAAAADNKcUZUcz8JcEHbAA5Mofi',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO03DwPK/tracks',
         'total': 43},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DZ06evO03DwPK'},
       {'collaborative': False,
        'description': "Who's now and next in pop. Cover: Bryant Barnes & d4vd",
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWUa8ZRTfalHk'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWUa8ZRTfalHk',
        'id': '37i9dQZF1DWUa8ZRTfalHk',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002e665431c28f5dc4594dfca37',
          'width': None}],
        'name': 'Pop Rising',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'Zuz0WgAAAADjm8ChyJvb7qS/M+OzV5Ev',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWUa8ZRTfalHk/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWUa8ZRTfalHk'},
       {'collaborative': False,
        'description': "A selection of the greatest classical tunes; the perfect starting point for anyone who's keen to explore the world of classical music.",
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWWEJlAGA9gs0'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWEJlAGA9gs0',
        'id': '37i9dQZF1DWWEJlAGA9gs0',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002762f5045eac92a372596acca',
          'width': None}],
        'name': 'Classical Essentials',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuskNAAAAABsIFqomwZnf8yZAlxf8Jqd',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWEJlAGA9gs0/tracks',
         'total': 182},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWWEJlAGA9gs0'},
       {'collaborative': False,
        'description': 'I would be complex. I would be cool.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXbdNhlZLjJXz'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXbdNhlZLjJXz',
        'id': '37i9dQZF1DXbdNhlZLjJXz',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002149e4a90c39cf1578fead99f',
          'width': None}],
        'name': 'hot girl walk',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAACZR1693ceJ9jJ+w5xg+Nce',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXbdNhlZLjJXz/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DXbdNhlZLjJXz'},
       {'collaborative': False,
        'description': 'Gentle instrumental covers of known songs.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX9j444F9NCBa'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX9j444F9NCBa',
        'id': '37i9dQZF1DX9j444F9NCBa',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f0000000208720d9f1080f4cfa16613d0',
          'width': None}],
        'name': 'Calming Instrumental Covers',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuPv7AAAAABIQD8I5EE3obd1KXOPXjA0',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX9j444F9NCBa/tracks',
         'total': 296},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX9j444F9NCBa'},
       {'collaborative': False,
        'description': 'Mood: Turnt Cover: Drake',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWY4xHQp97fN6'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWY4xHQp97fN6',
        'id': '37i9dQZF1DWY4xHQp97fN6',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002ab56a3437f661f1fa47a24a3',
          'width': None}],
        'name': 'Get Turnt',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#F49B23',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAADtjf7PZ8GTRZiUEU9yGXrk',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWY4xHQp97fN6/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWY4xHQp97fN6'},
       {'collaborative': False,
        'description': 'This is Kendrick Lamar. The essential tracks, all in one playlist.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DZ06evO1IPOOk'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO1IPOOk',
        'id': '37i9dQZF1DZ06evO1IPOOk',
        'images': [{'height': None,
          'url': 'https://thisis-images.spotifycdn.com/37i9dQZF1DZ06evO1IPOOk-default.jpg',
          'width': None}],
        'name': 'This Is Kendrick Lamar',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': None,
        'public': True,
        'snapshot_id': 'ZvCvgAAAAAAV04XhsfVD0rUCL8MRgDTd',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO1IPOOk/tracks',
         'total': 51},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DZ06evO1IPOOk'},
       {'collaborative': False,
        'description': 'Simply rain ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX8ymr6UES7vc'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX8ymr6UES7vc',
        'id': '37i9dQZF1DX8ymr6UES7vc',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002eaf2ff074e8e4db414e0f686',
          'width': None}],
        'name': 'Rain Sounds',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZpaIDwAAAADglcNCD8SAfkCn+tpLmJbP',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX8ymr6UES7vc/tracks',
         'total': 302},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX8ymr6UES7vc'},
       {'collaborative': False,
        'description': 'The perfect frequency for sleep or study – science tested, listener approved.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWZhzMp90Opmn'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZhzMp90Opmn',
        'id': '37i9dQZF1DWZhzMp90Opmn',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002dfbcf767233afdd2496900f5',
          'width': None}],
        'name': 'Pink Noise 10 Hours',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'Zr3AgAAAAABElX8FIIUU6/AskbC3ktw2',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZhzMp90Opmn/tracks',
         'total': 196},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWZhzMp90Opmn'},
       {'collaborative': False,
        'description': 'This is Jelly Roll. The essential tracks, all in one playlist.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DZ06evO0Crktg'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO0Crktg',
        'id': '37i9dQZF1DZ06evO0Crktg',
        'images': [{'height': None,
          'url': 'https://thisis-images.spotifycdn.com/37i9dQZF1DZ06evO0Crktg-default.jpg',
          'width': None}],
        'name': 'This Is Jelly Roll',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': None,
        'public': True,
        'snapshot_id': 'ZvCvgAAAAAAbF+lTZu8sgjriwgX4A5WH',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO0Crktg/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DZ06evO0Crktg'},
       {'collaborative': False,
        'description': 'These songs rocked the 00s. Cover: Linkin Park',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX3oM43CtKnRV'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX3oM43CtKnRV',
        'id': '37i9dQZF1DX3oM43CtKnRV',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002051df99763937e296c9fddf3',
          'width': None}],
        'name': '00s Rock Anthems',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZucWiQAAAACycslstfOXWwxIuPGwrClp',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX3oM43CtKnRV/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX3oM43CtKnRV'},
       {'collaborative': False,
        'description': 'Calming green frequencies and nature sounds to help you relax and sleep.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWZ8HCIPoGGKp'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZ8HCIPoGGKp',
        'id': '37i9dQZF1DWZ8HCIPoGGKp',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f0000000287b6719666115fc028c5f5ac',
          'width': None}],
        'name': 'Green Noise',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'Zr2/DAAAAAAS+VVXVOZT2OIhTy2oE+6A',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZ8HCIPoGGKp/tracks',
         'total': 201},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWZ8HCIPoGGKp'},
       {'collaborative': False,
        'description': 'Press play, press start.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWTyiBJ6yEqeu'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWTyiBJ6yEqeu',
        'id': '37i9dQZF1DWTyiBJ6yEqeu',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002f8b3113ff97bf94e7c8f6354',
          'width': None}],
        'name': 'Top Gaming Tracks',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuMRYAAAAAAhbyGvzubvE0dQibz4B5hU',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWTyiBJ6yEqeu/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWTyiBJ6yEqeu'},
       {'collaborative': False,
        'description': 'Crossing over like Allen I. Cover: Don Toliver',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX2A29LI7xHn1'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX2A29LI7xHn1',
        'id': '37i9dQZF1DX2A29LI7xHn1',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002111395a806454f2d7881872b',
          'width': None}],
        'name': 'Signed XOXO',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#F49B23',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAACW9fgNvncxm6Mc8a+pwIil',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX2A29LI7xHn1/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX2A29LI7xHn1'},
       {'collaborative': False,
        'description': 'Everyone deserves a happy ending. Listen to the music from the Deadpool series, including Deadpool & Wolverine, now playing in theaters. ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX5WkSQEMTURo'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX5WkSQEMTURo',
        'id': '37i9dQZF1DX5WkSQEMTURo',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000021ec255fdd0522947aceb1781',
          'width': None}],
        'name': 'Deadpool Official Playlist',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZrueqgAAAADxvoIC66KFylWDasP35RcH',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX5WkSQEMTURo/tracks',
         'total': 76},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX5WkSQEMTURo'}],
      'limit': 20,
      'next': None,
      'offset': 80,
      'previous': 'https://api.spotify.com/v1/browse/featured-playlists?offset=60&limit=20',
      'total': 100}}



You can see that the value of the `next` field is `None`, indicating that you reached the last page. On the other hand, you can see that `previous` contains the URL to request the data from the previous page, so you can even go backward if required.

<a name='ex02'></a>
### Exercise 2

Follow the instructions to create a new function that will handle pagination, based on the `get_featured_playlists` function:

1. Check the function definition, you have to provide a callable (`endpoint_request`) that corresponds to the function that performs the API call to get the featured playlists.
2. Before the `while` loop, create a dictionary named `kwargs` with the following keys:
    * `'url'`: the URL to perform the call passed to the function as a parameter.
    * `'access_token'`: the access token passed to the function as a parameter. 
    * `'offset'`: page's offset for the paginated request.
    * `'limit'`: maximum number of elements in the page's request.
3. Call the `endpoint_request()` function with the keyword arguments that you specified in the `kwargs` dictionary. Assign it to `response`.
4. Extend the `responses` list with the playlist's `items` from the `response`.
5. Create a variable `total_elements` that hosts the total number of elements from the  `response`. Remember that the `response` has a field named `'playlists'` that has the `'total'` number of elements. If you have any doubt about the response structure, remember to see the [documentation](https://developer.spotify.com/documentation/web-api/reference/get-featured-playlists).
6. In the `while` loop, set the stop condition as when the `offset` value is smaller than the `total_elements` variable you defined before.
7. Inside the `while` loop do the following steps: 
   * Update the `offset` value with the current value from the request you did plus the `limit` value.
   * Repeat the definition of the `kwargs` dictionary with the same parameters. Note that in this case the `offset` value has been updated.
   * Repeat steps 3 and 4.
  


```python
def paginated_featured_playlists(endpoint_request: Callable, url: str, access_token: str, offset: int=0, limit: int=20) -> list:
    """Allows to perform pagination over and API request done by the endpoint_request function

    Args:
        endpoint_request (Callable): Function that performs the API Calls
        url (str): Endpoint's URL for the request
        access_token (str): Access token
        offset (int, optional): Offset of the page's request. Defaults to 0.
        limit (int, optional): Limit of the page's request. Defaults to 20.

    Returns:
        list: List with the requested items
    """
    
    responses = []
    
    ### START CODE HERE ### (~ 19 lines of code)
    # Create a dictionary named kwargs with the values corresponding to the keys url, token, offset, limit
    kwargs = {         
            "url": url,
            "access_token": access_token,
            "offset": offset,
            "limit": limit,
        } 
    
    # Call the endpoint_request() function with the arguments specified in the kwargs dictionary.
    response = endpoint_request(**kwargs)
    # Use extend() method to add the playlist's items to the list of responses.
    responses.extend(response.get('playlists').get('items'))
    # Get the total number of the elements in playlist and save it in the variable total_elements.
    total_elements = response.get('playlists').get('total')

    # Run the loop as long as the offset value is smaller than total_elements.
    while offset < total_elements:
        # Update the offset value with the current value from the request you did plus the limit value.
        offset = response.get('playlists').get('offset') + limit

        # Repeat the definition of the kwargs dictionary with the same parameters (with the new offset value).
        kwargs = {             
            "url": url,
            "access_token": access_token,
            "offset": offset,
            "limit": limit,
        }         
        # Call the endpoint_request() function with the arguments specified in the kwargs dictionary.
        response = endpoint_request(**kwargs)
         # Use extend() method to add the playlist's items to the list of responses.
        responses.extend(response.get('playlists').get('items'))
    ### END CODE HERE ###
        
        print(f"Finished iteration for page with offset: {offset-limit}")

    return responses
```

Now, execute the paginated_featured_playlists with the function `get_featured_playlists` as the `endpoint_request` callable parameter. Use the same URL used in the previous `get_featured_playlists` call, as well as the access token. Set the initial `offset` as 0. For the limit, the default value is 20 but you can play with other values if you want.


```python
responses = paginated_featured_playlists(endpoint_request=get_featured_playlists, url=URL_FEATURE_PLAYLISTS, access_token=token.get('access_token'), offset=0, limit=20)
```

    Finished iteration for page with offset: 0
    Finished iteration for page with offset: 20
    Finished iteration for page with offset: 40
    Finished iteration for page with offset: 60
    Finished iteration for page with offset: 80


Have a look at one of the item:


```python
responses[0]
```




    {'collaborative': False,
     'description': 'The hottest 50. Cover: Tate McRae',
     'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M'},
     'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M',
     'id': '37i9dQZF1DXcBWIGoYBM5M',
     'images': [{'height': None,
       'url': 'https://i.scdn.co/image/ab67706f000000029d98b94f343cd13002dedb9b',
       'width': None}],
     'name': 'Today’s Top Hits',
     'owner': {'display_name': 'Spotify',
      'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
      'href': 'https://api.spotify.com/v1/users/spotify',
      'id': 'spotify',
      'type': 'user',
      'uri': 'spotify:user:spotify'},
     'primary_color': '#FFFFFF',
     'public': True,
     'snapshot_id': 'ZuzzQAAAAADhqQafWE+qj88gO0gfJcje',
     'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks',
      'total': 50},
     'type': 'playlist',
     'uri': 'spotify:playlist:37i9dQZF1DXcBWIGoYBM5M'}



You can check the `responses` variable to see if all the elements were downloaded successfully.


```python
len(responses)
```




    100



With the `paginated_featured_playlists` function that you created, you are now able to get all 100 available items.

<a name='ex03'></a>
### Exercise 3

The function `get_featured_playlists` can handle pagination by passing the `offset` and `limit` parameters or only using the `next` parameter. Create another function that uses the `next` parameter to perform the pagination and compare your results from the previous exercise. Follow the instructions below:

The dictionary `kwargs` is now defined with the following keys:
- `'url'`: the URL to perform the call passed to the function as a parameter.
- `'access_token'`: the access token passed to the function as a parameter. 
- `'next'`: the URL to generate the next request, defined as an empty string for the first call.

Inside the `while` loop:
1. Call the `endpoint_request()` function with the keyword arguments that you specified in the `kwargs` dictionary. Assign it to `response`.
2. Extend the `responses` list with the playlist's `items` from the `response`.
3. Reassign the value of `next_page` as the `'next'` value from the `response["playlists"]` dictionary.  If you have any doubt about the response structure, remember to see the [documentation](https://developer.spotify.com/documentation/web-api/reference/get-featured-playlists).
4. Update the `kwargs` dictionary: set the value of the key `'next'` as the variable `next_page`.


```python
def paginated_with_next_featured_playlists(endpoint_request: Callable, url: str, access_token: str) -> list:
    """Manages pagination for API requests done with the endpoint_request callable

    Args:
        endpoint_request (Callable): Function that performs API request
        url (str): Base URL for the request
        access_token (str): Access token

    Returns:
        list: Responses stored in a list
    """
    responses = []
        
    next_page = url
    
    kwargs = {
            "url": url,
            "access_token": access_token,
            "next": ""
        }
    
    while next_page:
        
        ### START CODE HERE ### (~ 4 lines of code)
        # Call the endpoint_request() function with the arguments specified in the kwargs dictionary.
        response = endpoint_request(**kwargs)
        # Use extend() method to add the playlist's items to the list of responses.
        responses.extend(response.get('playlists').get('items'))
        # Reassign the value of next_page as the 'next' value from the response["playlists"] dictionary.
        next_page = response.get('playlists').get('next')
        # Update the kwargs dictionary: set the value of the key 'next' as the variable next_page.
        kwargs["next"] = next_page
        ### END CODE HERE ###
        
        print(f"Executed request with URL: {response.get('playlists').get('href')}.")
                
    return responses
    
```

Now, perform the new paginated call:


```python
responses_with_next = paginated_with_next_featured_playlists(endpoint_request=get_featured_playlists, url=URL_FEATURE_PLAYLISTS, access_token=token.get('access_token'))
```

    Executed request with URL: https://api.spotify.com/v1/browse/featured-playlists?offset=0&limit=20.
    Executed request with URL: https://api.spotify.com/v1/browse/featured-playlists?offset=20&limit=20.
    Executed request with URL: https://api.spotify.com/v1/browse/featured-playlists?offset=40&limit=20.
    Executed request with URL: https://api.spotify.com/v1/browse/featured-playlists?offset=60&limit=20.
    Executed request with URL: https://api.spotify.com/v1/browse/featured-playlists?offset=80&limit=20.


Have a look at one of the responses:


```python
responses_with_next[0]
```




    {'collaborative': False,
     'description': 'The hottest 50. Cover: Tate McRae',
     'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M'},
     'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M',
     'id': '37i9dQZF1DXcBWIGoYBM5M',
     'images': [{'height': None,
       'url': 'https://i.scdn.co/image/ab67706f000000029d98b94f343cd13002dedb9b',
       'width': None}],
     'name': 'Today’s Top Hits',
     'owner': {'display_name': 'Spotify',
      'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
      'href': 'https://api.spotify.com/v1/users/spotify',
      'id': 'spotify',
      'type': 'user',
      'uri': 'spotify:user:spotify'},
     'primary_color': '#FFFFFF',
     'public': True,
     'snapshot_id': 'ZuzzQAAAAADhqQafWE+qj88gO0gfJcje',
     'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks',
      'total': 50},
     'type': 'playlist',
     'uri': 'spotify:playlist:37i9dQZF1DXcBWIGoYBM5M'}



<a name='2.4'></a>
### 2.4 - Optional - API Rate Limits

*Note*: This is an optional section.

Another important aspect to take into account when working with APIs is regarding the rate limits. Rate limiting is a mechanism used by APIs to control the number of requests that a client can make within a specified period of time. It helps prevent abuse or overload of the API by limiting the frequency or volume of requests from a single client. Here's how rate limiting typically works:

- Request Quotas: APIs may enforce a maximum number of requests that a client can make within a given time window, for example, 100 requests per minute.

- Time Windows: The time window specifies the duration over which the request quota is measured. For example, a rate limit of 100 requests per minute means that the client can make up to 100 requests in any 60-second period.

- Response to Exceeding Limits: When a client exceeds the rate limit, the API typically responds with an error code (such as 429 Too Many Requests) or a message indicating that the rate limit has been exceeded. This allows clients to adjust their behavior accordingly, such as by implementing [exponential backoff](https://medium.com/bobble-engineering/how-does-exponential-backoff-work-90ef02401c65) and other retry strategies. (Check [here](https://harish-bhattbhatt.medium.com/best-practices-for-retry-pattern-f29d47cd5117) or [here](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)). 

- Rate Limit Headers: APIs may include headers in the response to indicate the client's current rate limit status, such as the number of requests remaining until the limit resets or the time at which the limit will reset.

Rate limiting helps maintain the stability and reliability of APIs by ensuring fair access to resources and protecting against abusive or malicious behavior. It also allows API providers to allocate resources more effectively and manage traffic loads more efficiently.

You can also see more of the specifics of the rate limits of the Spotify Web API in the [documentation](https://developer.spotify.com/documentation/web-api/concepts/rate-limits). Particularly, this API doesn't enforce a hard limit for the number of requests done but it works dynamically based on the number of calls within a rolling 30 seconds window. You can find some [blogs](https://medium.com/mendix/limiting-your-amount-of-calls-in-mendix-most-of-the-time-rest-835dde55b10e#:~:text=The%20Spotify%20API%20service%20has,for%2060%20requests%20per%20minute) where experiments have been done to identify the average number of requests per minute. 

Below you are provided with a code that benchmarks the API calls; you can play with the number of requests and the request interval to see the average time of a request. In case you perform too many requests so that you violate the rate limits, you will get a 429 status code.

*Note*: This code may take a few minutes to run.


```python
import time

# Define the Spotify API endpoint
endpoint = 'https://api.spotify.com/v1/browse/featured-playlists?offset=0&limit=20'

headers = get_auth_header(access_token=token.get('access_token'))

# Define the number of requests to make
num_requests = 200

# Define the interval between requests (in seconds)
request_interval = 0.1  # Adjust as needed based on the API rate limit

# Store the timestamps of successful requests
success_timestamps = []

# Make repeated requests to the endpoint
for i in range(num_requests):
    # Make the request
    response = requests.get(url=endpoint, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        success_timestamps.append(time.time())
    else:        
        print(f'Request {i+1}: Failed with code {response.status_code}')
    
    # Wait for the specified interval before making the next request
    time.sleep(request_interval)

# Calculate the time between successful requests
if len(success_timestamps) > 1:
    time_gaps = [success_timestamps[i] - success_timestamps[i-1] for i in range(1, len(success_timestamps))]
    print(f'Average time between successful requests: {sum(time_gaps) / len(time_gaps):.2f} seconds')
else:
    print('At least two successful requests are needed to calculate the time between requests.')
```

    Average time between successful requests: 0.50 seconds


<a name='3'></a>
## 3 - Batch pipeline

Now that you have learned the basics of working with APIs, let's create a pipeline that extracts the track information for the featured playlists. For that, you will use two endpoints:
* The same [featured playlists endpoint](https://developer.spotify.com/documentation/web-api/reference/get-featured-playlists) you used in the previous exercises.
* The [Get Playlist Items endpoint](https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks). This endpoint allows you to get tracks information for a given playlist such as track name, album, artists, etc.

In the `src/` folder, you are given three scripts (`authentication.py`, `endpoint.py` and `main.py`) that will allow you to perform such extraction.
- The `endpoint.py` file contains two paginated api calls. The first one `get_paginated_featured_playlists`allows you get the list of featured playlists using the same paginated call you used in the first part. The second one `get_paginated_spotify_playlists` allows you to get the track information for a given playlist using the Get Playlist Items endpoint. 
- The `authentication.py` file contains the script of the `get_token` function that returns an access token.
- The `main.py` file calls the first paginated API call to get the ids of the featured playlists. Then for each playlist id, the second paginated API call is performed to extract the track information for each playlist id. 

At this moment, the code manages paginated requests but we haven't taken into account that our access token has a limited time, so if your pipeline requests last more than 3600 seconds, you can get a 401 status code error. So the first step is to write a routine that handles token refresh in the `get_paginated_featured_playlists`. Follow the instructions to implement this routine.

<a name='ex04'></a>
### Exercise 4

Open the file located at `src/endpoint.py`.

Search for the `get_paginated_featured_playlists` function. Create an if condition over the `response.status_code` and compare it with the value 401. This means that if the returned status code is 401 (Unauthorized) you will perform the next steps:
- Use the `kwargs` argument that is passed to the `get_paginated_featured_playlists` function; pass it to the `get_token` callable and assign it to a variable named `token_response`.
- Create an internal condition in which you will check if the key `"access_token"` is in the `token_response` dictionary. If true, you will call the `get_auth_header` function with the corresponding access token and assign the result to the variable `headers`. Note the usage of the `continue` keyword to make sure that the request will be executed again.
- If the condition over `"access_token"` is false, just return an empty list.

Save changes in the file `src/endpoint.py`.

Now that we know how to refresh the token in case it expires, it's time to continue with the rest of the code. Now that we have the featured playlists, the idea is to extract the tracks that compose each playlist with the following information: 

* Playlist name and reference URL
* Track name and reference URL
* Album name and reference URL
* Artist name and reference URL

To get this information, you will use the [Get Playlist Items endpoint](https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks). Take a moment to read the documentation and understand how to request data from that particular endpoint. Take a closer look at the `fields` parameter as it will be used for the next part of the pipeline. 

Open the file at `src/main.py`. There you will see after the call to the `get_paginated_featured_playlists` function that you are extracting the playlists' IDs from the response and saving them into the `playlist_ids` list. Those IDs will be used in the request. Also, search for the following constants: 

- `URL_PLAYLIST_ITEMS`: The base URL to get information from a particular playlist. Take a look at the documentation, you can see that you will have to complement that URL with the playlist ID and with the `tracks` string to complete the endpoint.
- `PLAYLIST_ITEMS_FIELDS`: A string with some fields that will be passed to the particular endpoint through the `fields` parameter. This string specifies what fields should be returned in the response such as the track name and url, album name and url and artist name and url as requested.

This information will be passed to the function `get_paginated_spotify_playlist` to construct the full endpoint for the API call. In the next exercise, you will work on completing this function in the file `src/endpoint.py`.

<a name='ex05'></a>
### Exercise 5

Go back to the `src/endpoint.py` file. Search for the comment `Exercise 5` and follow the instructions to complete the function `get_paginated_spotify_playlist`.

1. The function blueprint for `get_paginated_spotify_playlist` is already provided to you. The first thing you have to do is to call the `get_auth_header` function with the access token and pass it to a variable `headers`. 
2. Create the `requests_url` by using the `base_url` and `playlist_id` parameters. Remember to add `tracks` to the URL endpoint. Also, make sure to add the `fields` parameter to the URL request to filter only the necessary fields for the playlist's items.
3. In the `while` loop, perform a GET request using the `request_url` and `headers` that you created in the previous step. Assign the result to `response`.
4. Implement the same token refresh routine as before for the `get_paginated_featured_playlists` function.
5. After the token refresh, convert the `response` to JSON using the `.json()` method. Assign it to `response_json`.
6. Extend the `playlist_data` list with the value from `"items"` in `response_json`.
7. Update `request_url` with the `"next"` value from `response_json`.

Save changes in the file `src/endpoint.py`.

<a name='ex06'></a>
### Exercise 6

Go back to the `src/main.py` file. Search for the comment `Exercise 6`. Inside the loop that iterates through the `playlists_ids`, there's a call for the `get_paginated_spotify_playlists` function. Follow the instructions to define the following parameters for the given function:
- `base_url`: Use the `URL_PLAYLIST_ITEMS` constant defined for you.
- `access_token`: Make sure to pass the `"access_token"` from the `token` object.
- `playlist_id`.
- `fields` Use the `PLAYLIST_ITEMS_FIELDS` constant with the fields to be extracted in the request.
- `get_token`: pass the same `get_token` function.
- Finally, pass the `kwargs` dictionary defined at the start of the `main()` function.

The function response will be assigned to the variable `playlist_data`.

Save changes in the file `src/main.py`.

Inside the same for loop, the response `playlist_data` is added to the `playlists_items` dictionary, using the corresponding playlist id as key. Finally, after iterating through all playlists, you can see that the dictionary `playlists_items` is saved to a JSON file in the local environment. Take a look at the format of the filename, which takes into account the current date time to avoid collision with other files.

Run the following commands in Jupyter or Cloud9 terminal to run the `main.py` script:

```bash
cd ~/environment
source jupyterlab-venv/bin/activate
cd src
python main.py
```

*Notes*: 
- The first command ensures that you're in the root folder (environment). This is to ensure that you successfully run the second command. 
- To open the Jupyter Notebook terminal, click on File -> New -> Terminal
<img src="images/JupyterTerminal.png"  width="500"/>

Once the script is finished, you should be able to see a file named `playlist_items_<DATETIME>.json` in the folder `src`.

<a name='4'></a>
## 4 - Optional - Spotipy SDK

In several cases, the API developers also provide a Software Development Kit (SDK) to connect and perform requests to the different endpoints of the API without the necessity of creating the code from scratch. For Spotify Web API they developed the [Spotipy SDK](https://spotipy.readthedocs.io/en/2.22.1/) to do it. Let's see an example of how it will work to replicate the extraction of data from the featured playlists endpoint in a paginated way.


```python
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
```


```python
credentials = SpotifyClientCredentials(
        client_id=CLIENT_ID, client_secret=CLIENT_SECRET
    )

spotify = spotipy.Spotify(client_credentials_manager=credentials)
```

You can see that the `credentials` object handles the authentication process and contains the token to be used in later requests.

*Note*: Please ignore the `DeprecationWarning` message if you see an access token in the output.


```python
credentials.get_access_token()
```

    /tmp/ipykernel_3074/2682040240.py:1: DeprecationWarning: You're using 'as_dict = True'.get_access_token will return the token string directly in future versions. Please adjust your code accordingly, or use get_cached_token instead.
      credentials.get_access_token()





    {'access_token': 'BQD_5waHR77C3NZaqyCGyu2FyVmAyBMejjSI4m9Pymi18HQAawp6_3dJnsUcOPA5M09MEHBXdd1W4DIqeXZX7evcfdPjM9YExODB-5Qsji7KaV4cIgY',
     'token_type': 'Bearer',
     'expires_in': 3600,
     'expires_at': 1727207794}



Let's get data from the featured playlists, as you did in the previous example:


```python
limit = 20
response = spotify.featured_playlists(limit=limit)
response
```




    {'message': 'Popular Playlists',
     'playlists': {'href': 'https://api.spotify.com/v1/browse/featured-playlists?offset=0&limit=20',
      'items': [{'collaborative': False,
        'description': 'The hottest 50. Cover: Tate McRae',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M',
        'id': '37i9dQZF1DXcBWIGoYBM5M',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000029d98b94f343cd13002dedb9b',
          'width': None}],
        'name': 'Today’s Top Hits',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAADhqQafWE+qj88gO0gfJcje',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DXcBWIGoYBM5M'},
       {'collaborative': False,
        'description': "Today's top country hits. Cover: Keith Urban",
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX1lVhptIYRda'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX1lVhptIYRda',
        'id': '37i9dQZF1DX1lVhptIYRda',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000021d653e6a53115413b2ffc5d4',
          'width': None}],
        'name': 'Hot Country',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFC864',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAAAwyHLTutcLwmNj++EmbDFK',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX1lVhptIYRda/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX1lVhptIYRda'},
       {'collaborative': False,
        'description': 'New music from Future, Lil Tecca and GloRilla. ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX0XUsuxWHRQd',
        'id': '37i9dQZF1DX0XUsuxWHRQd',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002e9367d2bc3e15cee50708ec2',
          'width': None}],
        'name': 'RapCaviar',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#F49B23',
        'public': True,
        'snapshot_id': 'ZvHBuQAAAAC3z5zpc8qNG3+6PvhFxEAZ',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX0XUsuxWHRQd/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX0XUsuxWHRQd'},
       {'collaborative': False,
        'description': 'The essential tracks, all in one playlist.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX5KpP2LN299J'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX5KpP2LN299J',
        'id': '37i9dQZF1DX5KpP2LN299J',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f0000000252feef11af8c9d412769ec5a',
          'width': None}],
        'name': 'This Is Taylor Swift',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'ZqsIQAAAAADe3rfnkTpKF5/AovrNituQ',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX5KpP2LN299J/tracks',
         'total': 180},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX5KpP2LN299J'},
       {'collaborative': False,
        'description': "Today's top Latin hits, elevando nuestra música. Cover: Bad Bunny",
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX10zKzsJ2jva'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX10zKzsJ2jva',
        'id': '37i9dQZF1DX10zKzsJ2jva',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002c1f07388b99b45312ad8e6c9',
          'width': None}],
        'name': 'Viva Latino',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'Zuy7AAAAAAA1G9tXanO/u5MOBpDKz0C3',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX10zKzsJ2jva/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX10zKzsJ2jva'},
       {'collaborative': False,
        'description': 'All your favorite Disney hits, including classics from Encanto, Descendants, Moana, Frozen, & The Lion King.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX8C9xQcOrE6T'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX8C9xQcOrE6T',
        'id': '37i9dQZF1DX8C9xQcOrE6T',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000027bdaa8658900f615ec212e73',
          'width': None}],
        'name': 'Disney Hits',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZtFisAAAAAA/1T9si5CYndx/doDKMvYa',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX8C9xQcOrE6T/tracks',
         'total': 111},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX8C9xQcOrE6T'},
       {'collaborative': False,
        'description': 'Gentle Ambient piano to help you fall asleep. ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWZd79rJ6a7lp'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZd79rJ6a7lp',
        'id': '37i9dQZF1DWZd79rJ6a7lp',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002cd17d41419faa97069e06c16',
          'width': None}],
        'name': 'Sleep',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'Zt63/gAAAAAn9oDfil6AhraaIoVjzapY',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZd79rJ6a7lp/tracks',
         'total': 183},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWZd79rJ6a7lp'},
       {'collaborative': False,
        'description': 'New music from Future, Bad Bunny, Bon Iver, Katy Perry, GloRilla, and more!',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX4JAvHpjipBk'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX4JAvHpjipBk',
        'id': '37i9dQZF1DX4JAvHpjipBk',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002cb4876c76b840ff5d773ea5e',
          'width': None}],
        'name': 'New Music Friday',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAABeoXK67XGjky+Sl/e2ZJAR',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX4JAvHpjipBk/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX4JAvHpjipBk'},
       {'collaborative': False,
        'description': 'Ten hours long continuous white noise to help you relax and let go. ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWUZ5bk6qqDSy'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWUZ5bk6qqDSy',
        'id': '37i9dQZF1DWUZ5bk6qqDSy',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000025b4d326fee8531fe32efe166',
          'width': None}],
        'name': 'White Noise 10 Hours',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZqnuAAAAAADY7kNw/2LeeKmMLVe9MAvu',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWUZ5bk6qqDSy/tracks',
         'total': 230},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWUZ5bk6qqDSy'},
       {'collaborative': False,
        'description': 'The hottest tracks in the United States. Cover: Sabrina Carpenter',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX0kbJZpiYdZl'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX0kbJZpiYdZl',
        'id': '37i9dQZF1DX0kbJZpiYdZl',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002c853cf0c309b398aa04e634f',
          'width': None}],
        'name': 'Hot Hits USA',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#FFFFFF',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAACNQVLjaktGmI/aMGhyGCvH',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX0kbJZpiYdZl/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX0kbJZpiYdZl'},
       {'collaborative': False,
        'description': 'Fourth quarter, two minutes left .. get locked in. Cover: Derrick Henry\n\n',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWTl4y3vgJOXW'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWTl4y3vgJOXW',
        'id': '37i9dQZF1DWTl4y3vgJOXW',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000027e645f7152aeac420b004512',
          'width': None}],
        'name': 'Locked In',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZvCi7wAAAAD1fQMtiF0Hci+pZchnTRB1',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWTl4y3vgJOXW/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWTl4y3vgJOXW'},
       {'collaborative': False,
        'description': 'autumn leaves falling down like pieces into place',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXahsxs9xh0fn'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXahsxs9xh0fn',
        'id': '37i9dQZF1DXahsxs9xh0fn',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002dcbea5e236f33008e73e3192',
          'width': None}],
        'name': 'fall feels',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZvHr6gAAAAD+AQKtIzuRvvQHyWj3hBh3',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXahsxs9xh0fn/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DXahsxs9xh0fn'},
       {'collaborative': False,
        'description': 'Peaceful piano to help you slow down, breathe, and relax. ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX4sWSpwq3LiO'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX4sWSpwq3LiO',
        'id': '37i9dQZF1DX4sWSpwq3LiO',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f0000000283da657fca565320e9311863',
          'width': None}],
        'name': 'Peaceful Piano',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZvF9/gAAAADPtdPFmSIXjwqmwmrlZWia',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX4sWSpwq3LiO/tracks',
         'total': 204},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX4sWSpwq3LiO'},
       {'collaborative': False,
        'description': 'This is Zach Bryan. The essential tracks, all in one playlist.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DZ06evO2llutr'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO2llutr',
        'id': '37i9dQZF1DZ06evO2llutr',
        'images': [{'height': None,
          'url': 'https://thisis-images.spotifycdn.com/37i9dQZF1DZ06evO2llutr-default.jpg',
          'width': None}],
        'name': 'This Is Zach Bryan',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': None,
        'public': True,
        'snapshot_id': 'ZvCvgAAAAAABIKaVr5aychkT8PMgH5vu',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DZ06evO2llutr/tracks',
         'total': 43},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DZ06evO2llutr'},
       {'collaborative': False,
        'description': 'Soft instrumental Jazz for all your activities.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWV7EzJMK2FUI'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWV7EzJMK2FUI',
        'id': '37i9dQZF1DWV7EzJMK2FUI',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f00000002472120b92edea982b5feb264',
          'width': None}],
        'name': 'Jazz in the Background',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuybGQAAAACn9xZrkMigk0LIjSHPmFLF',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWV7EzJMK2FUI/tracks',
         'total': 786},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWV7EzJMK2FUI'},
       {'collaborative': False,
        'description': 'Keep calm and focus with ambient and post-rock music.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZeKCadgRdKQ',
        'id': '37i9dQZF1DWZeKCadgRdKQ',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000026020f2f6476db518ef747da4',
          'width': None}],
        'name': 'Deep Focus',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuqOmgAAAABj4oPfIm8TJ635GGeoRo7Y',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWZeKCadgRdKQ/tracks',
         'total': 162},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWZeKCadgRdKQ'},
       {'collaborative': False,
        'description': 'the beat of your drift',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWWY64wDtewQt'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWY64wDtewQt',
        'id': '37i9dQZF1DWWY64wDtewQt',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000027dc5028b26eb62f22d31bb1f',
          'width': None}],
        'name': 'phonk',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'Zu2O8AAAAABj9nRkASfiLYEB8aMyMY0m',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWY64wDtewQt/tracks',
         'total': 100},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWWY64wDtewQt'},
       {'collaborative': False,
        'description': "Country music's 50 most played songs in the world. Updated weekly. Cover: Post Malone and Morgan Wallen",
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX7aUUBCKwo4Y'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX7aUUBCKwo4Y',
        'id': '37i9dQZF1DX7aUUBCKwo4Y',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000025b07a04dce2d3bdf7b3352e5',
          'width': None}],
        'name': 'Country Top 50',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZusjpgAAAAA4sW9Te9EmTxqVgw76UHJW',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX7aUUBCKwo4Y/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX7aUUBCKwo4Y'},
       {'collaborative': False,
        'description': 'chill beats, lofi vibes, new tracks every week... ',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DWWQRwui0ExPn'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWQRwui0ExPn',
        'id': '37i9dQZF1DWWQRwui0ExPn',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f0000000255be59b7be2929112e7ac927',
          'width': None}],
        'name': 'lofi beats',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'ZuzzQAAAAACI+zl4dWMXp+qQ/dUIjDhK',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DWWQRwui0ExPn/tracks',
         'total': 750},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DWWQRwui0ExPn'},
       {'collaborative': False,
        'description': '¡Las más placosas y llegadoras de nuestra música! Al millón con Grupo Firme, Hernan Sepulveda.',
        'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DX905zIRtblN3'},
        'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX905zIRtblN3',
        'id': '37i9dQZF1DX905zIRtblN3',
        'images': [{'height': None,
          'url': 'https://i.scdn.co/image/ab67706f000000028169dfcd53c5fa947ac80bc2',
          'width': None}],
        'name': 'La Reina: Éxitos de la Música Mexicana',
        'owner': {'display_name': 'Spotify',
         'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
         'href': 'https://api.spotify.com/v1/users/spotify',
         'id': 'spotify',
         'type': 'user',
         'uri': 'spotify:user:spotify'},
        'primary_color': '#ffffff',
        'public': True,
        'snapshot_id': 'Zuz1+QAAAAA4i7k9OW/f8fb2zIHZiZfz',
        'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DX905zIRtblN3/tracks',
         'total': 50},
        'type': 'playlist',
        'uri': 'spotify:playlist:37i9dQZF1DX905zIRtblN3'}],
      'limit': 20,
      'next': 'https://api.spotify.com/v1/browse/featured-playlists?offset=20&limit=20',
      'offset': 0,
      'previous': None,
      'total': 100}}



You can also paginate through these responses. If you check the documentation of the [`featured_playlist` method](https://spotipy.readthedocs.io/en/2.22.1/?highlight=featured_playlists#spotipy.client.Spotify.featured_playlists), you can see that you can specify the parameter `offset`, as you previously did. 

<a name='ex07'></a>
### Exercise 7

LetвЂ™s perform a paginated request with the SDK. We can then check the results of this paginated request against the total number of elements we saw in the previous exercises, which would be 100. Follow the instructions to finish the code to perform paginated requests.

1. Extend the `playlist_data` list with the `items` from the `playlists` key in the previous `response`.
2. Get the `total` number of elements from the response and assign it to the variable `total_playlists_elements`.
3. Create a list of offset indexes. As you already have the data from the first call, your starting offset index should be the `limit` value that you used to make the first request. The list should finish at `total_playlists_elements` and the pace should be the same `limit` value. Save it into `offset_idx`.
4. Start the pagination: iterate over each index in `offset_idx`. In `response_page`, assign the response from the request to the `featured_playlists` method using the corresponding offset index and limit.
5. Extend again the `playlist_data` with the playlist `items` that you get in the `response_page`.

You can visually inspect the values in the `playlist_data` and make sure the list length is the same as the total number of elements that are available to request.


```python
def paginated_feature_playlists_sdk(limit: int=20) -> list:

    playlist_data = []
    ### START CODE HERE ### (~ 6 lines of code)
    playlist_data.extend(response.get('playlists').get('items'))
    total_playlists_elements = response.get('playlists').get('total')
    offset_idx = list(range(limit, total_playlists_elements, limit))

    for idx in offset_idx:         
        response_page = spotify.featured_playlists(limit=limit, offset=idx)
        playlist_data.extend(response_page.get('playlists').get('items'))
    ### END CODE HERE ###
    return playlist_data
    
playlist_data_sdk = paginated_feature_playlists_sdk()
playlist_data_sdk[0]
```




    {'collaborative': False,
     'description': 'The hottest 50. Cover: Tate McRae',
     'external_urls': {'spotify': 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M'},
     'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M',
     'id': '37i9dQZF1DXcBWIGoYBM5M',
     'images': [{'height': None,
       'url': 'https://i.scdn.co/image/ab67706f000000029d98b94f343cd13002dedb9b',
       'width': None}],
     'name': 'Today’s Top Hits',
     'owner': {'display_name': 'Spotify',
      'external_urls': {'spotify': 'https://open.spotify.com/user/spotify'},
      'href': 'https://api.spotify.com/v1/users/spotify',
      'id': 'spotify',
      'type': 'user',
      'uri': 'spotify:user:spotify'},
     'primary_color': '#FFFFFF',
     'public': True,
     'snapshot_id': 'ZuzzQAAAAADhqQafWE+qj88gO0gfJcje',
     'tracks': {'href': 'https://api.spotify.com/v1/playlists/37i9dQZF1DXcBWIGoYBM5M/tracks',
      'total': 50},
     'type': 'playlist',
     'uri': 'spotify:playlist:37i9dQZF1DXcBWIGoYBM5M'}




```python
len(playlist_data_sdk)
```




    100



In this lab you learned the basics of ingesting data from the API. You worked with authentication process and pagination in a manual way as well as using an API SDK.

<a name='5'></a>
## 5 - Upload the Files for Grading
Run the following cell to upload the notebook and Python files `./src/main.py`, `./src/endpoint.py` into S3 bucket for grading purposes.

*Note*: you may need to click **Save** button before the upload.


```python
# Retrieve the AWS account ID
result = subprocess.run(['aws', 'sts', 'get-caller-identity', '--query', 'Account', '--output', 'text'], capture_output=True, text=True)
AWS_ACCOUNT_ID = result.stdout.strip()

SUBMISSION_BUCKET = f"de-c2w2a1-{AWS_ACCOUNT_ID}-us-east-1-submission"

!aws s3 cp ./C2_W2_Assignment.ipynb s3://$SUBMISSION_BUCKET/C2_W2_Assignment_Learner.ipynb
!aws s3 cp ./src/main.py s3://$SUBMISSION_BUCKET/src/main_learner.py
!aws s3 cp ./src/endpoint.py s3://$SUBMISSION_BUCKET/src/endpoint_learner.py
```

    upload: ./C2_W2_Assignment.ipynb to s3://de-c2w2a1-083361267754-us-east-1-submission/C2_W2_Assignment_Learner.ipynb
    upload: src/main.py to s3://de-c2w2a1-083361267754-us-east-1-submission/src/main_learner.py
    upload: src/endpoint.py to s3://de-c2w2a1-083361267754-us-east-1-submission/src/endpoint_learner.py



```python

```
