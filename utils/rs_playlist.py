import requests

# EXAMPLE
# https://rsplaylist.com/ajax/requests.php?channel=kozaka&action=set-tag&id=1305252&tag=8c8c2924&value=true
# https://rsplaylist.com/ajax/requests.php?channel=kozaka&action=set-tag&id=1305252&tag=8c8c2924&value=false
RS_PLAYLIST_HOME = "https://rsplaylist.com/ajax"
URL_PLAYLIST = RS_PLAYLIST_HOME + "/playlist.php?channel=%s"
URL_REQUESTS = RS_PLAYLIST_HOME + "/requests.php?channel=%s"
URL_TAG_SET = URL_REQUESTS + "&action=set-tag&id=%s&tag=%s&value=true"
URL_TAG_UNSET = URL_REQUESTS + "&action=set-tag&id=%s&tag=%s&value=false"


def get_playlist(twitch_channel, phpsessid):
    return requests.get(URL_PLAYLIST % twitch_channel, cookies={'PHPSESSID': phpsessid}).json()


def set_tag(twitch_channel, phpsessid, rspl_request_id, tag_id):
    url = URL_TAG_SET % (twitch_channel, rspl_request_id, tag_id)
    cookies = {'PHPSESSID': phpsessid}
    requests.put(url, cookies=cookies).json()


def unset_tag(twitch_channel, phpsessid, rspl_request_id, tag_id):
    url = URL_TAG_UNSET % (twitch_channel, rspl_request_id, tag_id)
    cookies = {'PHPSESSID': phpsessid}
    requests.put(url, cookies=cookies).json()


def set_tag_loaded(twitch_channel, phpsessid, rspl_request_id, rspl_tags):
    set_tag(twitch_channel, phpsessid, rspl_request_id, rspl_tags.tag_loaded)
    # TODO remove tag 'to download'?
    unset_tag(twitch_channel, phpsessid, rspl_request_id, rspl_tags.tag_to_download)


def set_tag_to_download(twitch_channel, phpsessid, rspl_request_id, rspl_tags):
    set_tag(twitch_channel, phpsessid, rspl_request_id, rspl_tags.tag_to_download)
    # TODO remove tag 'loaded'?
    unset_tag(twitch_channel, phpsessid, rspl_request_id, rspl_tags.tag_loaded)
