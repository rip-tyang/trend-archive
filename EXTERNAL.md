# External Data Sources

Sources that are **not** archived by this repo because the publisher already keeps a complete, downloadable history. Archiving them daily would only produce duplicate snapshots. If the data is needed, fetch it directly from the links below.

---

## Netflix Top 10

Netflix publishes its Top 10 **weekly**. Weeks run Monday–Sunday and new data usually lands on Tuesday. Each file below contains the **full history** since the week of 2021-07-04 and is updated in place every week.

| File | URL | Contents |
| :--- | :--- | :--- |
| Global weekly | https://www.netflix.com/tudum/top10/data/all-weeks-global.tsv | Global Top 10 per week in 4 categories: Films (English), Films (Non-English), TV (English), TV (Non-English). |
| Per-country weekly | https://www.netflix.com/tudum/top10/data/all-weeks-countries.tsv | Top 10 per week per country (~33 MB). |
| Most popular (all-time) | https://www.netflix.com/tudum/top10/data/most-popular.tsv | All-time most popular titles, ranked by views in their first 91 days. |

Website: https://www.netflix.com/tudum/top10

### Columns

- **Global**: `week`, `category`, `weekly_rank`, `show_title`, `season_title`, `weekly_hours_viewed`, `runtime`, `weekly_views`, `cumulative_weeks_in_top_10`
- **Per-country**: `country_name`, `country_iso2`, `week`, `category`, `weekly_rank`, `show_title`, `season_title`, `cumulative_weeks_in_top_10`
- **Most popular**: `category`, `rank`, `show_title`, `season_title`, `hours_viewed_first_91_days`, `runtime`, `views_first_91_days`

### Notes

- `week` is the **last day (Sunday)** of the reporting week.
- `season_title` is the literal string `N/A` for films and single-season titles.
- The files are served **without a charset header**. Decode them as UTF-8 explicitly, or non-English titles will be garbled (e.g. with `requests`, set `res.encoding = 'utf-8'` before reading `res.text`).
- Netflix could change or remove these files at any time. Download a copy before relying on them for long-term analysis.
