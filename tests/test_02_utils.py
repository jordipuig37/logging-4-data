import os
import pathlib
import datetime as dt
import log4data as l4d
import pytest

class TestDeleteOldLogFiles:
    @pytest.fixture(autouse=True)
    def generate_sample_log_files_to_delete(self, tmp_path):
        # Create a log file older than 30 days
        self.tmp_dir = tmp_path
        old_date = (dt.datetime.now() - dt.timedelta(days=31)).strftime("%Y%m%d")
        self.old_log = self.tmp_dir / f"test_{old_date}.log"
        self.old_log.write_text("old log content")

    def is_folder_empty(self, d):
        return not any(pathlib.Path(d).iterdir())

    def test_delete_old_log_files(self):
        l4d.delete_old_log_files(str(self.tmp_dir), older_than=30)
        assert self.is_folder_empty(self.tmp_dir)
