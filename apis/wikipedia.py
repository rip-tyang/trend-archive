from typing import Dict, List, Any, Optional, Union
from os import path
from datetime import date, datetime, timedelta

from apis.base import BaseApi
from writer import write_raw_data, write_md


class WikipediaAPI(BaseApi):
    LOC = 'Wikipedia'
    BASE_URL = 'https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia/all-access'
    WIKI_HEADERS = {
        'User-Agent': 'trend-archive/1.0 (https://github.com/rip-tyang/trend-archive; bot@example.com)',
    }
    BACKFILL_DAYS = 7
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'top_pageviews.json',
        'README.md',
    ]

    @classmethod
    def get_top_pageviews(cls, day: date, limit: int = 100) -> Optional[RAW_DATA_T]:
        """
        Fetch the top pageviews for a single day.
        Returns None if Wikimedia has not published that day yet (404).
        """
        url = f'{cls.BASE_URL}/{day.strftime("%Y/%m/%d")}'
        try:
            json_data = cls._get_json(url, headers=cls.WIKI_HEADERS)
        except ValueError as e:
            if 'Status code: 404' in str(e):
                return None
            raise
        items = json_data.get('items', [])
        if not items:
            return None
        return cls._parse_articles(items[0].get('articles', []), limit=limit)

    @classmethod
    def archive_for_date(cls, target_date: Union[date, datetime, str, None] = None, force: bool = False) -> None:
        """
        Pageviews for day D are published 1-3 days later and stay available afterwards,
        so each folder is named after the day the views are for (not the run date),
        and every run fills any missing day in the trailing BACKFILL_DAYS window.
        """
        run_day = datetime.strptime(cls.format_date(target_date), '%Y-%m-%d').date()
        window = [run_day - timedelta(days=offset) for offset in range(1, cls.BACKFILL_DAYS + 1)]
        for day in window:
            if not force and cls.has_data(day):
                continue
            articles = cls.get_top_pageviews(day)
            if articles is None:
                print(f'[{cls.LOC}] Pageviews for {day.isoformat()} not published yet.')
                continue
            loc = cls.get_archive_dir(day)
            write_raw_data(articles, path.join(loc, 'top_pageviews.json'))
            cls._write_md_for_date(loc, articles)

        if not any(cls.has_data(day) for day in window):
            raise ValueError(
                f'No Wikipedia pageviews published in the {cls.BACKFILL_DAYS} days before {run_day.isoformat()}'
            )

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
        md_str = f'# Wikipedia Top Pageviews (English) - {path.basename(loc)}\n\n'
        md_str += '| Rank | Article | Daily Pageviews | Link |\n'
        md_str += '| --- | --- | --- | --- |\n'

        for item in articles:
            title_link = f'[{item["title"]}]({item["url"]})' if item["url"] else item["title"]
            views_str = f'{item["views"]:,}' if isinstance(item["views"], int) else str(item["views"])
            view_link = f'[Article]({item["url"]})' if item["url"] else '-'
            md_str += f'| {item["rank"]} | {title_link} | {views_str} | {view_link} |\n'

        write_md(md_str, path.join(loc, 'README.md'))
