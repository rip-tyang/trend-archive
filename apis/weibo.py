from typing import Dict, List, Any
from os import path
import urllib.parse

from apis.base import BaseApi
from writer import write_raw_data, write_md


class WeiboAPI(BaseApi):
    LOC = 'Weibo'
    BASE_URL = 'https://weibo.com/ajax/side/hotSearch'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'hot_search.json',
        'README.md',
    ]

    @classmethod
    def get_hot_search(cls) -> RAW_DATA_T:
        json_data = cls._get_json(cls.BASE_URL, headers={'Referer': 'https://weibo.com'})
        realtime = json_data.get('data', {}).get('realtime', [])
        parsed = []
        for rank, item in enumerate(realtime, start=1):
            word = item.get('word', '').replace('|', '-')
            num = item.get('num', 0)
            tag = item.get('label_name') or item.get('icon_desc') or ''
            raw_url = item.get('word_scheme', '')
            encoded_word = urllib.parse.quote(item.get('word', ''))
            search_url = f'https://s.weibo.com/weibo?q={encoded_word}'

            parsed.append({
                'rank': rank,
                'word': word,
                'num': num,
                'tag': tag,
                'url': search_url,
                'raw': item,
            })
        return parsed

    @classmethod
    def _write_md_for_date(cls, loc: str, items: RAW_DATA_T) -> None:
        md_str = '# 微博热搜 (Weibo Hot Search)\n\n'
        md_str += '| 排名 | 热搜词 | 标签 | 热度 | 链接 |\n'
        md_str += '| --- | --- | --- | --- | --- |\n'

        for item in items:
            link = f'[{item["word"]}]({item["url"]})'
            tag = item['tag'] or '-'
            heat = f'{item["num"]:,}' if isinstance(item["num"], int) else str(item["num"])
            md_str += f'| {item["rank"]} | {link} | {tag} | {heat} | [查看]({item["url"]}) |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        items = cls.get_hot_search()
        write_raw_data(items, path.join(loc, 'hot_search.json'))
        cls._write_md_for_date(loc, items)
