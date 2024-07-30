import argparse
import os
import logging as lg
import warnings

from functools import wraps

from typing import (
    Any,
    Callable,
    Final,
    Optional
)

from .utils import (
    _create_log_folder,
    _add_dynamic_date
)


DEFAULT_MONITOR_NAME: Final = "monitor"
DEFAULT_MONITOR_FILE: Final = "logs/monitoring_exit.log"


def _initialize_log_headers(filename: str):
    """This function simply writes the header to the log file that the monitor
    will use, in order to be easily read as a csv with headers later.
    """
    header = "timestamp,name,levelname,message,key,value"
    if not os.path.exists(filename):
        with open(filename, "w") as lgf:
            lgf.write(header)
            lgf.write("\n")


def setup_monitoring_args(
    parser: Optional[argparse.ArgumentParser] = None,
    return_args: bool = False
) -> Optional[argparse.Namespace]:
    """
    Adds monitor related arguments to an argparse.ArgumentParser.

    This function will add two arguments (``monitor-name`` and
    ``monitor-file-name``) to the parser provided. If no parser is given, a new
    one is created. If ``return_args`` is True, parse and return the arguments.

    Parameters
        parser : (argparse.ArgumentParser, None)
            The parser to which the arguments are added. If None, a new parser
            will be created.
        return_args : (bool)
            If True, parse the arguments and return the Namespace containing
            them.

    Returns
        argparse.Namespace or None
            The Namespace containing parsed arguments if `return_args` is True
            otherwise, None.

    Note
    ----
    The arguments added are:

    + ``--monitor-name`` (``-mtn``) [str]: The name of the monitor.
    + ``--monitor-file-name`` (``-mtfn``) [str]: File where monitor
      logs will be written.

    """
    if parser is None:  # create the argparse if it's not created
        parser = argparse.ArgumentParser()

    # add custom arguments
    parser.add_argument(
        "-mtn", "--monitor-name",
        type=str, default="monitor", help="Set the monitor name."
    )
    parser.add_argument(
        "-mtfn", "--monitor-file-name",
        type=str, default="logs/monitor.log",
        help="File to write monitor logs to."
    )

    if return_args:  # return the parsed arguments
        args = parser.parse_args()
        return args
    return None


class MonitorLogger(lg.Logger):
    """A custom Logger subclass designed for logging events in data pipeline
    processes, with support for additional context in the form of 'key' and
    'value' pairs.

    This logger extends the standard logging.Logger to include 'key' and
    'value' parameters in every log record. These parameters are intended to
    provide extra context specific to data processing tasks, making it easier
    to track and filter logs based on specific attributes or stages of the
    pipeline.

    Attributes:
        name (str): The name of the logger.
        level (int): The threshold for this logger. Logging messages which are
            less severe than `level` will be ignored.
    """
    def __init__(self, name, level=lg.NOTSET):
        super().__init__(name, level)

    def _log(
            self,
            level,
            msg,
            args,
            exc_info=None,
            extra=None,
            stack_info=False,
            stacklevel=1,
            key=None,
            value=None):
        # Extend the 'extra' dictionary to include 'key' and 'value'
        assert key is not None and key != "", \
            "You can't pass an empty or null key"
        if extra is None:
            extra = dict()
        extra['key'] = key
        extra['value'] = value
        # Call the original _log method with the extended 'extra'
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)


def _build_monitor_logger(
    logger_name: str,
    level: int,
    monitor_file: str,
    dynamic_date: bool = True
) -> lg.Logger:
    """Creates a new MonitorLogger object with the configurations passed
    as parameters: name, level, monitor_file and dynamic_date.
    """
    assert logger_name not in lg.Logger.manager.loggerDict, \
        f"Can't create a logger named {logger_name}, it's already created"
    lg.setLoggerClass(MonitorLogger)
    monitoring_logger = lg.getLogger(logger_name)
    lg.setLoggerClass(lg.Logger)  # set it to normal again

    monitoring_logger.setLevel(level)

    if dynamic_date:
        monitor_file = _add_dynamic_date(monitor_file)

    _create_log_folder(monitor_file)
    _initialize_log_headers(monitor_file)
    default_file_handeler = lg.FileHandler(monitor_file)

    log_format = '"%(asctime)s",%(name)s,%(levelname)s,"%(message)s","%(key)s","%(value)s"'  # noqa:E501
    default_file_handeler.setFormatter(lg.Formatter(log_format))
    monitoring_logger.addHandler(default_file_handeler)

    return monitoring_logger


def setup_default_monitor(
    return_monitor: bool = False
) -> Optional[lg.Logger]:
    """This function initializes a MonitorLogger with a default configuration.

    Optionally, the function returns the monitor object by setting
    return_monitor to True. You can also get the monitor in other scopes
    by calling ``logging.getLogger("monitor")``
    Default configurations are:

    + name: "monitor"
    + file: ``logs/monitoring_exit_<YYYYMMDD>.log``
    + log_level: ``logging.INFO``
    """
    monitor_name = DEFAULT_MONITOR_NAME
    monitor_file = DEFAULT_MONITOR_FILE
    if monitor_name not in lg.Logger.manager.loggerDict:
        _ = _build_monitor_logger(
            monitor_name,
            lg.INFO,
            monitor_file
        )
    else:
        warnings.warn(
            f"Setting up an already created Logger with name {monitor_name}",
            UserWarning, stacklevel=2)

    if return_monitor:
        return lg.getLogger(monitor_name)
    return None


