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
        WikipediaAPI,
        GoogleTrendsAPI,
        BaiduAPI,
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
    WikipediaAPI,
    GoogleTrendsAPI,
    BaiduAPI,
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
    'WikipediaAPI',
    'GoogleTrendsAPI',
    'BaiduAPI',
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
        WikipediaAPI,
        GoogleTrendsAPI,
        BaiduAPI,
    ]:
        api_cls.archive_for_today()