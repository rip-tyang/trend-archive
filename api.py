from typing import Dict, List, Any

from bs4 import BeautifulSoup
from os import path
from datetime import date
from time import sleep
import requests
import json
import re

from writer import write_raw_data, write_md

class BaseApi(object):
    BASE_PATH = './archive'

    @classmethod
    def _get(cls, url: str) -> str:
        res = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        })
        print(f'getting {url}')
        if res.status_code != 200:
            raise ValueError(f'Status code: {res.status_code}\n Content: {res.text}')
        return res.text

    @classmethod
    def _get_json(cls, url: str) -> Dict[str, Any]:
        try:
            result = cls._get(url)
            return json.loads(result)
        except json.decoder.JSONDecodeError as e:
            print(e)
            print(result)

    @classmethod
    def _get_parsed_html(cls, url: str) -> BeautifulSoup:
        result = cls._get(url)
        return BeautifulSoup(result, 'html.parser')

    @classmethod
    def archive_for_today(cls) -> None:
        raise NotImplementedError
class BilibiliApi(BaseApi):
    LOC = 'Bilibili'
    NAP_TIME = .5
    BASE_URL = 'https://api.bilibili.com'
    RAW_DATA_T = List[Dict[str, Any]]

    @classmethod
    def _get_highest_ranked(cls) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/web-interface/ranking'
        return cls._get_data_list(url)

    @classmethod
    def _get_most_popular(cls) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/web-interface/popular'
        return cls._get_data_list(url)

    @classmethod
    def _get_tag(cls, aid) -> RAW_DATA_T:
        url = f'{cls.BASE_URL}/x/tag/archive/tags?aid={aid}'
        return cls._get_data(url)

    @classmethod
    def _get_data(cls, url: str) -> RAW_DATA_T:
        json_data = cls._get_json(url)
        raw_data_list = json_data['data']
        return raw_data_list

    @classmethod
    def _get_data_list(cls, url: str) -> RAW_DATA_T:
        json_data = cls._get_json(url)
        raw_data_list = json_data['data']['list']
        return raw_data_list

    @classmethod
    def _get_tags(cls, aids: List[str]) -> None:
        all_tags = {}
        for aid in aids:
            sleep(cls.NAP_TIME)
            tag_list = BilibiliApi._get_tag(aid)
            for tag in tag_list:
                if tag['tag_id'] in all_tags:
                    all_tags[tag['tag_id']]['day_count'] += 1
                else:
                    all_tags[tag['tag_id']] = {'data': tag, 'day_count': 1}
        return all_tags

    @classmethod
    def _generate_md_top_list(cls, raw_data: RAW_DATA_T) -> str:
        res = []
        for video in raw_data:
            line = '1. '
            url = f'https://www.bilibili.com/video/{video["bvid"]}'
            line += f'[{video["title"]}]({url})'
            res.append(line)
        return '\n'.join(res)

    @classmethod
    def generate_md_table_row(cls, row: List[Any]) -> str:
        return f'| {" | ".join(row)} |\n'

    @classmethod
    def _generate_tag_distribution(cls, raw_tags: RAW_DATA_T) -> str:
        summary = []
        for _, tag in raw_tags.items():
            name = tag['data']['tag_name']
            count = str(tag['day_count'])
            summary.append((name, count))

        summary.sort(key=lambda x: int(x[1]), reverse=True)

        summary_header = ['Tag', 'Count']
        summary_md = ''
        summary_md += cls.generate_md_table_row(summary_header)
        summary_md += cls.generate_md_table_row(['---'] * len(summary_header))
        for row in summary:
            summary_md += cls.generate_md_table_row(row)

        return summary_md

    @classmethod
    def _write_md_for_date(
        cls, 
        loc: str, 
        most_popular: RAW_DATA_T, 
        highest_ranked: RAW_DATA_T, 
        most_popular_tags: RAW_DATA_T, 
        highest_ranked_tags: RAW_DATA_T
    ) -> None:
        md_str = '# Top List\n'
        md_str += '## Highest Ranked Videos\n'
        md_str += cls._generate_md_top_list(highest_ranked)
        md_str += '\n\n'
        md_str += '## Most Popular Videos\n'
        md_str += cls._generate_md_top_list(most_popular)

        md_str += '\n\n'
        md_str += '# Tag Distribution\n'
        md_str += '## Highest Ranked Videos\n'
        md_str += '\n\n'
        md_str += cls._generate_tag_distribution(highest_ranked_tags)
        md_str += '\n\n'
        md_str += '## Most Popular Videos\n'
        md_str += cls._generate_tag_distribution(most_popular_tags)

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def archive_for_today(cls) -> None:
        loc = path.join(cls.BASE_PATH, cls.LOC, date.today().isoformat())
        most_popular_data = cls._get_most_popular()
        most_popular_aids = (video['aid'] for video in most_popular_data)
        most_popular_tags = cls._get_tags(most_popular_aids)
        write_raw_data(most_popular_data, path.join(loc, 'Raw', 'most_popular.json'))
        write_raw_data(most_popular_tags, path.join(loc, 'Tags', 'most_popular.json'))

        highest_ranked_data = cls._get_highest_ranked()
        highest_ranked_aids = (video['aid'] for video in highest_ranked_data)
        highest_ranked_tags = cls._get_tags(highest_ranked_aids)
        write_raw_data(highest_ranked_data, path.join(loc, 'Raw', 'highest_ranked.json'))
        write_raw_data(highest_ranked_tags, path.join(loc, 'Tags', 'highest_ranked.json'))

        cls._write_md_for_date(loc, most_popular_data, highest_ranked_data, most_popular_tags, highest_ranked_tags)

