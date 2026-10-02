import sys
import traceback
from datetime import date
from typing import List, Union

from apis import BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI

APIS = [BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI]


def save_raw_for_date(target_date: Union[date, str, None] = None, force: bool = False) -> List[str]:
    failed = []
    for api in APIS:
        dest_name = getattr(api, 'LOC', api.__name__)
        try:
            print(f"=== Archiving destination: {dest_name} ===")
            api.archive_for_date(target_date, force=force)
            print(f"=== Finished destination: {dest_name} ===\n")
        except Exception as e:
            print(f"Error archiving destination {dest_name}: {e}", file=sys.stderr)
            traceback.print_exc()
            failed.append(dest_name)
    return failed


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