def setup_monitor(
    monitor_name: str = "monitor",
    level: int = lg.INFO,
    monitor_file: str = "logs/monitoring_exit.log",
    dynamic_date: bool = True,
    return_monitor: bool = False
) -> Optional[lg.Logger]:
    """This function initializes a monitor logger with the given configuration.

    Optionally, the function returns the monitor object by setting
    return_monitor to True. You can also get the monitor in other scopes
    by calling ``logging.getLogger(monitor_name)``. All parameters have default
    values

    Parameters
        logger_name: (str)
            The name of the MonitorLogger (subclass of Logger) object
        level: (int)
            Level at wich monitor logs will be shown
        monitor_file: (str)
            The file where logs will be stored
        dynamic_date: (bool)
            Whether to add the date suffix after the monitor_file, obtaining a
            file like this: ``<monitor_file>_<YYYYMMDD>.log``
    """
    if monitor_name not in lg.Logger.manager.loggerDict:
        _ = _build_monitor_logger(
            monitor_name,
            level,
            monitor_file,
            dynamic_date
        )
    else:
        warnings.warn(
            f"Setting up an already created Logger with name {monitor_name}",
            UserWarning, stacklevel=2)

    if return_monitor:
        return lg.getLogger(monitor_name)
    return None


def setup_monitor_from_args(
        args: argparse.Namespace,
        return_monitor: bool = False
) -> Optional[lg.Logger]:
    """Same as setup_monitor but uses an argparse.Namespace to define the
    configuration.
    """
    if args.monitor_name not in lg.Logger.manager.loggerDict:
        _ = _build_monitor_logger(
            args.monitor_name,
            args.log_level,
            args.monitor_file_name,
            args.add_dynamic_date
        )
    else:
        warnings.warn(
            f"Setting up an already created Logger with name {args.monitor_name}",  # noqa: E501
            UserWarning, stacklevel=2)

    if return_monitor:
        return lg.getLogger(args.monitor_name)
    return None


def inject_default_monitor(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    A decorator that injects a monitor logger into the decorated function.

    This decorator modifies the function by adding a ``monitor`` parameter
    automatically before calling the function. It retrieves the default monitor
    logger (with name "monitor").

    Note
    ----
    The decorated function must be designed to accept a 'monitor' keyword
    argument. This implementation does not handle the case where the
    function already has a 'monitor' keyword argument or uses *args and
    **kwargs in a way that conflicts with the automatic injection of the
    monitor.


    Parameters
        func : Callable
            The function to decorate.

    Returns
        Callable
            A wrapper function that adds the monitor to ``func``'s
            arguments.

    Example
        .. code-block:: python

            @inject_default_monitor
            def process_data(data, monitor=None):
                monitor.info(
                    "Processing data",
                    key="data_value", value=data
                )
                pass

            # call the function without passing a monitor
            process_data(data)

    """
    if DEFAULT_MONITOR_NAME not in lg.Logger.manager.loggerDict:
        setup_default_monitor()

    @wraps(func)
    def wrapper(*args, **kwargs):
        monitor = lg.getLogger(DEFAULT_MONITOR_NAME)
        return func(*args, monitor=monitor, **kwargs)

    return wrapper


def inject_named_monitor(monitor_name: str):
    """
    A decorator that injects a monitor logger into the decorated function,
    with a given name.

    This decorator modifies the function by adding a ``monitor`` parameter
    automatically before calling the function. It retrieves a monitor instance
    using the passed argument monitor_name, which helps in tracking.

    Note
    ----
    + The decorated function must be designed to accept a 'monitor' keyword
      argument. This implementation does not handle the case where the
      function already has a 'monitor' keyword argument or uses *args and
      *kwargs in a way that conflicts with the automatic injection of the
      logger.
    + The monitor must be initialized before injecting it. Else, the logger
      returned will be a base lg.Logger object with the default configuration.


    Parameters
        monitor_name : str
            The name of the monitor to be used. Cant't be an empty string.

    Returns
        Callable
            A wrapper function that adds the logger to ``func``'s arguments.

    Examples
        .. code-block:: python

            @inject_named_monitor("my_monitor")
            def process_data(data, monitor=None):
                monitor.info(
                    "Processing data",
                    key="data_value", value=data
                )
                pass

            # call the function without passing a monitor logger
            process_data(data)

    """
    assert monitor_name is not None and monitor_name != "", \
        "Monitor name can't be empty or None"

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            monitor = lg.getLogger(monitor_name)
            return func(*args, monitor=monitor, **kwargs)

        return wrapper
    return decorator
