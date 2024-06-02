import requests

from utils.exceptions import RSPLPlaylistIsNotEnabledError

RS_PLAYLIST_HOME = "https://rsplaylist.com/ajax/"
URL_PLAYLIST = RS_PLAYLIST_HOME + "playlist.php?channel=%s"
URL_REQUESTS = RS_PLAYLIST_HOME + "requests.php?channel=%s"
URL_TAG_SET = URL_REQUESTS + "&action=set-tag&id=%s&tag=%s&value=true"
URL_TAG_UNSET = URL_REQUESTS + "&action=set-tag&id=%s&tag=%s&value=false"
# https://rsplaylist.com/ajax/viewers.php?user_name=&pageIndex=3&channel=kozaka
URL_VIEWERS = RS_PLAYLIST_HOME + "viewers.php?user_name=&pageIndex=0&channel=%s"
# https://rsplaylist.com/ajax/form-settings.php?channel=Kozaka
URL_SETTINGS = RS_PLAYLIST_HOME + "form-settings.php?channel=%s"


def get_playlist(twitch_channel, phpsessid):
    return requests.get(URL_PLAYLIST % twitch_channel, cookies={'PHPSESSID': phpsessid}).json()


def get_viewers(twitch_channel, phpsessid):
    return requests.get(URL_VIEWERS % twitch_channel, cookies={'PHPSESSID': phpsessid}).json()


def get_settings(twitch_channel, phpsessid):
    return requests.get(URL_SETTINGS % twitch_channel, cookies={'PHPSESSID': phpsessid}).json()


def __set_tag(twitch_channel, phpsessid, rspl_request_id, tag_id):
    url = URL_TAG_SET % (twitch_channel, rspl_request_id, tag_id)
    cookies = {'PHPSESSID': phpsessid}
    requests.put(url, cookies=cookies).json()


def __unset_tag(twitch_channel, phpsessid, rspl_request_id, tag_id):
    url = URL_TAG_UNSET % (twitch_channel, rspl_request_id, tag_id)
    cookies = {'PHPSESSID': phpsessid}
    requests.put(url, cookies=cookies).json()


def set_tag_loaded(twitch_channel, phpsessid, rspl_request_id, rspl_tags):
    __unset_tag(twitch_channel, phpsessid, rspl_request_id, rspl_tags.tag_to_download)
    __set_tag(twitch_channel, phpsessid, rspl_request_id, rspl_tags.tag_loaded)


def set_tag_to_download(twitch_channel, phpsessid, rspl_request_id, rspl_tags):
    __unset_tag(twitch_channel, phpsessid, rspl_request_id, rspl_tags.tag_loaded)
    __set_tag(twitch_channel, phpsessid, rspl_request_id, rspl_tags.tag_to_download)


def user_is_not_logged_in(playlist):
    try:
        for sr in playlist["playlist"]:
            for cdlc in sr["dlc_set"]:
                try:
                    cdlc['id']
                except TypeError:
                    return True
                return False
        return None
    except KeyError:
        raise RSPLPlaylistIsNotEnabledError
