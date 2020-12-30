from typing import List

import json
from time import sleep
from datetime import date
from os import path

from api import BilibiliApi
from writer import write_md, write_raw_data

BASE_PATH = './archive'
NAP_TIME = .5

def generate_md(raw_data: BilibiliApi.RAW_DATA_T) -> str:
    res = []
    for video in raw_data:
        line = '1. '
        url = f'https://www.bilibili.com/video/{video["bvid"]}'
        line += f'[{video["title"]}]({url})'
        res.append(line)
    return '\n'.join(res)


def generate_md_table_row(row: List[Any]) -> str:
    return f'| {" | ".join(r for r in row)} |\n'


def summarize_tags(api: BilibiliApi, loc: str, name: str, aids: List[str]) -> BilibiliApi.RAW_DATA_T:
    all_tags = {}
    for aid in aids:
        sleep(NAP_TIME)
        tag_list = api.get_tag(aid)
        for tag in tag_list:
            if tag['tag_id'] in all_tags:
                all_tags[tag['tag_id']]['day_count'] += 1
            else:
                all_tags[tag['tag_id']] = {'data': tag, 'day_count': 1}
    write_raw_data(all_tags, path.join(loc, 'Tags', 'README.md'))

    summary = []
    for _, tag in all_tags.items():
        name = tag['data']['tag_name']
        count = tag['day_count']
        summary.append((name, count))

    sort(summary, key=lambda x: x[1], acending=False)


    summary_header = ['Tag', 'Count']
    summary_md = '# Tag Distribution\n'
    summary_md += generate_md_table_row(summary_header)
    summary_md += generate_md_table_row(['---'] * len(summary_header))
    for row in summary:
        summary_md += generate_md_table_row(row)
    write_md(summary_md, path.join(loc, 'Tags', name))

def summarize_highest_ranked(api: BilibiliApi, loc: str) -> BilibiliApi.RAW_DATA_T:
    highest_ranked = api.get_highest_ranked()
    write_raw_data(highest_ranked, path.join(loc, 'Raw', 'highest_ranked.json'))

    aids = [video['aid'] for video in highest_ranked]
    summarize_tags(api, loc, 'highest_ranked.json', aids)

    return highest_ranked


def summarize_most_popular(api: BilibiliApi, loc: str) -> BilibiliApi.RAW_DATA_T:
    most_popular = api.get_most_popular()
    write_raw_data(most_popular, path.join(loc, 'Raw', 'most_popular.json'))

    aids = (video['aid'] for video in most_popular)
    summarize_tags(api, loc, 'most_popular.json', aids)

    return most_popular


def summarize_today():
    date_str = date.today().isoformat()
    loc = path.join(BASE_PATH, 'Bilibili', date_str)

    api = BilibiliApi()
    highest_ranked = summarize_highest_ranked(api, loc)
    most_popular = summarize_most_popular(api, loc)

    md_str = '# Highest Ranked Videos\n'
    md_str += generate_md(highest_ranked)
    md_str += '\n\n'
    md_str += '# Most Popular Videos\n'
    md_str += generate_md(most_popular)
    write_md(md_str, path.join(loc, 'README.md'))


if __name__ == '__main__':
    summarize_today()
