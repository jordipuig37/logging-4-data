import logging as lg
import pandas as pd

from typing import (
    Optional
)

class LogMonitor:
    def __init__(self):
        self.log_format = '"%(asctime)s","%(name)s","%(levelname)s","%(message)s"'  # noqa: E501
        self.file_dest = None  # [ ] name with run UID, create monitor/ folder or something like that
        self.log_config = None
        self.handler: lg.Handler = lg.FileHandler(self.file_dest)
        self.handler.setLevel(lg.INFO)
        self.handler.setFormatter(self.log_format)

    def get_logger(self, name: Optional[str]=None):
        """Return a logger with the specified name, creating it if necessary,
        and adding the Monitoring handler.

        If no name is specified, return the root logger.
        """
        if name in lg.Logger.manager.loggerDict:
            return lg.getLogger(name)
        else:
            new_logger = lg.getLogger(name)  # create the new logger
            new_logger.addHandler(self.handler)  # add the class handler
            return new_logger

    def retrieve_data(self):
        return pd.read_csv(self.file_dest, sep=",", quotechar="\"")