class GithubAPI(BaseApi):
    LOC = 'Github'
    BASE_URL = 'https://github.com'
    RAW_DATA_T = List[Dict[str, Any]]

    @classmethod
    def get_trending(cls) -> RAW_DATA_T:
        soup = cls._get_parsed_html(f"{cls.BASE_URL}/trending")
        articles = soup.find_all('article', class_='Box-row')
        trending_repos = []
        for article in articles:
            title = re.sub(r'\s+', '', article.find('h2').text)
            url = f"{cls.BASE_URL}/{article.find('h2').find('a')['href']}"

            description_tag = article.find('p')
            description = description_tag.text.strip() if description_tag else ''

            language_tag = article.find(attrs={'itemprop': 'programmingLanguage'})
            language = language_tag.text.strip() if language_tag else ''

            stars_tag = article.find('a', href=re.compile(r'/stargazers$'))
            stars = stars_tag.text.strip() if stars_tag else ''

            forks_tag = article.find('a', href=re.compile(r'/forks$'))
            forks = forks_tag.text.strip() if forks_tag else ''


            contributors_tag = article.find_all('a', attrs={'data-hovercard-type': 'user'})
            contributors = []
            for contributor_tag in contributors_tag:
                img_tag = contributor_tag.find('img')
                name = img_tag['alt'].lstrip('@')
                url = f"{cls.BASE_URL}/{name}"
                avatar = img_tag['src']
                contributors.append({
                    'name': name,
                    'url': url,
                    'avatar': avatar,
                }),

            trending_repos.append({
                'title': title,
                'url': url,
                'description': description,
                'language': language,
                'stars': stars,
                'forks': forks,
                'contributors': contributors,
            })
        return trending_repos

    @classmethod
    def _write_md_for_date(
        cls, 
        loc: str, 
        trending_repos: RAW_DATA_T, 
    ) -> None:
        md_str = '# Trending\n'
        md_str += '| Repository | Description | Language | Stars | Forks |\n'
        md_str += '| --- | --- | --- | --- | --- |\n'
        for repo in trending_repos:
            md_str += f'| [{repo["title"]}]({repo["url"]}) | {repo["description"]} | {repo["language"]} | {repo["stars"]} | {repo["forks"]} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def archive_for_today(cls) -> None:
        loc = path.join(cls.BASE_PATH, cls.LOC, date.today().isoformat())
        trending_repos = cls.get_trending()
        write_raw_data(trending_repos, path.join(loc, 'trending.json'))
        cls._write_md_for_date(loc, trending_repos)

class YahooFinanceAPI(BaseApi):
    LOC = 'Stock'
    BASE_URL = 'https://finance.yahoo.com'
    MOST_ACTIVE_PATH = 'markets/stocks/most-active/?start=0&count=200'
    RAW_DATA_T = List[Dict[str, Any]]

    @classmethod
    def get_trending(cls) -> RAW_DATA_T:
        soup = cls._get_parsed_html(f"{cls.BASE_URL}/{cls.MOST_ACTIVE_PATH}")
        data_table = soup.find('div', class_='table-container').find('table').find('tbody').find_all('tr')
        most_active = []
        for row in data_table:
            ticker = row.find('td', attrs={'data-testid-cell': 'ticker'}).text.strip()
            company = row.find('td', attrs={'data-testid-cell': 'companyshortname.raw'}).text.strip()
            intradayprice = row.find('td', attrs={'data-testid-cell': 'intradayprice'}).find('fin-streamer', attrs={'data-test': 'change'}).text.strip()
            intradaypricechange = row.find('td', attrs={'data-testid-cell': 'intradaypricechange'}).text.strip()
            percentchange = row.find('td', attrs={'data-testid-cell': 'percentchange'}).text.strip()
            dayvolume = row.find('td', attrs={'data-testid-cell': 'dayvolume'}).text.strip()
            avgdailyvol3m = row.find('td', attrs={'data-testid-cell': 'avgdailyvol3m'}).text.strip()
            intradaymarketcap = row.find('td', attrs={'data-testid-cell': 'intradaymarketcap'}).text.strip()
            peratio = row.find('td', attrs={'data-testid-cell': 'peratio.lasttwelvemonths'}).text.strip()
            year_range = row.find('td', attrs={'data-testid-cell': 'fiftyTwoWeekRange'}).find('div', class_='labels').find_all('span')
            year_range_low = year_range[0].text.strip()
            year_range_high = year_range[1].text.strip()

            most_active.append({
                'ticker': ticker,
                'company': company,
                'intradayprice': intradayprice,
                'intradaypricechange': intradaypricechange,
                'percentchange': percentchange,
                'dayvolume': dayvolume,
                'avgdailyvol3m': avgdailyvol3m,
                'intradaymarketcap': intradaymarketcap,
                'peratio': peratio,
                'year_range_low': year_range_low,
                'year_range_high': year_range_high,
            })
        return most_active

    @classmethod
    def _write_md_for_date(
        cls, 
        loc: str, 
        trending_repos: RAW_DATA_T, 
    ) -> None:
        md_str = '# Most Active\n'
        md_str += '| Symbol Name | Company | Price | Change | Change % | Volume | Avg Vol (3M) | Market Cap | P/E Ratio (TTM) |  52 Wk Low | 52 Wk High |\n'
        md_str += '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n'
        for repo in trending_repos:
            md_str += f'| {repo["ticker"]} | {repo["company"]} | {repo["intradayprice"]} | {repo["intradaypricechange"]} | {repo["percentchange"]} | {repo["dayvolume"]} | {repo["avgdailyvol3m"]} | {repo["intradaymarketcap"]} | {repo["peratio"]} | {repo["year_range_low"]} | {repo["year_range_high"]} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def archive_for_today(cls) -> None:
        loc = path.join(cls.BASE_PATH, cls.LOC, date.today().isoformat())
        trending_repos = cls.get_trending()
        write_raw_data(trending_repos, path.join(loc, 'trending.json'))
        cls._write_md_for_date(loc, trending_repos)

