from api import BilibiliApi, GithubAPI, YahooFinanceAPI

def save_raw_today():
    for api in [BilibiliApi, GithubAPI, YahooFinanceAPI]:
        api.archive_for_today()

if __name__ == '__main__':
    save_raw_today()
