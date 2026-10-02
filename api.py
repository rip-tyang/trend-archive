"""
Backward-compatibility module.
Direct imports should use the `apis` package:
    from apis import BaseApi, BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI
"""
from apis import (
    BaseApi,
    BilibiliApi,
    GithubAPI,
    YahooFinanceAPI,
    HuggingFaceAPI,
)

__all__ = [
    'BaseApi',
    'BilibiliApi',
    'GithubAPI',
    'YahooFinanceAPI',
    'HuggingFaceAPI',
]


if __name__ == '__main__':
    for api_cls in [BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI]:
        api_cls.archive_for_today()