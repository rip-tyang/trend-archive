from typing import Dict, List, Any

import requests
import json

class BilibiliApi(object):
    BASE_URL = 'https://api.bilibili.com'
    RAW_DATA_T = List[Dict[str, Any]]

    @classmethod
    def get_highest_ranked(cls) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/web-interface/ranking'
        return cls._get_data_list(url)

    @classmethod
    def get_most_popular(cls) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/web-interface/popular'
        return cls._get_data_list(url)

    @classmethod
    def get_tag(cls, aid) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/tag/archive/tags?aid={aid}'
        return cls._get_data(url)

    @classmethod
    def _get_data(cls, url: str) -> RAW_DATA_T:
        json_data = cls._get(url)
        raw_data_list = json_data['data']
        return raw_data_list

    @classmethod
    def _get_data_list(cls, url: str) -> RAW_DATA_T:
        json_data = cls._get(url)
        raw_data_list = json_data['data']['list']
        return raw_data_list

    @classmethod
    def _get(cls, url: str) -> Dict[str, Any]:
        res = requests.get(url)
        print(f'getting {url}')
        if res.status_code != 200:
            raise ValueError('Status code: {res.status_code}\n Content: {res.text}')
        return json.loads(res.text)
