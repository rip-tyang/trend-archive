from typing import Dict, List, Any
from os import path
import re

from apis.base import BaseApi
from writer import write_raw_data, write_md


class GithubAPI(BaseApi):
    LOC = 'Github'
    BASE_URL = 'https://github.com'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'trending.json',
        'README.md',
    ]

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
                avatar = img_tag['src']
                contributors.append({
                    'name': name,
                    'url': url,
                    'avatar': avatar,
                })

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
    def _archive_for_date(cls, loc: str) -> None:
        trending_repos = cls.get_trending()
        write_raw_data(trending_repos, path.join(loc, 'trending.json'))
        cls._write_md_for_date(loc, trending_repos)
