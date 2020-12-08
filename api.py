from typing import Dict, List, Any

import requests
import json

class BilibiliApi(object):
    BASE_URL = 'https://api.bilibili.com'
    RAW_DATA_T = List[Dict[str, Any]]

    @classmethod
    def get_highest_ranked(cls) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/web-interface/ranking'
        return cls._get_video_list(url)

    @classmethod
    def get_most_popular(cls) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/web-interface/popular'
        return cls._get_video_list(url)

    @classmethod
    def _get_video_list(cls, url: str) -> RAW_DATA_T:
        json_data = cls._get(url)
        raw_videos = json_data['data']['list']
        return raw_videos

    @classmethod
    def _get(cls, url: str) -> Dict[str, Any]:
        res = requests.get(url)
        if res.status_code != 200:
            raise ValueError('Status code: {res.status_code}\n Content: {res.text}')
        return json.loads(res.text)
