import datetime as dt
import json
import os

from dotenv import load_dotenv
from endpoint import (
    get_paginated_featured_playlists,
    get_paginated_spotify_playlist,
)
from authentication import get_token

load_dotenv("./env", override=True)

CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")


URL_TOKEN = "https://accounts.spotify.com/api/token"
URL_FEATURE_PLAYLISTS = "https://api.spotify.com/v1/browse/featured-playlists"
URL_PLAYLIST_ITEMS = "https://api.spotify.com/v1/playlists"
PLAYLIST_ITEMS_FIELDS = "href,name,owner(!href,external_urls),items(added_at,track(name,href,album(name,href),artists(name,href))),offset,limit,next,previous,total"


def main():
    # Getting token:
    kwargs = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "url": URL_TOKEN,
    }

    token = get_token(**kwargs)

    featured_playlists = get_paginated_featured_playlists(
        base_url=URL_FEATURE_PLAYLISTS,
        access_token=token.get("access_token"),
        get_token=get_token,
        **kwargs,
    )

    print("Featured playlists have been extracted.")

    # Getting playlists IDs
    playlists_ids = [playlist["id"] for playlist in featured_playlists]

    print(
        f"Total number of featured playlists extracted: {len(playlists_ids)}"
    )

    # Getting information about each playlist
    print(f"Getting information about each playlist")

    playlists_items = {}

    ### Exercise 6
    ### START CODE HERE ### (~ 9 lines of code)
    for playlist_id in playlists_ids:
        playlist_data = get_paginated_spotify_playlist(
            base_url=None,
            access_token=token.None("None"),
            playlist_id=None,
            fields=None,
            get_token=None,
            **None,
        )
    ### END CODE HERE ###

        playlists_items[playlist_id] = playlist_data

        print(f"Playlist {playlist_id} has been processed successfully")

    # Saving processed data to a JSON file.
    if len(playlists_items.keys()) > 0:
        current_time = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        filename = f"playlist_items_{current_time}"

        with open(f"./{filename}.json", "w+") as playlists_file:
            json.dump(playlists_items, playlists_file)

        print(f"Data has been saved successfully to {filename}.json")
    else:
        print(f"No data was available to be saved.")


if __name__ == "__main__":
    main()
