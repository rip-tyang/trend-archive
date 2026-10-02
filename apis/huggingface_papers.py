from typing import Dict, List, Any
from os import path

from apis.base import BaseApi
from writer import write_raw_data, write_md


class HuggingFacePapersAPI(BaseApi):
    LOC = 'HuggingFacePapers'
    BASE_URL = 'https://huggingface.co/api/daily_papers'
    RAW_DATA_T = List[Dict[str, Any]]
    EXPECTED_FILES = [
        'papers.json',
        'README.md',
    ]

    @classmethod
    def get_daily_papers(cls) -> RAW_DATA_T:
        papers_data = cls._get_json(cls.BASE_URL)
        parsed = []
        for rank, item in enumerate(papers_data, start=1):
            paper = item.get('paper', {})
            paper_id = paper.get('id', '')
            title = item.get('title') or paper.get('title', '')
            title_clean = title.replace('|', '-').replace('\n', ' ').strip()
            authors = [a.get('name') for a in paper.get('authors', []) if a.get('name')]
            authors_str = ', '.join(authors[:3]) + (' et al.' if len(authors) > 3 else '')
            authors_str = authors_str.replace('|', '-')
            upvotes = paper.get('upvotes', 0)
            comments = item.get('numComments', 0)
            github_repo = paper.get('githubRepo') or ''
            github_stars = paper.get('githubStars') or ''
            summary = (item.get('summary') or paper.get('summary', '')).replace('|', '-').replace('\n', ' ').strip()
            # Truncate summary for table display if too long
            short_summary = summary[:180] + '...' if len(summary) > 180 else summary

            parsed.append({
                'rank': rank,
                'id': paper_id,
                'title': title_clean,
                'url': f'https://huggingface.co/papers/{paper_id}' if paper_id else '',
                'arxiv_url': f'https://arxiv.org/abs/{paper_id}' if paper_id else '',
                'authors': authors,
                'authors_str': authors_str,
                'upvotes': upvotes,
                'comments': comments,
                'github_repo': github_repo,
                'github_stars': github_stars,
                'summary': summary,
                'short_summary': short_summary,
                'thumbnail': item.get('thumbnail', ''),
                'published_at': item.get('publishedAt') or paper.get('publishedAt', ''),
            })
        return parsed

    @classmethod
    def _write_md_for_date(cls, loc: str, papers: RAW_DATA_T) -> None:
        md_str = '# Hugging Face Daily Papers\n\n'
        md_str += '| Rank | Title | Upvotes | Comments | GitHub | Authors | Summary |\n'
        md_str += '| --- | --- | --- | --- | --- | --- | --- |\n'

        for p in papers:
            title_link = f'[{p["title"]}]({p["url"]})' if p["url"] else p["title"]
            gh_link = f'[{p["github_stars"]} ★]({p["github_repo"]})' if p["github_repo"] else (str(p["github_stars"]) if p["github_stars"] else '-')
            md_str += f'| {p["rank"]} | {title_link} | {p["upvotes"]} | {p["comments"]} | {gh_link} | {p["authors_str"]} | {p["short_summary"]} |\n'

        write_md(md_str, path.join(loc, 'README.md'))

    @classmethod
    def _archive_for_date(cls, loc: str) -> None:
        papers = cls.get_daily_papers()
        write_raw_data(papers, path.join(loc, 'papers.json'))
        cls._write_md_for_date(loc, papers)
