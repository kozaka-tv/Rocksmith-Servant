import requests

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
