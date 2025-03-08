import sys

import requests

from modules.servant.song_loader.dataclasses.owned_dlcs import OwnedDLCs, OwnedDLC
from utils.exceptions import RSPLPlaylistIsNotEnabledError

REQUEST_TIMEOUT = 15

RS_PLAYLIST_HOME = "https://rsplaylist.com/ajax/"
URLS = {
    "playlist": RS_PLAYLIST_HOME + "playlist.php?channel={channel}",
    "viewers": RS_PLAYLIST_HOME + "viewers.php?user_name=&pageIndex=0&channel={channel}",
    "settings": RS_PLAYLIST_HOME + "form-settings.php?channel={channel}",
    "tag_set": RS_PLAYLIST_HOME + "requests.php?channel={channel}&action=set-tag&id={id}&tag={tag}&value=true",
    "tag_unset": RS_PLAYLIST_HOME + "requests.php?channel={channel}&action=set-tag&id={id}&tag={tag}&value=false",
}


def fetch_owned_dlc(channel: str, php_session_id: str) -> OwnedDLCs:
    """
    Fetch owned DLC data from the RS Playlist API paginated endpoint.
    :param channel: The channel name.
    :param php_session_id: The PHP session ID for authentication.
    :return: An OwnedDLCs object containing the list of DLCs, total count and owned count.
    """
    base_url = RS_PLAYLIST_HOME + "owneddlc.php?pageIndex={page}&pageSize=1&channel={channel}"
    results = []
    page_index = 0
    owned_count = 0

    while True:
        # Format the URL with pageIndex and channel
        url = base_url.format(page=page_index, channel=channel)

        # Make the request
        response = make_request("GET", url, cookies={'PHPSESSID': php_session_id})

        # Parse the response data
        dlc_items = response.get('data', [])
        if not dlc_items:  # Stop if no more items are returned
            break

        # Define the mapping from JSON keys to OwnedDLC fields
        key_mapping = {
            'id': 'rspl_owned_dlc_id',
        }

        # Convert JSON objects into OwnedDLC data class instances
        for item in dlc_items:
            results.append(OwnedDLC(**(map_rspl_item(item, key_mapping))))
            if item.get('owned'):
                owned_count += 1

        # Increment the page index for the next request
        page_index += 1

    return OwnedDLCs(
        data=results,
        total_count=len(results),
        owned_count=owned_count
    )


def map_rspl_item(item, key_mapping):
    mapped_item = {
        key_mapping.get(k, k): v
        for k, v in item.items()
        if k in key_mapping or k in OwnedDLC.__annotations__
    }
    return mapped_item


def make_request(method, url, cookies, timeout=REQUEST_TIMEOUT):
    """
    Helper function for making HTTP requests.
    :param method: HTTP method ('GET', 'PUT', etc.)
    :param url: The URL to request.
    :param cookies: Dictionary of cookies for the request.
    :param timeout: Timeout for the request.
    :return: JSON response.
    """
    response = requests.request(method, url, cookies=cookies, timeout=timeout)
    return response.json()


def get_playlist(channel, php_session_id):
    return make_request("GET", URLS["playlist"].format(channel=channel), cookies={'PHPSESSID': php_session_id})


def get_viewers(channel, php_session_id):
    return make_request("GET", URLS["viewers"].format(channel=channel), cookies={'PHPSESSID': php_session_id})


def get_settings(channel, php_session_id):
    return make_request("GET", URLS["settings"].format(channel=channel), cookies={'PHPSESSID': php_session_id})


def __set_tag(channel, php_session_id, request_id, tag_id):
    url = URLS["tag_set"].format(channel=channel, id=request_id, tag=tag_id)
    make_request("PUT", url, cookies={'PHPSESSID': php_session_id})


def __unset_tag(channel, php_session_id, request_id, tag_id):
    url = URLS["tag_unset"].format(channel=channel, id=request_id, tag=tag_id)
    make_request("PUT", url, cookies={'PHPSESSID': php_session_id})


def unset_user_tags(channel, php_session_id, request_id, tags, item_tags):
    for tag in item_tags:
        if tag in (tags.tag_loaded, tags.tag_to_download):  # Simplified condition
            __unset_tag(channel, php_session_id, request_id, tag)


def set_tag_loaded(channel, php_session_id, request_id, tags):
    __set_tag(channel, php_session_id, request_id, tags.tag_loaded)


def set_tag_to_download(channel, php_session_id, request_id, tags):
    __set_tag(channel, php_session_id, request_id, tags.tag_to_download)


def user_is_not_logged_in(playlist):
    try:
        # Streamlined the nested checks for readability
        return any(
            "id" not in cdlc
            for sr in playlist.get("playlist", [])
            for cdlc in sr.get("dlc_set", [])
        )
    except KeyError as exc:
        raise RSPLPlaylistIsNotEnabledError from exc


if __name__ == "__main__":
    # Main section, for testing the fetch_owned_dlc function.
    # Ensure the script receives the correct number of arguments
    if len(sys.argv) != 3:
        print("Usage: python rs_playlist_util.py <channel_name> <php_session_id>")
        sys.exit(1)

    # Get the channel and PHP session ID from command-line arguments
    channel_name = sys.argv[1]
    php_session_id_arg = sys.argv[2]

    try:
        # Fetch the owned DLC data
        print(f"Fetching owned DLC for channel '{channel_name}'...")
        owned_dlc_list = fetch_owned_dlc(channel_name, php_session_id_arg)

        # Output the result
        if not owned_dlc_list:
            print("No DLC items found.")
        else:
            print(f"Found {owned_dlc_list.total_count} DLC items, "
                  f"from what {owned_dlc_list.owned_count} are owned:")

            owned_dlcs = sorted([dlc for dlc in owned_dlc_list.data if dlc.owned],
                                key=lambda x: (x.artist_name.lower(), x.title.lower()))
            if owned_dlcs:
                print("\nOwned DLCs:")
                for dlc in owned_dlcs:
                    print(f"{dlc.rspl_owned_dlc_id} - {dlc.cdlc_id}: {dlc.artist_name} - {dlc.title}")
            else:
                print("\nNo owned DLCs found.")

    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"An error occurred: {e}")
