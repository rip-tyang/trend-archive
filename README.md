# Trend-Archive

[![Daily Archive](https://github.com/rip-tyang/trend-archive/actions/workflows/schedule.yml/badge.svg)](https://github.com/rip-tyang/trend-archive/actions/workflows/schedule.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Trend-Archive** is an automated, daily archival engine that tracks and preserves hot and trending topics, developer projects, AI models & research, financial markets, social media discussions, and gaming charts from across the web.

Each day, an automated pipeline queries APIs and platform frontends, generating:
1. **Raw structured JSON data** for programmatic research, time-series analysis, and machine learning datasets.
2. **Clean Markdown summaries** rendered directly inside each date's archive folder for quick human browsing on GitHub.

---

## Table of Contents

- [Supported Platforms & Tracked Metrics](#supported-platforms--tracked-metrics)
- [Archive Structure](#archive-structure)
- [How It Works](#how-it-works)
  - [Idempotent Archiving](#idempotent-archiving)
  - [Fault-Tolerant Error Isolation](#fault-tolerant-error-isolation)
  - [Daily GitHub Actions Automation](#daily-github-actions-automation)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Command Line](#command-line)
  - [Python API](#python-api)
  - [Reading Archived Data](#reading-archived-data)
- [Extending / Adding New Sources](#extending--adding-new-sources)
- [Testing](#testing)
- [License](#license)

---

## Supported Platforms & Tracked Metrics

| Platform | Class | Destination Folder | Metrics & Data Captured |
| :--- | :--- | :--- | :--- |
| **GitHub** | `GithubAPI` | `archive/Github/<date>/` | Daily trending repositories, descriptions, languages, star counts, fork counts, and top contributors. |
| **Hugging Face Models & Datasets** | `HuggingFaceAPI` | `archive/HuggingFace/<date>/` | Trending ML models (task category, model size, downloads, likes, inference providers) and trending datasets (views, downloads, likes). |
| **Hugging Face Papers** | `HuggingFacePapersAPI` | `archive/HuggingFacePapers/<date>/` | Daily trending AI research papers, upvote counts, comments, linked GitHub repositories & stars, authors, and abstract summaries. |
| **US Stocks (Yahoo Finance)** | `YahooFinanceAPI` | `archive/Stock/<date>/` | Most active US equities, tickers, intraday price, price change & %, trading volume, 3-month average volume, market cap, P/E ratio, and 52-week high/low range. |
| **CoinGecko** | `CoinGeckoAPI` | `archive/CoinGecko/<date>/` | Trending cryptocurrencies (price, 24h change, 24h volume, market cap rank), trending NFT collections (floor price, 24h volume), and trending categories. |
| **Crypto Fear & Greed** | `CryptoFearGreedAPI` | `archive/CryptoFearGreed/<date>/` | Alternative.me market sentiment index (0–100 score, classification from Extreme Fear to Extreme Greed) and 30-day historical trend. |
| **Bilibili** | `BilibiliApi` | `archive/Bilibili/<date>/` | Most popular and highest-ranked video lists, video identifiers (`aid`, `bvid`), durations, view counts, and tag frequency distribution. |
| **Weibo (微博)** | `WeiboAPI` | `archive/Weibo/<date>/` | Real-time Weibo Hot Search list (微博热搜榜), hotness rankings, search heat values, category badges, and direct search links. |
| **Zhihu (知乎)** | `ZhihuAPI` | `archive/Zhihu/<date>/` | Zhihu Topstory Hot List (知乎热榜), question titles, hotness metrics, answer counts, follower counts, and topic excerpts. |
| **Steam** | `SteamAPI` | `archive/Steam/<date>/` | Top Most Played games (current concurrent players, peak players today, prices) and Top Selling games globally (ranks, price, rank movement, weeks on chart). |
| **Wikipedia (English)** | `WikipediaAPI` | `archive/Wikipedia/<date>/` | Daily top 100 most read Wikipedia articles globally, pageview counts, article titles, and direct Wikipedia links. |
| **Google Trends** | `GoogleTrendsAPI` | `archive/GoogleTrends/<date>/` | Daily trending search queries (US), approximate search traffic volume, publication timestamps, and top related news headlines. |
| **Baidu (百度热搜)** | `BaiduAPI` | `archive/Baidu/<date>/` | Real-time Baidu Hot Search board (百度热搜榜), heat indices, topic descriptions, and Baidu search links. |

---

## Archive Structure

All archives are organized hierarchically by destination name and date (`YYYY-MM-DD`):

```text
archive/
├── Baidu/
│   └── 2026-10-02/
│       ├── hot_search.json
│       └── README.md
├── Bilibili/
│   └── 2026-10-02/
│       ├── Raw/
│       │   ├── highest_ranked.json
│       │   └── most_popular.json
│       ├── Tags/
│       │   ├── highest_ranked.json
│       │   └── most_popular.json
│       └── README.md
├── CoinGecko/
│   └── 2026-10-02/
│       ├── trending.json
│       └── README.md
├── CryptoFearGreed/
│   └── 2026-10-02/
│       ├── fng.json
│       └── README.md
├── Github/
│   └── 2026-10-02/
│       ├── trending.json
│       └── README.md
├── GoogleTrends/
│   └── 2026-10-02/
│       ├── daily_searches.json
│       └── README.md
├── HuggingFace/
│   └── 2026-10-02/
│       ├── trending_dataset.json
│       ├── trending_model.json
│       └── README.md
├── HuggingFacePapers/
│   └── 2026-10-02/
│       ├── papers.json
│       └── README.md
├── Steam/
│   └── 2026-10-02/
│       ├── most_played.json
│       ├── top_sellers.json
│       └── README.md
├── Stock/
│   └── 2026-10-02/
│       ├── trending.json
│       └── README.md
├── Weibo/
│   └── 2026-10-02/
│       ├── hot_search.json
│       └── README.md
├── Wikipedia/
│   └── 2026-10-02/
│       ├── top_pageviews.json
│       └── README.md
└── Zhihu/
    └── 2026-10-02/
        ├── hot_list.json
        └── README.md
```

Each date directory includes:
- **`*.json`**: Raw, unmodified API responses and parsed objects for data pipelines.
- **`README.md`**: Markdown tables presenting the day's highlights, viewable directly on GitHub.

---

## How It Works

### Idempotent Archiving
Each scraper inherits from `BaseApi`, which checks `has_data(target_date)` before making network requests. If the expected files already exist in `archive/<Source>/<YYYY-MM-DD>/`, the fetch step is automatically skipped. Pass `force=True` to re-fetch and overwrite existing data.

### Fault-Tolerant Error Isolation
When running `save_raw.py`, every platform is executed inside an isolated exception boundary. If a single platform fails due to a rate limit or network hiccup, other sources continue to execute unimpeded. Any failed destinations are recorded and reported at the end, exiting with non-zero status code `1` so alerting or CI workflows are aware.

### Daily GitHub Actions Automation
A scheduled workflow (`.github/workflows/schedule.yml`) runs daily at midnight UTC (`0 0 * * *`) and supports manual triggering via `workflow_dispatch`. It installs dependencies, runs `python save_raw.py`, and automatically commits and pushes updated archives.

---

## Getting Started

### Prerequisites

- Python 3.9+
- [Conda](https://docs.conda.io/) or standard `venv` / `pip`

### Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/rip-tyang/trend-archive.git
cd trend-archive
```

**Using pip:**
```bash
pip install requests beautifulsoup4
```

**Using Conda:**
```bash
conda env create -f environment.yml
conda activate trend-archive
```

---

## Usage

### Command Line

Archive all platforms for today:
```bash
python save_raw.py
```

Archive or backfill a specific date (`YYYY-MM-DD`):
```bash
python save_raw.py 2026-10-02
```

### Python API

You can import and run scrapers individually or programmatically:

```python
from datetime import date
from apis import GithubAPI, CoinGeckoAPI, SteamAPI

# Archive today's trends
GithubAPI.archive_for_today()

# Archive for a specific date (force refresh)
CoinGeckoAPI.archive_for_date("2026-10-02", force=True)

# Fetch data in-memory without saving
trending_games = SteamAPI.get_most_played()
print(trending_games[0])
```

All scrapers can be imported from the `apis` package:
```python
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
```

*(Note: Direct imports from `api.py` are also supported for backward compatibility.)*

### Reading Archived Data

Use `reader.py` or standard `json` to load archived records:

```python
from reader import read_json

data = read_json("archive/Github/2026-09-30/trending.json")
for repo in data:
    print(f"{repo['title']} - {repo['stars']}")
```

---

## Extending / Adding New Sources

To add a new platform:

1. Create a new module in `apis/` (e.g., `apis/my_platform.py`).
2. Subclass `BaseApi` and set:
   - `LOC`: Subfolder name under `archive/`
   - `EXPECTED_FILES`: List of expected files for idempotency checking (e.g. `['trending.json', 'README.md']`)
   - `_archive_for_date(cls, loc: str)`: Implementation fetching data and calling `write_raw_data()` and `write_md()`
3. Export the class in `apis/__init__.py`.
4. Add the class to `APIS` in `save_raw.py`.

---

## Testing

Run the test suite with `unittest`:

```bash
python -m unittest discover tests
```

Tests cover:
- Module exports and backward compatibility
- Date formatting utilities
- Idempotency & cached file detection
- Error isolation during batch runs
- Platform class structures and expected files

---

## License

This project is licensed under the [MIT License](LICENSE).
