from typing import Dict, List, Any
from os import path

from apis.base import BaseApi
from writer import write_raw_data, write_md


class ZhihuAPI(BaseApi):
    LOC = 'Zhihu'
    BASE_URL = 'https://api.zhihu.com/topstory/hot-lists/total'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'hot_list.json',
        'README.md',
    ]

    @classmethod
    def get_hot_list(cls) -> RAW_DATA_T:
        json_data = cls._get_json(cls.BASE_URL)
        items = json_data.get('data', [])
        parsed = []
        for rank, item in enumerate(items, start=1):
            target = item.get('target', {})
            qid = target.get('id', '')
            title = target.get('title', '').replace('|', '-').replace('\n', ' ').strip()
            detail_text = item.get('detail_text', '').replace('|', '-')
            excerpt = target.get('excerpt', '').replace('|', '-').replace('\n', ' ').strip()
            short_excerpt = excerpt[:150] + '...' if len(excerpt) > 150 else excerpt
            url = f'https://www.zhihu.com/question/{qid}' if qid else ''

            parsed.append({
                'rank': rank,
                'id': qid,
                'title': title,
                'url': url,
                'heat': detail_text,
                'answer_count': target.get('answer_count', 0),
                'follower_count': target.get('follower_count', 0),
                'comment_count': target.get('comment_count', 0),
                'excerpt': excerpt,
                'short_excerpt': short_excerpt,
                'raw': item,
            })
        return parsed

    @classmethod
    def _write_md_for_date(cls, loc: str, items: RAW_DATA_T) -> None:
        md_str = '# 知乎热榜 (Zhihu Hot List)\n\n'
        md_str += '| 排名 | 问题 / 话题 | 热度 | 回答数 | 关注数 | 摘要 |\n'
        md_str += '| --- | --- | --- | --- | --- | --- |\n'

        for item in items:
            title_link = f'[{item["title"]}]({item["url"]})' if item["url"] else item["title"]
            md_str += f'| {item["rank"]} | {title_link} | {item["heat"]} | {item["answer_count"]} | {item["follower_count"]} | {item["short_excerpt"]} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        items = cls.get_hot_list()
        write_raw_data(items, path.join(loc, 'hot_list.json'))
        cls._write_md_for_date(loc, items)
