from typing import Dict, List, Any, Optional
from os import path
from datetime import datetime, timedelta
import requests

from apis.base import BaseApi
from writer import write_raw_data, write_md


class WikipediaAPI(BaseApi):
    LOC = 'Wikipedia'
    BASE_URL = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access'
    WIKI_HEADERS = {
        'User-Agent': 'trend-archive/1.0 (https://github.com/rip-tyang/trend-archive; bot@example.com)',
    }
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'top_pageviews.json',
        'README.md',
    ]

    @classmethod
    def get_top_pageviews(cls, target_date_str: Optional[str] = None, limit: int = 100) -> RAW_DATA_T:
        """
        Fetch top pageviews from Wikimedia REST API.
        If target_date_str is None, defaults to yesterday (since current day pageviews are still finalizing).
        If fetching the specified date yields 404 (not yet available), falls back to previous days.
        """
        if target_date_str:
            try:
                base_dt = datetime.strptime(target_date_str, '%Y-%m-%d')
            except ValueError:
                base_dt = datetime.today()
        else:
            base_dt = datetime.today()

        # Try target date, then up to 2 days prior if stats not yet compiled
        candidate_dates = [
            base_dt,
            base_dt - timedelta(days=1),
            base_dt - timedelta(days=2),
        ]

        last_error = None
        for dt in candidate_dates:
            date_path = dt.strftime('%Y/%m/%d')
            url = f'{cls.BASE_URL}/{date_path}'
            try:
                json_data = cls._get_json(url, headers=cls.WIKI_HEADERS)
                items = json_data.get('items', [])
                if items:
                    raw_articles = items[0].get('articles', [])
                    return cls._parse_articles(raw_articles, limit=limit)
            except Exception as e:
                last_error = e
                continue

        raise ValueError(f'Failed to fetch Wikipedia pageviews after fallback attempts: {last_error}')

    @classmethod
    def _parse_articles(cls, raw_articles: List[Dict[str, Any]], limit: int = 100) -> RAW_DATA_T:
        parsed = []
        for item in raw_articles[:limit]:
            article_raw = item.get('article', '')
            title = article_raw.replace('_', ' ').replace('|', '-')
            views = item.get('views', 0)
            rank = item.get('rank', len(parsed) + 1)
            url = f'https://en.wikipedia.org/wiki/{article_raw}' if article_raw else ''

            parsed.append({
                'rank': rank,
                'article': article_raw,
                'title': title,
                'views': views,
                'url': url,
            })
        return parsed

    @classmethod
    def _write_md_for_date(cls, loc: str, articles: RAW_DATA_T) -> None:
        md_str = '# Wikipedia Top Pageviews (English)\n\n'
        md_str += '| Rank | Article | Daily Pageviews | Link |\n'
        md_str += '| --- | --- | --- | --- |\n'

        for item in articles:
            title_link = f'[{item["title"]}]({item["url"]})' if item["url"] else item["title"]
            views_str = f'{item["views"]:,}' if isinstance(item["views"], int) else str(item["views"])
            view_link = f'[Article]({item["url"]})' if item["url"] else '-'
            md_str += f'| {item["rank"]} | {title_link} | {views_str} | {view_link} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        date_str = path.basename(loc)
        articles = cls.get_top_pageviews(target_date_str=date_str)
        write_raw_data(articles, path.join(loc, 'top_pageviews.json'))
        cls._write_md_for_date(loc, articles)
