import sys
import time
import traceback
from datetime import date
from typing import List, Union

from apis import (
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

APIS = [
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
]


# Seconds to wait before retrying failed destinations once, so short upstream outages can clear
RETRY_PASS_DELAY_SECONDS = 120


def _archive_all(apis: List[type], target_date: Union[date, str, None], force: bool) -> List[type]:
    failed = []
    for api in apis:
        dest_name = getattr(api, 'LOC', api.__name__)
        try:
            print(f"=== Archiving destination: {dest_name} ===")
            api.archive_for_date(target_date, force=force)
            print(f"=== Finished destination: {dest_name} ===\n")
        except Exception as e:
            print(f"Error archiving destination {dest_name}: {e}", file=sys.stderr)
            traceback.print_exc()
            failed.append(api)
    return failed


def save_raw_for_date(target_date: Union[date, str, None] = None, force: bool = False) -> List[str]:
    failed = _archive_all(APIS, target_date, force)
    if failed:
        names = ', '.join(getattr(api, 'LOC', api.__name__) for api in failed)
        print(f"Retrying failed destination(s) in {RETRY_PASS_DELAY_SECONDS}s: {names}\n")
        time.sleep(RETRY_PASS_DELAY_SECONDS)
        failed = _archive_all(failed, target_date, force)
    return [getattr(api, 'LOC', api.__name__) for api in failed]


def save_raw_today(force: bool = False) -> List[str]:
    return save_raw_for_date(date.today(), force=force)


def main() -> None:
    target = sys.argv[1] if len(sys.argv) > 1 else None
    failed = save_raw_for_date(target)
    if failed:
        print(f"\n[FAILED] Archiving failed for destination(s): {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
    print("\n[SUCCESS] All destinations processed successfully.")


if __name__ == '__main__':
    main()


