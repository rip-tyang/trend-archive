import os
import sys
import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from apis import BaseApi, BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI
import api as legacy_api
import save_raw


class TestBackwardCompatibility(unittest.TestCase):
    def test_legacy_api_module_exports(self):
        self.assertIs(legacy_api.BaseApi, BaseApi)
        self.assertIs(legacy_api.BilibiliApi, BilibiliApi)
        self.assertIs(legacy_api.GithubAPI, GithubAPI)
        self.assertIs(legacy_api.YahooFinanceAPI, YahooFinanceAPI)
        self.assertIs(legacy_api.HuggingFaceAPI, HuggingFaceAPI)


class TestDateFormatting(unittest.TestCase):
    def test_format_date_none(self):
        today_str = date.today().isoformat()
        self.assertEqual(BaseApi.format_date(None), today_str)

    def test_format_date_date_obj(self):
        d = date(2026, 9, 30)
        self.assertEqual(BaseApi.format_date(d), "2026-09-30")

    def test_format_date_datetime_obj(self):
        dt = datetime(2026, 9, 30, 15, 30)
        self.assertEqual(BaseApi.format_date(dt), "2026-09-30")

    def test_format_date_str(self):
        self.assertEqual(BaseApi.format_date("2026-09-30"), "2026-09-30")


class TestIdempotency(unittest.TestCase):
    def test_has_data_existing_date(self):
        # 2026-09-30 is already archived in the repo
        for api_cls in [BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI]:
            self.assertTrue(
                api_cls.has_data("2026-09-30"),
                f"{api_cls.LOC} should have data for 2026-09-30",
            )

    def test_has_data_nonexistent_date(self):
        for api_cls in [BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI]:
            self.assertFalse(
                api_cls.has_data("1990-01-01"),
                f"{api_cls.LOC} should not have data for 1990-01-01",
            )

    def test_has_data_partial_files(self):
        class DummyApi(BaseApi):
            LOC = "Dummy"
            EXPECTED_FILES = ["a.json", "b.json", "README.md"]

        with patch("apis.base.path.exists") as mock_exists:
            # Case 1: directory doesn't exist
            mock_exists.return_value = False
            self.assertFalse(DummyApi.has_data("2026-01-01"))

            # Case 2: dir exists, but one file missing
            def side_effect(p):
                return not p.endswith("b.json")

            mock_exists.side_effect = side_effect
            self.assertFalse(DummyApi.has_data("2026-01-01"))

            # Case 3: all exist
            mock_exists.side_effect = None
            mock_exists.return_value = True
            self.assertTrue(DummyApi.has_data("2026-01-01"))

    def test_archive_for_date_skips_fetch_when_data_exists(self):
        for api_cls in [BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI]:
            with patch.object(api_cls, "_archive_for_date") as mock_archive:
                api_cls.archive_for_date("2026-09-30")
                mock_archive.assert_not_called()

    def test_archive_for_date_fetches_when_forced(self):
        for api_cls in [BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI]:
            with patch.object(api_cls, "_archive_for_date") as mock_archive:
                api_cls.archive_for_date("2026-09-30", force=True)
                mock_archive.assert_called_once()

    def test_archive_for_date_fetches_when_no_data(self):
        for api_cls in [BilibiliApi, GithubAPI, YahooFinanceAPI, HuggingFaceAPI]:
            with patch.object(api_cls, "has_data", return_value=False), patch.object(
                api_cls, "_archive_for_date"
            ) as mock_archive:
                api_cls.archive_for_date("2099-01-01")
                mock_archive.assert_called_once()


class TestErrorIsolation(unittest.TestCase):
    def test_one_failure_does_not_halt_others(self):
        call_order = []

        def make_archive_fn(dest_name, should_fail=False):
            def fn(target_date=None, force=False):
                call_order.append(dest_name)
                if should_fail:
                    raise RuntimeError(f"{dest_name} network error")
            return fn

        with patch.object(BilibiliApi, "archive_for_date", side_effect=make_archive_fn("Bilibili")), \
             patch.object(GithubAPI, "archive_for_date", side_effect=make_archive_fn("Github", should_fail=True)), \
             patch.object(YahooFinanceAPI, "archive_for_date", side_effect=make_archive_fn("Stock")), \
             patch.object(HuggingFaceAPI, "archive_for_date", side_effect=make_archive_fn("HuggingFace")):

            failed = save_raw.save_raw_for_date("2099-01-01")

            # All 4 destinations were attempted
            self.assertEqual(call_order, ["Bilibili", "Github", "Stock", "HuggingFace"])
            # Only Github failed
            self.assertEqual(failed, ["Github"])

    def test_all_succeed(self):
        with patch.object(BilibiliApi, "archive_for_date"), \
             patch.object(GithubAPI, "archive_for_date"), \
             patch.object(YahooFinanceAPI, "archive_for_date"), \
             patch.object(HuggingFaceAPI, "archive_for_date"):

            failed = save_raw.save_raw_for_date("2099-01-01")
            self.assertEqual(failed, [])

    def test_multiple_failures(self):
        with patch.object(BilibiliApi, "archive_for_date", side_effect=Exception("Bilibili down")), \
             patch.object(GithubAPI, "archive_for_date"), \
             patch.object(YahooFinanceAPI, "archive_for_date", side_effect=Exception("Yahoo down")), \
             patch.object(HuggingFaceAPI, "archive_for_date"):

            failed = save_raw.save_raw_for_date("2099-01-01")
            self.assertEqual(failed, ["Bilibili", "Stock"])


    def test_main_exit_code_zero_on_success(self):
        with patch("save_raw.save_raw_for_date", return_value=[]), \
             patch("sys.argv", ["save_raw.py", "2026-09-30"]):
            # Should complete without sys.exit(1)
            save_raw.main()

    def test_main_exit_code_one_on_failure(self):
        with patch("save_raw.save_raw_for_date", return_value=["Github"]), \
             patch("sys.argv", ["save_raw.py", "2099-01-01"]):
            with self.assertRaises(SystemExit) as cm:
                save_raw.main()
            self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()

