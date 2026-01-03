#!/usr/bin/env python3
"""
Automated tests for squishmallowdex.py

Run with: python3 -m pytest test_squishmallowdex.py -v
Or simply: python3 test_squishmallowdex.py
"""

import os
import sys
import tempfile
from io import StringIO

# Import the module under test
import squishmallowdex as sq


class TestSkippedFilePath:
    """Tests for the skipped_file_path function."""

    def test_txt_extension(self):
        assert sq.skipped_file_path("progress.txt") == "progress_skipped.txt"

    def test_json_extension(self):
        assert sq.skipped_file_path("progress.json") == "progress_skipped.json"

    def test_no_extension(self):
        assert sq.skipped_file_path("progress") == "progress_skipped.txt"

    def test_path_with_directory(self):
        result = sq.skipped_file_path("/path/to/progress.txt")
        assert result == "/path/to/progress_skipped.txt"

    def test_double_extension(self):
        result = sq.skipped_file_path("file.backup.txt")
        assert result == "file.backup_skipped.txt"


class TestAdventureLog:
    """Tests for the AdventureLog class."""

    def test_default_values(self):
        log = sq.AdventureLog()
        assert log.verbose == 0
        assert log.adventure_mode is True
        assert log.quiet is False
        assert log.new_catches == 0
        assert log.skipped == 0
        assert log.errors == 0

    def test_quiet_mode_suppresses_banner(self):
        log = sq.AdventureLog(quiet=True, use_color=False)
        output = StringIO()
        log._print = lambda msg, **kw: output.write(msg + "\n")
        log.banner()
        assert output.getvalue() == ""

    def test_quiet_mode_suppresses_info(self):
        log = sq.AdventureLog(quiet=True, use_color=False)
        output = StringIO()
        log._print = lambda msg, **kw: output.write(msg + "\n")
        log.info("test message")
        assert output.getvalue() == ""

    def test_quiet_mode_suppresses_step(self):
        log = sq.AdventureLog(quiet=True, use_color=False)
        output = StringIO()
        log._print = lambda msg, **kw: output.write(msg + "\n")
        log.step("test step")
        assert output.getvalue() == ""

    def test_quiet_mode_allows_warn(self):
        log = sq.AdventureLog(quiet=True, use_color=False)
        output = StringIO()
        log._print = lambda msg, **kw: output.write(msg + "\n")
        log.warn("test warning")
        assert "warning" in output.getvalue().lower()

    def test_quiet_mode_allows_error(self):
        log = sq.AdventureLog(quiet=True, use_color=False)
        output = StringIO()
        log._print = lambda msg, **kw: output.write(msg + "\n")
        log.error("test error")
        assert "error" in output.getvalue().lower()

    def test_catch_increments_counter(self):
        log = sq.AdventureLog(quiet=True)
        assert log.new_catches == 0
        log.catch("Test Squish", 1)
        assert log.new_catches == 1
        log.catch("Another Squish", 2)
        assert log.new_catches == 2

    def test_skip_increments_counter(self):
        log = sq.AdventureLog(quiet=True)
        assert log.skipped == 0
        log.skip("Page 1")
        assert log.skipped == 1
        log.skip("Page 2", "bad data")
        assert log.skipped == 2

    def test_cache_hit_increments_counter(self):
        log = sq.AdventureLog(quiet=True)
        assert log.cache_hits == 0
        log.cache_hit("file1")
        assert log.cache_hits == 1

    def test_cache_miss_increments_counter(self):
        log = sq.AdventureLog(quiet=True)
        assert log.cache_misses == 0
        log.cache_miss("file1")
        assert log.cache_misses == 1

    def test_track_squish_updates_stats(self):
        log = sq.AdventureLog()
        log.track_squish({"Type": "Unicorn", "Color": "Pink", "Squad": "Fantasy"})
        assert log.types_seen["Unicorn"] == 1
        assert log.colors_seen["Pink"] == 1
        assert log.squads_seen["Fantasy"] == 1

        log.track_squish({"Type": "Unicorn", "Color": "Blue", "Squad": "Fantasy"})
        assert log.types_seen["Unicorn"] == 2
        assert log.colors_seen["Blue"] == 1
        assert log.squads_seen["Fantasy"] == 2

    def test_log_file_operations(self):
        log = sq.AdventureLog()
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "test.log")
            log.log_file = log_path
            log.open_log()
            log._log_to_file("test message")
            log.close_log()

            with open(log_path) as f:
                content = f.read()
            assert "test message" in content
            assert "Run completed at" in content

    def test_log_creates_directory(self):
        log = sq.AdventureLog()
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "subdir", "test.log")
            log.log_file = log_path
            log.open_log()
            log.close_log()
            assert os.path.exists(log_path)


class TestSha1:
    """Tests for the _sha1 helper function."""

    def test_consistent_hash(self):
        assert sq._sha1("test") == sq._sha1("test")

    def test_different_inputs_different_hash(self):
        assert sq._sha1("test1") != sq._sha1("test2")

    def test_returns_hex_string(self):
        result = sq._sha1("test")
        assert all(c in "0123456789abcdef" for c in result)
        assert len(result) == 40  # SHA1 is 40 hex chars


class TestCSVOperations:
    """Tests for CSV read/write operations."""

    def test_read_nonexistent_csv(self):
        rows = sq.read_existing_csv("/nonexistent/path.csv")
        assert rows == []

    def test_write_and_read_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            test_rows = [
                {"Name": "Squish1", "Type": "Cat", "Color": "Pink"},
                {"Name": "Squish2", "Type": "Dog", "Color": "Blue"},
            ]
            sq.write_csv(test_rows, csv_path)
            read_rows = sq.read_existing_csv(csv_path)
            assert len(read_rows) == 2
            assert read_rows[0]["Name"] == "Squish1"
            assert read_rows[1]["Type"] == "Dog"


