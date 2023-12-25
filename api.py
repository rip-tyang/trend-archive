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
        res = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        })
        print(f'getting {url}')
        if res.status_code != 200:
            raise ValueError(f'Status code: {res.status_code}\n Content: {res.text}')
        try:
            return json.loads(res.text)
        except json.decoder.JSONDecodeError as e:
            print(e)
            print(res.text)

