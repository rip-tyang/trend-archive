from typing import List, Any

import json
from datetime import date
from os import path
from argparse import ArgumentParser

from api import BilibiliApi
from reader import read_json
from writer import write_md

BASE_PATH = './archive'

def generate_md_top_list(raw_data: BilibiliApi.RAW_DATA_T) -> str:
    res = []
    for video in raw_data:
        line = '1. '
        url = f'https://www.bilibili.com/video/{video["bvid"]}'
        line += f'[{video["title"]}]({url})'
        res.append(line)
    return '\n'.join(res)


def generate_tag_distribution(raw_tags: BilibiliApi.RAW_DATA_T) -> str:
    summary = []
    for _, tag in raw_tags.items():
        name = tag['data']['tag_name']
        count = str(tag['day_count'])
        summary.append((name, count))

    summary.sort(key=lambda x: x[1], reverse=True)

    summary_header = ['Tag', 'Count']
    summary_md = ''
    summary_md += generate_md_table_row(summary_header)
    summary_md += generate_md_table_row(['---'] * len(summary_header))
    for row in summary:
        summary_md += generate_md_table_row(row)

    return summary_md


def generate_md_table_row(row: List[Any]) -> str:
    return f'| {" | ".join(row)} |\n'


def write_md_for_date(target_date: date):
    date_str = target_date.isoformat()
    loc = path.join(BASE_PATH, 'Bilibili', date_str)

    highest_ranked = read_json(path.join(loc, 'Raw', 'highest_ranked.json'))
    most_popular = read_json(path.join(loc, 'Raw', 'most_popular.json'))

    md_str = '# Top List\n'
    md_str += '## Highest Ranked Videos\n'
    md_str += generate_md_top_list(highest_ranked)
    md_str += '\n\n'
    md_str += '## Most Popular Videos\n'
    md_str += generate_md_top_list(most_popular)

    highest_ranked_tags = read_json(path.join(loc, 'Tags', 'highest_ranked.json'))
    most_popular_tags = read_json(path.join(loc, 'Tags', 'most_popular.json'))

    md_str += '\n\n'
    md_str += '# Tag Distribution\n'
    md_str += '## Highest Ranked Videos\n'
    md_str += '\n\n'
    md_str += generate_tag_distribution(highest_ranked_tags)
    md_str += '\n\n'
    md_str += '## Most Popular Videos\n'
    md_str += generate_tag_distribution(most_popular_tags)

    write_md(md_str, path.join(loc, 'README.md'))


if __name__ == '__main__':
    parser = ArgumentParser('Generate markdown from raw data')
    parser.add_argument('-d', '--date', type=date.fromisoformat, default=date.today().isoformat())
    args = parser.parse_args()

    write_md_for_date(args.date)
