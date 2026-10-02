from typing import Dict, List, Any
from os import path

from apis.base import BaseApi
from writer import write_raw_data, write_md


class CoinGeckoAPI(BaseApi):
    LOC = 'CoinGecko'
    BASE_URL = 'https://api.coingecko.com/api/v3/search/trending'
    RAW_DATA_T = Dict[str, Any]
    EXPECTED_FILES = [
        'trending.json',
        'README.md',
    ]

    @classmethod
    def get_trending(cls) -> RAW_DATA_T:
        return cls._get_json(cls.BASE_URL)

    @classmethod
    def _write_md_for_date(cls, loc: str, data: RAW_DATA_T) -> None:
        md_str = '# CoinGecko Trending\n\n'

        # 1. Trending Coins
        coins = data.get('coins', [])
        md_str += '## Trending Coins\n\n'
        md_str += '| Rank | Name | Symbol | Market Cap Rank | Price (USD) | 24h Change | 24h Volume | Market Cap |\n'
        md_str += '| --- | --- | --- | --- | --- | --- | --- | --- |\n'
        for rank, coin_wrapper in enumerate(coins, start=1):
            item = coin_wrapper.get('item', {})
            name = item.get('name', '')
            symbol = item.get('symbol', '').upper()
            slug = item.get('slug', '')
            coin_link = f'[{name}](https://www.coingecko.com/en/coins/{slug})' if slug else name
            mcap_rank = item.get('market_cap_rank') or 'N/A'
            d = item.get('data', {})
            price = d.get('price', 'N/A')
            if isinstance(price, (int, float)):
                price_str = f'${price:,.4f}' if price < 1 else f'${price:,.2f}'
            else:
                price_str = str(price)

            change_pct = d.get('price_change_percentage_24h', {})
            usd_change = change_pct.get('usd') if isinstance(change_pct, dict) else None
            change_str = f'{usd_change:+.2f}%' if isinstance(usd_change, (int, float)) else 'N/A'
            volume = d.get('total_volume', 'N/A')
            mcap = d.get('market_cap', 'N/A')

            md_str += f'| {rank} | {coin_link} | {symbol} | {mcap_rank} | {price_str} | {change_str} | {volume} | {mcap} |\n'

        # 2. Trending NFTs
        nfts = data.get('nfts', [])
        if nfts:
            md_str += '\n## Trending NFTs\n\n'
            md_str += '| Rank | Name | Symbol | Floor Price | 24h Volume |\n'
            md_str += '| --- | --- | --- | --- | --- |\n'
            for rank, nft in enumerate(nfts, start=1):
                name = nft.get('name', '')
                symbol = nft.get('symbol', '').upper()
                d = nft.get('data', {})
                floor_price = d.get('floor_price', 'N/A')
                h24_vol = d.get('h24_volume', 'N/A')
                md_str += f'| {rank} | {name} | {symbol} | {floor_price} | {h24_vol} |\n'

        # 3. Trending Categories
        categories = data.get('categories', [])
        if categories:
            md_str += '\n## Trending Categories\n\n'
            md_str += '| Rank | Category | 24h Market Cap Change | 24h Volume |\n'
            md_str += '| --- | --- | --- | --- |\n'
            for rank, cat in enumerate(categories, start=1):
                name = cat.get('name', '')
                d = cat.get('data', {})
                vol = d.get('total_volume')
                vol_str = f'${vol:,.2f}' if isinstance(vol, (int, float)) else str(vol or 'N/A')
                mcap_change = cat.get('market_cap_1h_change')
                mcap_change_str = f'{mcap_change:+.2f}%' if isinstance(mcap_change, (int, float)) else 'N/A'
                md_str += f'| {rank} | {name} | {mcap_change_str} | {vol_str} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        data = cls.get_trending()
        write_raw_data(data, path.join(loc, 'trending.json'))
        cls._write_md_for_date(loc, data)
