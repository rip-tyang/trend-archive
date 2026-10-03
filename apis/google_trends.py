from typing import Dict, List, Any
from os import path
import xml.etree.ElementTree as ET
import urllib.parse

from apis.base import BaseApi
from writer import write_raw_data, write_md


class GoogleTrendsAPI(BaseApi):
    LOC = 'GoogleTrends'
    BASE_URL = 'https://trends.google.com/trending/rss?geo=US'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'daily_searches.json',
        'README.md',
    ]

    @classmethod
    def get_daily_searches(cls) -> RAW_DATA_T:
        xml_content = cls._get(cls.BASE_URL)
        root = ET.fromstring(xml_content.encode('utf-8') if isinstance(xml_content, str) else xml_content)
        ns = {'ht': 'https://trends.google.com/trending/rss'}

        items = root.findall('.//item')
        results = []
        for rank, item in enumerate(items, start=1):
            title_elem = item.find('title')
            title = title_elem.text.strip().replace('|', '-') if title_elem is not None and title_elem.text else ''

            traffic_elem = item.find('ht:approx_traffic', ns)
            traffic = traffic_elem.text.strip() if traffic_elem is not None and traffic_elem.text else 'N/A'

            pub_date_elem = item.find('pubDate')
            pub_date = pub_date_elem.text.strip() if pub_date_elem is not None and pub_date_elem.text else ''

            picture_elem = item.find('ht:picture', ns)
            picture = picture_elem.text.strip() if picture_elem is not None and picture_elem.text else ''

            news_items = []
            for news in item.findall('ht:news_item', ns):
                t = news.find('ht:news_item_title', ns)
                u = news.find('ht:news_item_url', ns)
                s = news.find('ht:news_item_source', ns)
                news_title = t.text.strip().replace('|', '-') if t is not None and t.text else ''
                news_url = u.text.strip() if u is not None and u.text else ''
                news_source = s.text.strip().replace('|', '-') if s is not None and s.text else ''
                if news_title:
                    news_items.append({
                        'title': news_title,
                        'url': news_url,
                        'source': news_source,
                    })

            search_url = f'https://www.google.com/search?q={urllib.parse.quote(title)}' if title else ''

            results.append({
                'rank': rank,
                'title': title,
                'traffic': traffic,
                'pub_date': pub_date,
                'picture': picture,
                'url': search_url,
                'news_items': news_items,
            })
        return results

    @classmethod
    def _write_md_for_date(cls, loc: str, searches: RAW_DATA_T) -> None:
        md_str = '# Google Trends (Daily Searches)\n\n'
        md_str += '| Rank | Search Query | Search Volume | Top Headline | Source | Link |\n'
        md_str += '| --- | --- | --- | --- | --- | --- |\n'

        for item in searches:
            title_link = f'[{item["title"]}]({item["url"]})' if item["url"] else item["title"]
            if item["news_items"]:
                top_news = item["news_items"][0]
                headline = f'[{top_news["title"]}]({top_news["url"]})' if top_news["url"] else top_news["title"]
                source = top_news["source"]
            else:
                headline = '-'
                source = '-'

            search_link = f'[Google Search]({item["url"]})' if item["url"] else '-'
            md_str += f'| {item["rank"]} | {title_link} | {item["traffic"]} | {headline} | {source} | {search_link} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        searches = cls.get_daily_searches()
        write_raw_data(searches, path.join(loc, 'daily_searches.json'))
        cls._write_md_for_date(loc, searches)
