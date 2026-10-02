from typing import Dict, List, Any
from os import path
import json

from apis.base import BaseApi
from writer import write_raw_data, write_md


class YahooFinanceAPI(BaseApi):
    LOC = 'Stock'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'trending.json',
        'README.md',
    ]

    @classmethod
    def get_trending(cls) -> RAW_DATA_T:
        try: 
            return cls._get_json('https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=200&formatted=true&scrIds=MOST_ACTIVES&sortField=&sortType=&start=0&useRecordsResponse=true&fields=symbol%2CshortName&lang=en-US&region=US')['finance']['result'][0]['records']
        except ValueError as e:
            print(f'{e}, Failed to get via API, try parsing HTML...')
        soup = cls._get_parsed_html('https://finance.yahoo.com/markets/stocks/most-active/?start=0&count=200&guccounter=1')
        script_tags = soup.find_all('script')
        target_script = [script for script in script_tags if script.get('data-url') and 'MOST_ACTIVES' in script.get('data-url')]
        if len(target_script) != 1:
            raise ValueError('Cannot find target script')
        return json.loads(json.loads(target_script[0].text)['body'])['finance']['result'][0]['records']

    @classmethod
    def _write_md_for_date(
        cls, 
        loc: str, 
        trending_stocks: RAW_DATA_T, 
    ) -> None:
        md_str = '# Most Active\n'
        md_str += '| Symbol Name | Company | Price | Change | Change % | Volume | Avg Vol (3M) | Market Cap | P/E Ratio (TTM) | 52 Wk Change |  52 Wk Low | 52 Wk High |\n'
        md_str += '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
        for stock in trending_stocks:
            ticker = stock['ticker']
            company = stock['companyName']
            intradayprice = stock['regularMarketPrice']['raw']
            intradaypricechange = stock['regularMarketChange']['raw']
            percentchange = stock['regularMarketChangePercent']['raw']
            dayvolume = stock['regularMarketVolume']['raw']
            avgdailyvol3m = stock.get('avgDailyVol3m', {}).get('raw', 'N/A')
            intradaymarketcap = stock['marketCap']['raw']
            peratio = stock.get('peRatioLtm', {}).get('raw', 'N/A')
            year_change_precent = stock.get('fiftyTwoWeekChangePercent', {}).get('raw', 'N/A')
            year_range_low = stock.get('fiftyTwoWeekLow', {}).get('raw', 'N/A')
            year_range_high = stock.get('fiftyTwoWeekHigh', {}).get('raw', 'N/A')
            md_str += f'| {ticker} | {company} | {intradayprice} | {intradaypricechange} | {percentchange}% | {dayvolume} | {avgdailyvol3m} | {intradaymarketcap} | {peratio} | {year_change_precent}% | {year_range_low} | {year_range_high} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        trending_stocks = cls.get_trending()
        write_raw_data(trending_stocks, path.join(loc, 'trending.json'))
        cls._write_md_for_date(loc, trending_stocks)
