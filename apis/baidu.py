from typing import Dict, List, Any
from os import path
import re

from apis.base import BaseApi
from writer import write_raw_data, write_md


class BaiduAPI(BaseApi):
    LOC = 'Baidu'
    BASE_URL = 'https://top.baidu.com/board?tab=realtime'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'hot_search.json',
        'README.md',
    ]

    @classmethod
    def get_hot_search(cls) -> RAW_DATA_T:
        soup = cls._get_parsed_html(cls.BASE_URL)
        cards = soup.select('.category-wrap_iQLoo') or soup.find_all('div', class_=re.compile(r'category-wrap'))

        items = []
        for i, card in enumerate(cards):
            rank_elem = card.select_one('[class*="index_"]')
            rank_str = rank_elem.text.strip() if rank_elem else ''
            if not rank_str:
                rank_str = '置顶' if i == 0 else str(i)

            title_elem = card.select_one('.c-single-text-ellipsis') or card.select_one('[class*="title_"]') or card.select_one('a')
            title = title_elem.text.strip().replace('|', '-').replace('\n', ' ') if title_elem else ''

            link_elem = card.select_one('a')
            url = link_elem.get('href', '') if link_elem else ''
            if url and not url.startswith('http'):
                url = f'https://www.baidu.com{url}'

            heat_elem = card.select_one('[class*="hot-index_"]')
            heat = heat_elem.text.strip() if heat_elem else ''

            desc_elem = card.select_one('[class*="small_"]') or card.select_one('[class*="desc_"]') or card.select_one('[class*="content_"]')
            raw_desc = desc_elem.text.strip() if desc_elem else ''
            # Strip trailing "查看更多>" or similar prompts
            clean_desc = re.sub(r'\s*查看更多>?\s*$', '', raw_desc)
            clean_desc = clean_desc.replace('|', '-').replace('\n', ' ').strip()
            short_desc = clean_desc[:160] + '...' if len(clean_desc) > 160 else clean_desc

            if title:
                items.append({
                    'rank': rank_str,
                    'title': title,
                    'url': url,
                    'heat': heat,
                    'desc': short_desc,
                })
        return items

    @classmethod
    def _write_md_for_date(cls, loc: str, items: RAW_DATA_T) -> None:
        md_str = '# 百度热搜 (Baidu Realtime Hot Search)\n\n'
        md_str += '| 排名 | 热搜词 | 热搜指数 | 简介 | 链接 |\n'
        md_str += '| --- | --- | --- | --- | --- |\n'

        for item in items:
            title_link = f'[{item["title"]}]({item["url"]})' if item["url"] else item["title"]
            heat_val = item["heat"]
            try:
                heat_str = f'{int(heat_val):,}'
            except (ValueError, TypeError):
                heat_str = str(heat_val) if heat_val else '-'

            desc_str = item["desc"] or '-'
            view_link = f'[百度搜索]({item["url"]})' if item["url"] else '-'
            md_str += f'| {item["rank"]} | {title_link} | {heat_str} | {desc_str} | {view_link} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        items = cls.get_hot_search()
        write_raw_data(items, path.join(loc, 'hot_search.json'))
        cls._write_md_for_date(loc, items)
