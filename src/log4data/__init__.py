"""
Logging helper package for data pipelines built with Python.

To use, simply 'import log4data as l4g' and log away!
"""

import argparse
import datetime as dt
import logging as lg
import os

from functools import wraps

from typing import (
    Any,
    Callable,
    Final,
    Optional
)


__all__ = [
    "DEFAULT_LOG_FORMAT",
    "set_log_args",
    "setup_logger",
    "setup_logger_with_file"
    "default_setup_logger",
    "inject_logger",
    "inject_named_logger"
]


DEFAULT_LOG_FORMAT: Final = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # noqa: E501


def set_log_args(
    parser: Optional[argparse.ArgumentParser] = None,
    return_args: bool = False
) -> Optional[argparse.Namespace]:
    """
    Adds logging related arguments to an argparse.ArgumentParser.

    This function will add three arguments (`log-level`, `log-file-name`, and
    `log-format`) to the parser provided. If no parser is given, a new one is
    created.
    If `return_args` is True, parse and return the arguments.

    Args:
        parser (argparse.ArgumentParser, None): The parser to which the
            arguments are added. If None, a new parser will be created.
        return_args (bool): If True, parse the arguments and return the
            Namespace containing them.

    Returns:
        argparse.Namespace or None: The Namespace containing parsed arguments
            if `return_args` is True; otherwise, None.

    The arguments added are:
        * --log-level (-lglv) [str]: Level at which logs will be shown.
        * --log-file-name (-lgfn) [str]: File where logs will be written.
        * --log-format (-lgfmt) [str]: Logging format. Default is:
            "%(levelname)s - %(asctime)s - %(name)s - %(message)s"
    """
    if parser is None:  # create the argparse if it's not created
        parser = argparse.ArgumentParser()

    # add custom arguments
    parser.add_argument(
        "-lglv", "--log-level",
        type=str, default="info", help="Set the logging level."
    )
    parser.add_argument(
        "-lgfn", "--log-file-name",
        type=str, default="logs/exit.log", help="File to write logs to."
    )
    parser.add_argument(
        "-lgfmt", "--log-format",
        type=str, default=DEFAULT_LOG_FORMAT, help="Format for logging."
    )

    if return_args:  # return the parsed arguments
        args = parser.parse_args()
        return args


def setup_logger(args: argparse.Namespace):
    """
    Configures the logging.basicConfig() taking into account the arguments
    passed in args.
        * `args.log_level` sets the level of the logger
        * `args.log_file_name` sets the file where logs will be written to.
          This name is taken, and the date is added, resulting in:
          <args.log_file_name>_<YYYYMMDD>.log
        * `args.log_format` sets the format string for the handler

    Args:
        args (argparse.Namespace):
    """
    if args.log_level.lower() == "debug":
        session_level = lg.DEBUG
    elif args.log_level.lower() == "debug":
        session_level = lg.INFO
    elif args.log_level.lower() == "warning":
        session_level = lg.WARNING
    elif args.log_level.lower() == "error":
        session_level = lg.ERROR
    else:
        session_level = lg.INFO

    # dynamically generate the filename as <args.log_file_name>_<YYYYMMDD>.log
    today = dt.datetime.now().strftime("%Y%m%d")
    file_name = args.log_file_name.split(".")[0] \
        + "_" + today + "." + args.log_file_name.split(".")[1]

    _create_log_folder(file_name)

    lg.basicConfig(
        level=session_level,
        filename=file_name,
        format=args.log_format
    )


def setup_logger_with_file(log_file_name: str, dynamic_date: bool = True):
    """
    Configures the logging.basicConfig() taking into account the log_file_name.
    Level is set to INFO and format is set to the default:
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    Args:
        log_file_name (str): sets the file where logs will be written to.
        dynamic_date (bool): if True the name will be altered to add the date
            and result in a name like this: <log_file_name>_<YYYYMMDD>.log
    """
    session_level = lg.INFO

    file_name = log_file_name
    if dynamic_date:
        # dynamically generate the filename as <log_file_name>_<YYYYMMDD>.log
        today = dt.datetime.now().strftime("%Y%m%d")
        file_name = log_file_name.split(".")[0] \
            + "_" + today + "." + log_file_name.split(".")[1]

    _create_log_folder(file_name)

    lg.basicConfig(
        level=session_level,
        filename=file_name,
        format=DEFAULT_LOG_FORMAT
    )


def default_setup_logger():
    """Quick and easy way to setup the logging.basicConfig

    level: lg.INFO
    filename: exit_<YYYYMMDD>.log
    format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
    """
    today = dt.datetime.now().strftime("%Y%m%d")
    lg.basicConfig(
        level=lg.INFO,
        filename=f"exit_{today}.log",
        format=DEFAULT_LOG_FORMAT
    )


def inject_logger(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that injects a logger into the decorated function.

    This decorator modifies the function by adding a `logger` parameter
    automatically before calling the function. It retrieves a logger instance
    using the function's module and name, which helps in tracking which
    function logged the messages.

    Note:
        The decorated function must be designed to accept a 'logger' keyword
        argument. This implementation does not handle the case where the
        function already has a 'logger' keyword argument or uses *args and
        **kwargs in a way that conflicts with the automatic injection of the
        logger.

    Args:
        func (Callable): The function to decorate.

    Returns:
        Callable: A wrapper function that adds the logger to `func`s arguments.

    Example:
    ```python
        @inject_logger()
        def process_data(data, logger=None):
            logger.info("Processing data")
            pass

        # call the function without passing a logger
        process_data(data)
    ```
    """
    logger_name = f"{func.__module__}.{func.__name__}"
    logger = lg.getLogger(logger_name)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, logger=logger, **kwargs)

    return wrapper


def inject_named_logger(logger_name: Optional[str] = None):
    """
    A decorator that injects a logger into the decorated function, with a given
    name.

    This decorator modifies the function by adding a `logger` parameter
    automatically before calling the function. It retrieves a logger instance
    using the passed argument logger_name, which helps in tracking.

    Note:
        The decorated function must be designed to accept a 'logger' keyword
        argument. This implementation does not handle the case where the
        function already has a 'logger' keyword argument or uses *args and
        **kwargs in a way that conflicts with the automatic injection of the
        logger.

    Args:
        logger_name (Optional[str]): if logger_name is not None, the logger
            will have this name. Else the name will be root.

    Returns:
        Callable: A wrapper function that adds the logger to `func`s arguments.

    Example:
    ```python
        @inject_named_logger("my_logger")
        def process_data(data, logger=None):
            logger.info("Processing data")
            pass

        # call the function without passing a logger
        process_data(data)
    ```
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        logger = lg.getLogger(logger_name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, logger=logger, **kwargs)

        return wrapper
    return decorator


def _create_log_folder(file_name: str):
    """This function checks if the log file name will be in a folder and wether
    that folder exists, and creates the folder in the case it does not using
    os.mkdirs()
    """
    assert file_name.endswith(".log")
    if "/" in file_name:
        log_folder = "/".join(file_name.split[:-1])
        os.mkdirs(log_folder, exist_ok=True)
