Library Reference
=====================

Setup functions
+++++++++++++++
This group of functions helps you setup the logging in the base level. All are
directed to work with scripting except for `get_stream_logger`, which is meant
to be used in notebooks.

.. autofunction:: log4data.setup_log_args
.. autofunction:: log4data.setup_default_logger
.. autofunction:: log4data.setup_logger
.. autofunction:: log4data.setup_logger_from_args
.. autofunction:: log4data.get_stream_logger

Injectors
+++++++++
This functions are decorators to add a specific logger to functions that take
logger as an argument. 

.. autofunction:: log4data.inject_logger
.. autofunction:: log4data.inject_named_logger

Monitoring
++++++++++

.. autofunction:: log4data.setup_monitoring_args
.. autofunction:: log4data.setup_default_monitor
.. autofunction:: log4data.setup_monitor
.. autofunction:: log4data.setup_monitor_from_args
.. autofunction:: log4data.inject_default_monitor
.. autofunction:: log4data.inject_named_monitor

Utils
+++++

.. autofunction:: log4data.delete_old_log_files