class HuggingFaceAPI(BaseApi):
    LOC = 'HuggingFace'
    BASE_URL = 'https://huggingface.co'
    MOST_TRENDING_MODEL = 'models?sort=trending'
    MOST_TRENDING_DATASET = 'datasets?sort=trending'
    RAW_DATA_T = List[Dict[str, Any]]

    @classmethod
    def get_trending_model(cls) -> RAW_DATA_T:
        soup = cls._get_parsed_html(f"{cls.BASE_URL}/{cls.MOST_TRENDING_MODEL}")
        articles = soup.find_all('article')
        trending = []
        for article in articles:
            title = article.find('header').text.strip()
            desc = article.find('div').find('div')
            texts = [t.replace('\n', '').replace('\t', '').strip() for t in desc.text.split('•')]
            has_inference = '' in texts
            texts = [t for t in texts if t != '']
            item = {
                'title': title,
                'category': texts[0],
                'model_size': texts[-4] if len(texts) > 4 else '',
                'last_modified': texts[-3] if len(texts) > 3 else texts[-2],
                'download': texts[-2] if len(texts) > 3 else '',
                'like': texts[-1],
                'inference_provider': has_inference,
            }
            trending.append(item)
        return trending

    @classmethod
    def get_trending_dataset(cls) -> RAW_DATA_T:
        soup = cls._get_parsed_html(f"{cls.BASE_URL}/{cls.MOST_TRENDING_DATASET}")
        articles = soup.find_all('article')
        trending = []
        for article in articles:
            title = article.find('header').text.strip()
            desc = article.find('div').find('div')
            texts = [t.replace('\n', '').replace('\t', '').strip() for t in desc.text.split('•')]
            viewer = len(texts) > 3
            item = {
                'title': title,
                'last_modified': texts[-4] if viewer else texts[-3],
                'views': texts[-3] if viewer else '',
                'download': texts[-2],
                'like': texts[-1],
                'viewer': viewer,
            }
            trending.append(item)
        return trending

    @classmethod
    def _write_md_for_date(
        cls, 
        loc: str, 
        trending_model: RAW_DATA_T, 
        trending_dataset: RAW_DATA_T, 
    ) -> None:
        md_str = '# Most trending models \n'
        md_str += '| Model Name | Category | Model Size | Last Modified | Download | Like | Inference Provider |\n'
        md_str += '| --- | --- | --- | --- | --- | --- | --- |\n'
        for repo in trending_model:
            md_str += f'| {repo["title"]} | {repo["category"]} | {repo["model_size"]} | {repo["last_modified"]} | {repo["download"]} | {repo["like"]} | {repo["inference_provider"]} |\n'

        md_str += '# Most trending datasets \n'
        md_str += '| Dataset Name | Last Modified | Views | Download | Like | Viewer |\n'
        md_str += '| --- | --- | --- | --- | --- | --- |\n'
        for repo in trending_dataset:
            md_str += f'| {repo["title"]} | {repo["last_modified"]} | {repo["views"]} | {repo["download"]} | {repo["like"]} | {repo["viewer"]} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def archive_for_today(cls) -> None:
        loc = path.join(cls.BASE_PATH, cls.LOC, date.today().isoformat())
        trending_model = cls.get_trending_model()
        trending_dataset = cls.get_trending_dataset()
        write_raw_data(trending_model, path.join(loc, 'trending_model.json'))
        write_raw_data(trending_dataset, path.join(loc, 'trending_dataset.json'))
        cls._write_md_for_date(loc, trending_model, trending_dataset)

if __name__ == '__main__':
    HuggingFaceAPI.archive_for_today()