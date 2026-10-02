from typing import Dict, List, Any
from os import path

from apis.base import BaseApi
from writer import write_raw_data, write_md


class HuggingFaceAPI(BaseApi):
    LOC = 'HuggingFace'
    BASE_URL = 'https://huggingface.co'
    MOST_TRENDING_MODEL = 'models?sort=trending'
    MOST_TRENDING_DATASET = 'datasets?sort=trending'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'trending_model.json',
        'trending_dataset.json',
        'README.md',
    ]

    @classmethod
    def get_trending_model(cls) -> RAW_DATA_T:
        soup = cls._get_parsed_html(f"{cls.BASE_URL}/{cls.MOST_TRENDING_MODEL}")
        articles = soup.find_all('article')
        trending = []
        for article in articles:
            title = article.find('header').text.strip()
            desc = article.find('div').find('div', class_='items-center')
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
                'last_modified': texts[1] if viewer else texts[0],
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
    def _archive_for_date(cls, loc: str) -> None:
        trending_model = cls.get_trending_model()
        trending_dataset = cls.get_trending_dataset()
        write_raw_data(trending_model, path.join(loc, 'trending_model.json'))
        write_raw_data(trending_dataset, path.join(loc, 'trending_dataset.json'))
        cls._write_md_for_date(loc, trending_model, trending_dataset)
