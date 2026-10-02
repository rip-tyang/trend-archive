from typing import Dict, List, Any, Optional, Union
from bs4 import BeautifulSoup
from os import path
from datetime import date, datetime
import requests
import json
import sys

BASE_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Sec-Ch-Ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}


class BaseApi(object):
    BASE_PATH = './archive'
    LOC = ''
    EXPECTED_FILES: List[str] = []

    @classmethod
    def format_date(cls, target_date: Union[date, datetime, str, None] = None) -> str:
        if target_date is None:
            return date.today().isoformat()
        if isinstance(target_date, (date, datetime)):
            return target_date.strftime('%Y-%m-%d')
        return str(target_date)

    @classmethod
    def get_archive_dir(cls, target_date: Union[date, datetime, str, None] = None) -> str:
        date_str = cls.format_date(target_date)
        return path.join(cls.BASE_PATH, cls.LOC, date_str)

    @classmethod
    def has_data(cls, target_date: Union[date, datetime, str, None] = None) -> bool:
        loc = cls.get_archive_dir(target_date)
        if not path.exists(loc):
            return False
        if cls.EXPECTED_FILES:
            return all(path.exists(path.join(loc, f)) for f in cls.EXPECTED_FILES)
        return path.exists(path.join(loc, 'README.md'))

    @classmethod
    def archive_for_date(cls, target_date: Union[date, datetime, str, None] = None, force: bool = False) -> None:
        date_str = cls.format_date(target_date)
        loc = cls.get_archive_dir(target_date)
        if not force and cls.has_data(target_date):
            print(f'[{cls.LOC}] Data already exists for {date_str}, skipping fetch.')
            return
        cls._archive_for_date(loc)

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        raise NotImplementedError

    @classmethod
    def archive_for_today(cls, force: bool = False) -> None:
        cls.archive_for_date(date.today(), force=force)

    @classmethod
    def _get(cls, url: str, session: requests.Session = None) -> str:
        res = session.get(url) if session else requests.get(url, headers=BASE_REQUEST_HEADERS)
        print(f'getting {url}')
        if res.status_code != 200:
            raise ValueError(f'Status code: {res.status_code}\n Content: {res.text}')
        return res.text

    @classmethod
    def _get_json(cls, url: str, session: requests.Session = None) -> Dict[str, Any]:
        result = cls._get(url, session)
        try:
            return json.loads(result)
        except json.decoder.JSONDecodeError as e:
            print(f"Failed to decode JSON from {url}: {e}\nResponse: {result[:500]}", file=sys.stderr)
            raise

    @classmethod
    def _get_parsed_html(cls, url: str, session: requests.Session = None) -> BeautifulSoup:
        result = cls._get(url, session)
        return BeautifulSoup(result, 'html.parser')
