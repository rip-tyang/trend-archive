import json
from datetime import date
from os import path, makedirs

from api import BilibiliApi
from writer import write_md, write_raw_videos

BASE_PATH = './archive'

def generate_md(raw_data: BilibiliApi.RAW_DATA_T) -> str:
    res = []
    for video in raw_data:
        line = '1. '
        url = f'https://www.bilibili.com/video/{video["bvid"]}'
        line += f'[{video["title"]}]({url})'
        res.append(line)
    return '\n'.join(res)


def summarize_highest_ranked(api: BilibiliApi, loc: str) -> BilibiliApi.RAW_DATA_T:
    highest_ranked = api.get_highest_ranked()
    write_raw_videos(highest_ranked, path.join(loc, 'highest_ranked_raw.json'))

    return highest_ranked


def summarize_most_popular(api: BilibiliApi, loc: str) -> BilibiliApi.RAW_DATA_T:
    most_popular = api.get_most_popular()
    write_raw_videos(most_popular, path.join(loc, 'most_popular'))

    return most_popular


def summarize_today():
    date_str = date.today().isoformat()
    loc = path.join(BASE_PATH, date_str)
    makedirs(loc, exist_ok=True)

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
