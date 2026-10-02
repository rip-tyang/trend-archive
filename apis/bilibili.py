from typing import Dict, List, Any
from os import path
from time import sleep

from apis.base import BaseApi
from writer import write_raw_data, write_md


class BilibiliApi(BaseApi):
    LOC = 'Bilibili'
    NAP_TIME = .5
    BASE_URL = 'https://api.bilibili.com'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        path.join('Raw', 'most_popular.json'),
        path.join('Tags', 'most_popular.json'),
        path.join('Raw', 'highest_ranked.json'),
        path.join('Tags', 'highest_ranked.json'),
        'README.md',
    ]

    @classmethod
    def _get_highest_ranked(cls) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/web-interface/ranking'
        return cls._get_data_list(url)

    @classmethod
    def _get_most_popular(cls) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/web-interface/popular'
        return cls._get_data_list(url)

    @classmethod
    def _get_tag(cls, aid) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/tag/archive/tags?aid={aid}'
        return cls._get_data(url)

    @classmethod
    def _get_data(cls, url: str) -> RAW_DATA_T:
        json_data = cls._get_json(url)
        raw_data_list = json_data['data']
        return raw_data_list

    @classmethod
    def _get_data_list(cls, url: str) -> RAW_DATA_T:
        json_data = cls._get_json(url)
        raw_data_list = json_data['data']['list']
        return raw_data_list

    @classmethod
    def _get_tags(cls, aids: List[str]) -> Dict[str, Any]:
        all_tags = {}
        for aid in aids:
            sleep(cls.NAP_TIME)
            tag_list = BilibiliApi._get_tag(aid)
            for tag in tag_list:
                if tag['tag_id'] in all_tags:
                    all_tags[tag['tag_id']]['day_count'] += 1
                else:
                    all_tags[tag['tag_id']] = {'data': tag, 'day_count': 1}
        return all_tags

    @classmethod
    def _generate_md_top_list(cls, raw_data: RAW_DATA_T) -> str:
        res = []
        for video in raw_data:
            line = '1. '
            url = f'https://www.bilibili.com/video/{video["bvid"]}'
            line += f'[{video["title"]}]({url})'
            res.append(line)
        return '\n'.join(res)

    @classmethod
    def generate_md_table_row(cls, row: List[Any]) -> str:
        return f'| {" | ".join(row)} |\n'

    @classmethod
    def _generate_tag_distribution(cls, raw_tags: RAW_DATA_T) -> str:
        summary = []
        for _, tag in raw_tags.items():
            name = tag['data']['tag_name']
            count = str(tag['day_count'])
            summary.append((name, count))

        summary.sort(key=lambda x: int(x[1]), reverse=True)

        summary_header = ['Tag', 'Count']
        summary_md = ''
        summary_md += cls.generate_md_table_row(summary_header)
        summary_md += cls.generate_md_table_row(['---'] * len(summary_header))
        for row in summary:
            summary_md += cls.generate_md_table_row(row)

        return summary_md

    @classmethod
    def _write_md_for_date(
        cls, 
        loc: str, 
        most_popular: RAW_DATA_T, 
        highest_ranked: RAW_DATA_T, 
        most_popular_tags: RAW_DATA_T, 
        highest_ranked_tags: RAW_DATA_T
    ) -> None:
        md_str = '# Top List\n'
        md_str += '## Highest Ranked Videos\n'
        md_str += cls._generate_md_top_list(highest_ranked)
        md_str += '\n\n'
        md_str += '## Most Popular Videos\n'
        md_str += cls._generate_md_top_list(most_popular)

        md_str += '\n\n'
        md_str += '# Tag Distribution\n'
        md_str += '## Highest Ranked Videos\n'
        md_str += '\n\n'
        md_str += cls._generate_tag_distribution(highest_ranked_tags)
        md_str += '\n\n'
        md_str += '## Most Popular Videos\n'
        md_str += cls._generate_tag_distribution(most_popular_tags)

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        most_popular_data = cls._get_most_popular()
        most_popular_aids = [video['aid'] for video in most_popular_data]
        most_popular_tags = cls._get_tags(most_popular_aids)

        highest_ranked_data = cls._get_highest_ranked()
        highest_ranked_aids = [video['aid'] for video in highest_ranked_data]
        highest_ranked_tags = cls._get_tags(highest_ranked_aids)

        write_raw_data(most_popular_data, path.join(loc, 'Raw', 'most_popular.json'))
        write_raw_data(most_popular_tags, path.join(loc, 'Tags', 'most_popular.json'))
        write_raw_data(highest_ranked_data, path.join(loc, 'Raw', 'highest_ranked.json'))
        write_raw_data(highest_ranked_tags, path.join(loc, 'Tags', 'highest_ranked.json'))

        cls._write_md_for_date(loc, most_popular_data, highest_ranked_data, most_popular_tags, highest_ranked_tags)
