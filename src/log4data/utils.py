import os
import pathlib
import datetime as dt
import logging as lg

from typing import Optional

log_levels_lookup = {
    "critical": lg.CRITICAL,
    "error": lg.ERROR,
    "warning": lg.WARNING,
    "info": lg.INFO,
    "debug": lg.DEBUG,
    "notset": lg.NOTSET
}


def _create_log_folder(file_name: str):
    """This function checks if the log file name will be in a folder and wether
    that folder exists, and creates the folder in the case it does not using
    os.makedirs()
    """
    assert file_name.endswith(".log")
    log_folder = pathlib.Path(file_name).parent
    os.makedirs(log_folder, exist_ok=True)


def _add_dynamic_date(log_file_name: str) -> str:
    """Dynamically add today's date to the filename, obtaining something like:
    <log_file_name>_<YYYYMMDD>.log
    """
    today = dt.datetime.now().strftime("%Y%m%d")
    new_log_file_name = log_file_name.split(".")[0] \
        + "_" + today + "." + log_file_name.split(".")[1]

    return new_log_file_name


def parse_date_from_filename(filename: str) -> Optional[dt.datetime]:
    """Extract the date part from the filename, assuming filename format is
    <filename>_<YYYYMMDD>.log
    """
    date_part = filename.stem.split('_')[-1]  # filename.stem gives the filename without the extension
    try:
        # Convert the date part to a datetime object
        return dt.datetime.strptime(date_part, '%Y%m%d')
    except ValueError:
        return None
