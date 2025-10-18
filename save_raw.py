from api import BilibiliApi, GithubAPI

def save_raw_today():
    # BilibiliApi.archive_for_today()
    GithubAPI.archive_for_today()

if __name__ == '__main__':
    save_raw_today()
