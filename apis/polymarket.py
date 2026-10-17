from typing import Dict, List, Any
from os import path
import json

from apis.base import BaseApi
from writer import write_raw_data, write_md


class PolymarketAPI(BaseApi):
    LOC = 'Polymarket'
    BASE_URL = 'https://gamma-api.polymarket.com/events'
    EVENT_URL = 'https://polymarket.com/event/{slug}'
    MAX_MARKETS = 10
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'top_events.json',
        'README.md',
    ]
    EVENT_FIELDS = [
        'id', 'slug', 'title', 'startDate', 'endDate', 'volume', 'volume24hr',
        'volume1wk', 'liquidity', 'openInterest', 'commentCount', 'negRisk', 'closed',
    ]
    MARKET_FIELDS = [
        'id', 'question', 'groupItemTitle', 'slug', 'volume24hr', 'volumeNum',
        'lastTradePrice', 'bestBid', 'bestAsk', 'oneDayPriceChange', 'oneWeekPriceChange', 'closed',
    ]

    @classmethod
    def get_top_events(cls, limit: int = 50) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}?order=volume24hr&ascending=false&closed=false&limit={limit}'
        return [cls._parse_event(e) for e in cls._get_json(url)]

    @staticmethod
    def _load_list(value: Any) -> List[Any]:
        # outcomes / outcomePrices come back as JSON-encoded strings
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.decoder.JSONDecodeError:
                return []
        return value or []

    @classmethod
    def _parse_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        parsed = {k: event.get(k) for k in cls.EVENT_FIELDS}
        parsed['tags'] = [t.get('label') for t in event.get('tags') or [] if t.get('label')]
        markets = []
        for m in event.get('markets') or []:
            market = {k: m.get(k) for k in cls.MARKET_FIELDS}
            market['outcomes'] = cls._load_list(m.get('outcomes'))
            market['outcomePrices'] = [float(p) for p in cls._load_list(m.get('outcomePrices'))]
            markets.append(market)
        parsed['marketCount'] = len(markets)
        parsed['markets'] = sorted(markets, key=cls._market_sort_key(parsed))[:cls.MAX_MARKETS]
        return parsed

    @staticmethod
    def _market_sort_key(event: Dict[str, Any]):
        # Sports/esports events carry hundreds of prop markets, so only the top ones are kept.
        # negRisk events are mutually exclusive candidates: rank by Yes price; otherwise by volume.
        if event.get('negRisk'):
            return lambda m: -(m['outcomePrices'][0] if m['outcomePrices'] else 0)
        return lambda m: -float(m.get('volumeNum') or 0)

    @staticmethod
    def _md_escape(s: Any) -> str:
        return str(s or '').replace('|', '\\|').replace('\n', ' ')

    @staticmethod
    def _fmt_usd(v: Any) -> str:
        try:
            return f'${float(v):,.0f}'
        except (TypeError, ValueError):
            return 'N/A'

    @classmethod
    def _leading(cls, event: Dict[str, Any]) -> str:
        # markets are already sorted so the first one is the headline market
        markets = [m for m in event['markets'] if m['outcomePrices']]
        if not markets:
            return 'N/A'
        m = markets[0]
        label = m.get('groupItemTitle')
        if event.get('negRisk'):
            return f'{label or m.get("question")} ({m["outcomePrices"][0]:.0%})'
        price, outcome = max(zip(m['outcomePrices'], m['outcomes']))
        prefix = f'{label}: ' if label and len(markets) > 1 else ''
        return f'{prefix}{outcome} ({price:.0%})'

    @classmethod
    def _write_md_for_date(cls, loc: str, events: RAW_DATA_T) -> None:
        md_str = '# Polymarket Top Events by 24h Volume\n\n'
        md_str += '| Rank | Event | Leading | 24h Volume | Total Volume | Markets |\n'
        md_str += '| --- | --- | --- | --- | --- | --- |\n'
        for rank, e in enumerate(events, start=1):
            title = cls._md_escape(e['title'])
            link = f'[{title}]({cls.EVENT_URL.format(slug=e["slug"])})' if e.get('slug') else title
            md_str += (
                f'| {rank} | {link} | {cls._md_escape(cls._leading(e))} | {cls._fmt_usd(e["volume24hr"])} '
                f'| {cls._fmt_usd(e["volume"])} | {e["marketCount"]} |\n'
            )
        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        events = cls.get_top_events()
        write_raw_data(events, path.join(loc, 'top_events.json'))
        cls._write_md_for_date(loc, events)
