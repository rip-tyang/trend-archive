"""
Backward-compatibility module.
Direct imports should use the `apis` package:
    from apis import (
        BaseApi,
        BilibiliApi,
        GithubAPI,
        YahooFinanceAPI,
        HuggingFaceAPI,
        HuggingFacePapersAPI,
        CoinGeckoAPI,
        CryptoFearGreedAPI,
        WeiboAPI,
        ZhihuAPI,
        SteamAPI,
    )
"""
from apis import (
    BaseApi,
    BilibiliApi,
    GithubAPI,
    YahooFinanceAPI,
    HuggingFaceAPI,
    HuggingFacePapersAPI,
    CoinGeckoAPI,
    CryptoFearGreedAPI,
    WeiboAPI,
    ZhihuAPI,
    SteamAPI,
)

__all__ = [
    'BaseApi',
    'BilibiliApi',
    'GithubAPI',
    'YahooFinanceAPI',
    'HuggingFaceAPI',
    'HuggingFacePapersAPI',
    'CoinGeckoAPI',
    'CryptoFearGreedAPI',
    'WeiboAPI',
    'ZhihuAPI',
    'SteamAPI',
]


if __name__ == '__main__':
    for api_cls in [
        BilibiliApi,
        GithubAPI,
        YahooFinanceAPI,
        HuggingFaceAPI,
        HuggingFacePapersAPI,
        CoinGeckoAPI,
        CryptoFearGreedAPI,
        WeiboAPI,
        ZhihuAPI,
        SteamAPI,
    ]:
        api_cls.archive_for_today()