import sys
import os
import logging as lg
import argparse
import tempfile
import shutil
import types
import pytest
from freezegun import freeze_time

import log4data as l4d

import argparse


def clean_root_logger():
    """Remove all handlers from the root logger before and after the test."""
    for handler in lg.root.handlers[:]:
        lg.root.removeHandler(handler)


class TestSetupLogArgs:
    def test_arguments_added_to_parser(self, monkeypatch):
        parser = argparse.ArgumentParser()
        l4d.setup_log_args(parser)
        args = parser.parse_args([])

        assert hasattr(args, "log_level")
        assert hasattr(args, "log_file_name")
        assert hasattr(args, "log_format")
        assert hasattr(args, "add_dynamic_date")


    def test_default_argument_values(self, monkeypatch):
        parser = argparse.ArgumentParser()
        l4d.setup_log_args(parser)
        args = parser.parse_args([])

        assert args.log_level == "info"
        assert args.log_file_name == "logs/exit.log"
        assert args.log_format == l4d.DEFAULT_LOG_FORMAT
        assert args.add_dynamic_date is True


    def test_return_args_flag(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["prog"])
        args = l4d.setup_log_args(return_args=True)

        assert isinstance(args, argparse.Namespace)
        assert args.log_level == "info"

    def test_custom_cli_args(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", [
            "prog",
            "--log-level", "debug",
            "--log-file-name", "mylogs.log",
            "--log-format", "%(message)s",
            "--add-dynamic-date"
        ])
        args = l4d.setup_log_args(return_args=True)

        assert args.log_level == "debug"
        assert args.log_file_name == "mylogs.log"
        assert args.log_format == "%(message)s"
        assert args.add_dynamic_date is True

    def test_add_dynamic_date_flag(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["prog", "--add-dynamic-date"])
        args = l4d.setup_log_args(return_args=True)
        assert args.add_dynamic_date is True

        monkeypatch.setattr(sys, "argv", ["prog"])
        args = l4d.setup_log_args(return_args=True)
        assert args.add_dynamic_date is True


class TestSetupLoggerFromArgs:
    @pytest.fixture(autouse=True)
    def input_args(self):
        self.args = types.SimpleNamespace(
            log_level="info",
            log_file_name="tmp/TestSetupLoggerFromArgs.log",
            log_format=l4d.DEFAULT_LOG_FORMAT,
            add_dynamic_date=False
        )

    def test_setup_logger_from_args_creates_log_file(self):
        clean_root_logger()
        l4d.setup_logger_from_args(self.args)
        lg.info("from test_setup_logger_from_args_creates_log_file")

        assert os.path.exists(self.args.log_file_name), \
            f"File {self.args.log_file_name} doesn't exist."


class TestSetupLogger:
    @pytest.fixture(autouse=True)
    def log_file_path(self):
        self.log_file = "tmp/TestSetupLogger.log"

    def test_setup_logger_creates_log_file(self):
        clean_root_logger()
        l4d.setup_logger(
            level=lg.INFO,
            log_file_name=self.log_file,
            dynamic_date=False
        )
        lg.info("dummy test message")

        assert os.path.exists(self.log_file), \
            f"File {self.log_file} doesn't exist."


@freeze_time("2025-01-01 12:00:00")
class TestSetupDefaultLogger:
    @pytest.fixture(autouse=True)
    def fix_day_log_file_path(self):
        """Sets the log file name according to `freeze_time` to 2025-01-01
        """
        self.fix_day_log_file = "exit_20250101.log"

    def test_setup_default_logger_creates_log_file(self):
        clean_root_logger()
        l4d.setup_default_logger()
        lg.info("default logger test")

        assert os.path.exists(self.fix_day_log_file), \
            f"File {self.fix_day_log_file} doesn't exist."
