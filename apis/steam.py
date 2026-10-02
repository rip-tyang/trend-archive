from typing import Dict, List, Any
from os import path
from bs4 import BeautifulSoup

from apis.base import BaseApi
from writer import write_raw_data, write_md


class SteamAPI(BaseApi):
    LOC = 'Steam'
    MOST_PLAYED_URL = 'https://store.steampowered.com/charts/mostplayed'
    TOP_SELLERS_URL = 'https://store.steampowered.com/charts/topselling/global'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'most_played.json',
        'top_sellers.json',
        'README.md',
    ]

    @classmethod
    def get_most_played(cls) -> RAW_DATA_T:
        soup = cls._get_parsed_html(cls.MOST_PLAYED_URL)
        table = soup.find('table')
        if not table:
            raise ValueError('Steam most played table not found')
        rows = table.find_all('tr')[1:]
        results = []
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 6:
                rank = tds[1].text.strip()
                name = tds[2].text.strip().replace('|', '-')
                a_tag = tds[2].find('a')
                url = a_tag['href'].split('?')[0] if a_tag and a_tag.get('href') else ''
                price = tds[3].text.strip()
                current_players = tds[4].text.strip()
                peak_today = tds[5].text.strip()
                results.append({
                    'rank': rank,
                    'name': name,
                    'url': url,
                    'price': price,
                    'current_players': current_players,
                    'peak_today': peak_today,
                })
        return results

    @classmethod
    def get_top_sellers(cls) -> RAW_DATA_T:
        soup = cls._get_parsed_html(cls.TOP_SELLERS_URL)
        table = soup.find('table')
        if not table:
            raise ValueError('Steam top sellers table not found')
        rows = table.find_all('tr')[1:]
        results = []
        for row in rows:
            tds = row.find_all('td')
            if len(tds) >= 6:
                rank = tds[1].text.strip()
                name = tds[2].text.strip().replace('|', '-')
                a_tag = tds[2].find('a')
                url = a_tag['href'].split('?')[0] if a_tag and a_tag.get('href') else ''
                price = tds[3].text.strip()
                rank_change = tds[4].text.strip()
                weeks_on_chart = tds[5].text.strip()
                results.append({
                    'rank': rank,
                    'name': name,
                    'url': url,
                    'price': price,
                    'rank_change': rank_change,
                    'weeks_on_chart': weeks_on_chart,
                })
        return results

    @classmethod
    def _write_md_for_date(cls, loc: str, most_played: RAW_DATA_T, top_sellers: RAW_DATA_T) -> None:
        md_str = '# Steam Charts\n\n'

        md_str += '## Top Most Played Games\n\n'
        md_str += '| Rank | Game | Price | Current Players | Peak Today |\n'
        md_str += '| --- | --- | --- | --- | --- |\n'
        for item in most_played:
            link = f'[{item["name"]}]({item["url"]})' if item["url"] else item["name"]
            md_str += f'| {item["rank"]} | {link} | {item["price"]} | {item["current_players"]} | {item["peak_today"]} |\n'

        md_str += '\n## Top Selling Games (Global)\n\n'
        md_str += '| Rank | Game | Price | Rank Change | Weeks on Chart |\n'
        md_str += '| --- | --- | --- | --- | --- |\n'
        for item in top_sellers:
            link = f'[{item["name"]}]({item["url"]})' if item["url"] else item["name"]
            md_str += f'| {item["rank"]} | {link} | {item["price"]} | {item["rank_change"]} | {item["weeks_on_chart"]} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        most_played = cls.get_most_played()
        top_sellers = cls.get_top_sellers()
        write_raw_data(most_played, path.join(loc, 'most_played.json'))
        write_raw_data(top_sellers, path.join(loc, 'top_sellers.json'))
        cls._write_md_for_date(loc, most_played, top_sellers)
