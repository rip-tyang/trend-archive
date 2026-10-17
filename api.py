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
        PolymarketAPI,
        AppleChartsAPI,
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
    PolymarketAPI,
    AppleChartsAPI,
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
    'PolymarketAPI',
    'AppleChartsAPI',
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
        PolymarketAPI,
        AppleChartsAPI,
    ]:
        api_cls.archive_for_today()