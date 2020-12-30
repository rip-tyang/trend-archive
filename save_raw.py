from typing import List, Callable

import json
from time import sleep
from datetime import date
from os import path

from api import BilibiliApi
from writer import write_raw_data

BASE_PATH = './archive'
NAP_TIME = .5


def save_tags(api: BilibiliApi, loc: str, name: str, aids: List[str]) -> BilibiliApi.RAW_DATA_T:
    all_tags = {}
    for aid in aids:
        sleep(NAP_TIME)
        tag_list = api.get_tag(aid)
        for tag in tag_list:
            if tag['tag_id'] in all_tags:
                all_tags[tag['tag_id']]['day_count'] += 1
            else:
                all_tags[tag['tag_id']] = {'data': tag, 'day_count': 1}
    write_raw_data(all_tags, path.join(loc, 'Tags', name))


def save_raw(api: BilibiliApi, func: Callable[[], BilibiliApi.RAW_DATA_T], loc: str, name: str):
    raw_data = func()
    write_raw_data(raw_data, path.join(loc, 'Raw', name))

    aids = (video['aid'] for video in raw_data)
    save_tags(api, loc, name, aids)

def save_raw_today():
    date_str = date.today().isoformat()
    loc = path.join(BASE_PATH, 'Bilibili', date_str)

    api = BilibiliApi()
    save_raw(api, BilibiliApi.get_most_popular, loc, 'most_popular.json')
    save_raw(api, BilibiliApi.get_highest_ranked, loc, 'highest_ranked.json')


if __name__ == '__main__':
    save_raw_today()
