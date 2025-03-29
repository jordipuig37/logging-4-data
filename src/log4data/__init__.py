"""
Logging helper package for data pipelines built with Python.

To use, simply 'import log4data as l4g' and log away!
"""

import argparse
import logging as lg

from functools import wraps

from typing import (
    Any,
    Callable,
    Final,
    Optional
)

from .monitoring import (
    setup_monitoring_args,
    setup_default_monitor,
    setup_monitor,
    setup_monitor_from_args,
    inject_default_monitor,
    inject_named_monitor
)

from .utils import (
    log_levels_lookup,
    _create_log_folder,
    _add_dynamic_date,
    delete_old_log_files
)

__all__ = [
    "DEFAULT_LOG_FORMAT",
    # CORE
    "setup_log_args",
    "setup_default_logger",
    "setup_logger",
    "setup_logger_from_args",
    "get_stream_logger",
    "inject_logger",
    "inject_named_logger",
    # MONITORING
    "setup_monitoring_args",
    "setup_default_monitor",
    "setup_monitor",
    "setup_monitor_from_args",
    "inject_default_monitor",
    "inject_named_monitor",
    # UTILS
    "delete_old_log_files"
]


DEFAULT_LOG_FORMAT: Final = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # noqa: E501


def setup_log_args(
    parser: Optional[argparse.ArgumentParser] = None,
    return_args: bool = False
) -> Optional[argparse.Namespace]:
    """
    Adds logging related arguments to an argparse.ArgumentParser.

    This function will add three arguments (``log-level``, ``log-file-name``,
    and ``log-format``) to the parser provided. If no parser is given, a new
    one is created.
    If ``return_args`` is True, parse and return the arguments.

    Parameters
        parser : Optional[argparse.ArgumentParser] default None
            The parser to which the arguments are added. If None, a new parser
            will be created.
        return_args : (bool) default False
            If True, parse the arguments and return the Namespace containing
            them.

    Returns
        Optional[argparse.Namespace]
            The Namespace containing parsed arguments if `return_args` is True
            otherwise, None.

    Note
    ----
    The arguments added are:

    + ``--log-level`` (``-lglv``) [str]: Level at which logs will be shown.
    + ``--log-file-name`` (``-lgfn``) [str]: File where logs will be written.
    + ``--log-format`` (``-lgfmt``) [str]: Logging format. Default is:
      ``%(levelname)s - %(asctime)s - %(name)s - %(message)s``

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
    parser.add_argument(
        "-add", "--add-dynamic-date",
        type=bool, action="store_true", default=True,
        help="Add the date to the log file name: <filename>_<YYYYMMDD>.log"

    )

    if return_args:  # return the parsed arguments
        args = parser.parse_args()
        return args
    return None


def setup_logger_from_args(args: argparse.Namespace):
    """
    Configures the logging.basicConfig() taking into account the arguments
    passed in args.

    + ``args.log_level`` sets the level of the logger
    + ``args.log_file_name`` sets the file where logs will be written to.
      This name is taken, and the date is added, resulting in:
      ``<args.log_file_name>_<YYYYMMDD>.log``
    + ``args.log_format`` sets the format string for the handler
    + ``args.add_dynamic_date``

    Parameters
        args : (argparse.Namespace)
    """
    session_level = log_levels_lookup.get(args.log_level.lower(), lg.INFO)

    file_name = args.log_file_name
    if args.add_dynamic_date:
        file_name = _add_dynamic_date(args.log_file_name)

    _create_log_folder(file_name)

    lg.basicConfig(
        level=session_level,
        filename=file_name,
        format=args.log_format
    )


def setup_logger(
        level: int = lg.INFO,
        log_file_name: str = "exit.log",
        log_format: str = DEFAULT_LOG_FORMAT,
        dynamic_date: bool = True):
    """
    Configures the logging.basicConfig() taking into account the log_file_name.
    Level is set to INFO and format is set to the default:
    ``%(asctime)s - %(name)s - %(levelname)s - %(message)s``

    Parameters
        log_file_name : (str)
            Sets the file where logs will be written to.
        dynamic_date : (bool)
            If True the name will be altered to add the date and result in a
            name like this: ``<log_file_name>_<YYYYMMDD>.log``
    """
    if dynamic_date:
        log_file_name = _add_dynamic_date(log_file_name)

    _create_log_folder(log_file_name)

    lg.basicConfig(
        level=level,
        filename=log_file_name,
        format=log_format
    )


def setup_default_logger():
    """Quick and easy way to setup the logging.basicConfig

    + level: ``lg.INFO``
    + filename: ``exit_<YYYYMMDD>.log``
    + format: ``%(asctime)s - %(name)s - %(levelname)s - %(message)s``
    """
    log_file_name = _add_dynamic_date("exit.log")
    lg.basicConfig(
        level=lg.INFO,
        filename=log_file_name,
        format=DEFAULT_LOG_FORMAT
    )


def inject_logger(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that injects a logger into the decorated function.

    This decorator modifies the function by adding a ``logger`` parameter
    automatically before calling the function. It retrieves a logger instance
    using the function's module and name, which helps in tracking which
    function logged the messages.

    Note
    ----
    The decorated function must be designed to accept a ``logger`` keyword
    argument. This implementation does not handle the case where the
    function already has a ``logger`` keyword argument or uses *args and
    **kwargs in a way that conflicts with the automatic injection of the
    logger.


    Parameters
        func : (Callable[..., Any])
            The function to decorate.


    Returns
        Callable
            A wrapper function that adds the logger to ``func`` 's arguments.

    Example
        .. code-block:: python

            @inject_logger()
            def process_data(data, logger=None):
                logger.info("Processing data")
                pass

            # call the function without passing a logger
            process_data(data)

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

    This decorator modifies the function by adding a ``logger`` parameter
    automatically before calling the function. It retrieves a logger instance
    using the passed argument logger_name, which helps in tracking.


    Note
    ----
    The decorated function must be designed to accept a ``logger`` keyword
    argument. This implementation does not handle the case where the
    function already has a ``logger`` keyword argument or uses *args and
    **kwargs in a way that conflicts with the automatic injection of the
    logger.


    Parameters
        logger_name : (Optional[str])
            If logger_name is not None, the logger
            will have this name. Else the name will be root.

    Returns
        Callable
            A wrapper function that adds the logger to ``func`` 's arguments.

    Example
        .. code-block:: python

            @inject_named_logger("my_logger")
            def process_data(data, logger=None):
                logger.info("Processing data")
                pass

            # call the function without passing a logger
            process_data(data)

    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        logger = lg.getLogger(logger_name)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, logger=logger, **kwargs)

        return wrapper
    return decorator


def get_stream_logger(
        level: int = lg.INFO,
        log_format: str = DEFAULT_LOG_FORMAT) -> lg.Logger:
    """
    Setup logging to make beautiful logging in notebooks or in the terminal.

    This function returns a logger object that will print everything to the
    stream output. This is meant to be used in notebooks or in scripts ran from
    the terminal.

    Parameters
        level : (int)
            The logging level, default `lg.INFO`
        log_format : (str)
            The format of the messages. Set by default to library standard.
    """
    logger = lg.getLogger(__name__)
    logger.propagate = False  # removes the link to the root logger
    logger.setLevel(level)
    stream_handler = lg.StreamHandler()
    stream_handler.setFormatter(lg.Formatter(log_format))
    logger.handlers = [stream_handler]

    logger.info(
        f"Logger is initialized with level: lg.{lg.getLevelName(level)}"
    )

    return logger
