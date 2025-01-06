from dataclasses import dataclass


@dataclass
class RSPLTag:
    name: str
    rspl_id: str
    icon: str
    color: str
    user: bool


@dataclass
class RSPLTags:
    tag_to_download: RSPLTag
    tag_downloaded: RSPLTag
    tag_loaded: RSPLTag
    tag_new_viewer_request: RSPLTag
    tag_raider_request: RSPLTag
    tag_vip_viewer_request: RSPLTag