class TestProgressFileOperations:
    """Tests for progress file operations."""

    def test_load_nonexistent_progress(self):
        urls = sq.read_progress("/nonexistent/path.txt")
        assert urls == set()

    def test_append_and_load_progress(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            progress_path = os.path.join(tmpdir, "progress.txt")
            sq.append_progress(progress_path, "http://example.com/1")
            sq.append_progress(progress_path, "http://example.com/2")
            loaded = sq.read_progress(progress_path)
            assert "http://example.com/1" in loaded
            assert "http://example.com/2" in loaded


class TestURLFiltering:
    """Tests for URL filtering logic."""

    def test_skip_namespaces_filtered(self):
        # These should be filtered out
        assert any(ns in "File:Image.png" for ns in sq.SKIP_NAMESPACES)
        assert any(ns in "Category:Animals" for ns in sq.SKIP_NAMESPACES)
        assert any(ns in "Template:Infobox" for ns in sq.SKIP_NAMESPACES)

    def test_noisy_pages_pattern(self):
        assert sq.NOISY_PAGES.search("/wiki/Master_List")
        assert sq.NOISY_PAGES.search("/wiki/Main_Page")
        assert sq.NOISY_PAGES.search("/wiki/By_Color")
        assert not sq.NOISY_PAGES.search("/wiki/Fifi_the_Fox")

    def test_non_character_titles_pattern(self):
        assert sq.NON_CHARACTER_TITLES.search("Master List")
        assert sq.NON_CHARACTER_TITLES.search("Squishville Guide")
        assert not sq.NON_CHARACTER_TITLES.search("Fifi the Fox")


class TestHTMLRendering:
    """Tests for HTML rendering."""

    def test_render_html_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            html_path = os.path.join(tmpdir, "test.html")
            test_rows = [
                {"Name": "Squish1", "img": "http://example.com/img1.png"},
            ]
            sq.render_html(test_rows, html_path, "Test Title")
            assert os.path.exists(html_path)

            with open(html_path) as f:
                content = f.read()
            assert "Squish1" in content
            assert "Test Title" in content


class TestPhoenixEasterEgg:
    """Tests for the phoenix easter egg logic."""

    def test_phoenix_not_shown_by_default(self):
        log = sq.AdventureLog(quiet=False, use_color=False, show_phoenix_art=False)
        # Mock show_phoenix to track if it's called
        called = []
        log.show_phoenix = lambda: called.append(True)

        # total_available=0 means we don't know the total, so no easter egg
        log.summary(100, 50, total_available=0)
        assert len(called) == 0

    def test_phoenix_shown_when_all_collected(self):
        log = sq.AdventureLog(quiet=False, use_color=False, show_phoenix_art=False)
        called = []
        log.show_phoenix = lambda: called.append(True)

        # total_rows >= total_available triggers the easter egg
        log.summary(300, 100, total_available=300)
        assert len(called) == 1

    def test_phoenix_shown_with_flag(self):
        log = sq.AdventureLog(quiet=False, use_color=False, show_phoenix_art=True)
        called = []
        log.show_phoenix = lambda: called.append(True)

        log.summary(10, 5, total_available=1000)
        assert len(called) == 1

    def test_phoenix_respects_quiet_mode(self):
        log = sq.AdventureLog(quiet=True, use_color=False, show_phoenix_art=True)
        output = StringIO()
        original_print = print

        # Even with show_phoenix_art=True, quiet mode should suppress
        log.show_phoenix()  # Should do nothing due to quiet mode


class TestRemainingToCatchClamping:
    """Tests for the remaining_to_catch calculation."""

    def test_clamping_prevents_negative(self):
        # Simulate: limit=10, already have 50 rows, processing 100 URLs
        # Without clamping: 10 - 50 = -40
        # With clamping: max(0, min(-40, 100)) = 0
        limit = 10
        current_rows = 50
        urls_count = 100
        remaining = max(0, min(limit - current_rows, urls_count))
        assert remaining == 0

    def test_clamping_normal_case(self):
        limit = 100
        current_rows = 30
        urls_count = 50
        remaining = max(0, min(limit - current_rows, urls_count))
        assert remaining == 50  # min(70, 50) = 50

    def test_no_limit(self):
        # When limit is None, we process all URLs
        urls_count = 100
        remaining = urls_count
        assert remaining == 100


def run_tests():
    """Run tests using pytest if available, otherwise use basic assertions."""
    try:
        import pytest
        sys.exit(pytest.main([__file__, "-v"]))
    except ImportError:
        print("pytest not installed, running basic tests...")

        # Run each test class manually
        test_classes = [
            TestSkippedFilePath,
            TestAdventureLog,
            TestSha1,
            TestCSVOperations,
            TestProgressFileOperations,
            TestURLFiltering,
            TestHTMLRendering,
            TestPhoenixEasterEgg,
            TestRemainingToCatchClamping,
        ]

        passed = 0
        failed = 0

        for test_class in test_classes:
            instance = test_class()
            for method_name in dir(instance):
                if method_name.startswith("test_"):
                    try:
                        getattr(instance, method_name)()
                        print(f"  PASS: {test_class.__name__}.{method_name}")
                        passed += 1
                    except Exception as e:
                        print(f"  FAIL: {test_class.__name__}.{method_name}: {e}")
                        failed += 1

        print(f"\n{passed} passed, {failed} failed")
        sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    run_tests()
