from typing import Dict, List, Any
from os import path
import sys
import time

from apis.base import BaseApi
from reader import read_json
from writer import write_raw_data, write_md


class AppleChartsAPI(BaseApi):
    LOC = 'AppleCharts'
    BASE_URL = 'https://rss.applemarketingtools.com/api/v2/{country}/{feed}.json'
    COUNTRY = 'us'
    LIMIT = 100
    FEED_DELAY_SECONDS = 2
    RAW_DATA_T = List[Dict[str, Any]]
    # file name -> (section title, feed path without limit)
    FEEDS = {
        'top_free_apps': ('Top Free Apps', 'apps/top-free/{limit}/apps'),
        'top_paid_apps': ('Top Paid Apps', 'apps/top-paid/{limit}/apps'),
        'top_songs': ('Most Played Songs', 'music/most-played/{limit}/songs'),
        'top_albums': ('Most Played Albums', 'music/most-played/{limit}/albums'),
        'top_podcasts': ('Top Podcasts', 'podcasts/top/{limit}/podcasts'),
        'top_free_books': ('Top Free Books', 'books/top-free/{limit}/books'),
        'top_paid_books': ('Top Paid Books', 'books/top-paid/{limit}/books'),
    }
    EXPECTED_FILES = [f'{name}.json' for name in FEEDS] + ['README.md']

    @classmethod
    def get_feed(cls, feed: str) -> RAW_DATA_T:
        url = cls.BASE_URL.format(country=cls.COUNTRY, feed=feed.format(limit=cls.LIMIT))
        results = cls._get_json(url).get('feed', {}).get('results', [])
        return [
            {
                'rank': rank,
                'id': r.get('id'),
                'name': r.get('name'),
                'artistName': r.get('artistName'),
                'releaseDate': r.get('releaseDate'),
                'genres': [g.get('name') for g in r.get('genres') or [] if g.get('name')],
                'url': r.get('url'),
            }
            for rank, r in enumerate(results, start=1)
        ]

    @staticmethod
    def _md_escape(s: Any) -> str:
        return str(s or '').replace('|', '\\|')

    @classmethod
    def _write_md_for_date(cls, loc: str, charts: Dict[str, RAW_DATA_T]) -> None:
        md_str = f'# Apple Charts ({cls.COUNTRY.upper()})\n\n'
        for name, (title, _) in cls.FEEDS.items():
            md_str += f'## {title}\n\n'
            md_str += '| Rank | Name | Artist / Developer | Genre |\n'
            md_str += '| --- | --- | --- | --- |\n'
            for item in charts[name]:
                item_name = cls._md_escape(item['name'])
                link = f'[{item_name}]({item["url"]})' if item['url'] else item_name
                genre = item['genres'][0] if item['genres'] else '-'
                md_str += f'| {item["rank"]} | {link} | {cls._md_escape(item["artistName"])} | {genre} |\n'
            md_str += '\n'
        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        # Save every feed that succeeds; README.md is only written once all feeds are in,
        # so a partial day is not marked complete. A rerun of a partial day reuses the
        # feeds already saved and only fetches the missing ones.
        is_partial_day = not path.exists(path.join(loc, 'README.md'))
        charts, failed = {}, []
        for name, (_, feed) in cls.FEEDS.items():
            feed_path = path.join(loc, f'{name}.json')
            if is_partial_day and path.exists(feed_path):
                charts[name] = read_json(feed_path)
                continue
            if charts or failed:
                time.sleep(cls.FEED_DELAY_SECONDS)  # space out requests to avoid Apple's rate limit
            try:
                charts[name] = cls.get_feed(feed)
            except Exception as e:
                print(f'[{cls.LOC}] Failed to fetch {name}: {e}', file=sys.stderr)
                failed.append(name)
                continue
            write_raw_data(charts[name], feed_path)
        if failed:
            raise ValueError(f'Failed to fetch Apple feed(s): {", ".join(failed)}')
        cls._write_md_for_date(loc, charts)
