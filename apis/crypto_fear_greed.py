from typing import Dict, List, Any
from os import path
from datetime import datetime

from apis.base import BaseApi
from writer import write_raw_data, write_md


class CryptoFearGreedAPI(BaseApi):
    LOC = 'CryptoFearGreed'
    BASE_URL = 'https://api.alternative.me/fng/?limit=30'
    RAW_DATA_T = Dict[str, Any]
    EXPECTED_FILES = [
        'fng.json',
        'README.md',
    ]

    @classmethod
    def get_index_data(cls) -> RAW_DATA_T:
        return cls._get_json(cls.BASE_URL)

    @classmethod
    def _write_md_for_date(cls, loc: str, data: RAW_DATA_T) -> None:
        items = data.get('data', [])
        md_str = '# Crypto Fear & Greed Index\n\n'

        if items:
            latest = items[0]
            val = latest.get('value', 'N/A')
            classification = latest.get('value_classification', 'N/A')
            md_str += f'> **Current Sentiment**: **{classification}** (Score: **{val}** / 100)\n\n'

        md_str += '## Historical Trend (Last 30 Days)\n\n'
        md_str += '| Date | Score (0-100) | Classification |\n'
        md_str += '| --- | --- | --- |\n'

        for item in items:
            ts = item.get('timestamp')
            date_str = datetime.fromtimestamp(int(ts)).strftime('%Y-%m-%d') if ts else 'N/A'
            val = item.get('value', '')
            classification = item.get('value_classification', '')
            md_str += f'| {date_str} | {val} | {classification} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        data = cls.get_index_data()
        write_raw_data(data, path.join(loc, 'fng.json'))
        cls._write_md_for_date(loc, data)
