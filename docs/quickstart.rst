Quickstart
++++++++++

In this page an example of how to install the library and how to use it is provided.


Installation
============

To install the library, use pip:

.. code-block:: sh

    pip install log4data

Usage
=====

Basic Usage
-----------

To start using the library, import it in your script, and use the default configuration if you don't want to manually configure the logger.

.. code-block:: python

    import src.log4data.main as l4d
    import logging as lg

    if __name__ == "__main__":
        l4d.default_setup_logger()
        lg.info("Setup complete")

With just a few lines of code, you can set up effective logging. This will generate a log like this:

.. code-block::

    2024-07-03 00:00:00,000 - root - INFO - We are logging!

Advanced Usage
--------------

You can also parametrize the file name or the logging level:

.. code-block:: python

    # main.py
    import log4data as l4d
    import logging as lg

    if __name__ == "__main__":
        args = l4d.set_log_args(return_args=True)
        l4d.setup_logger(args)
        lg.info("Setup complete")

Then call python:

.. code-block:: sh

    python main.py -lglv debug -lgfn etl.log

Using the `@inject_logger` Decorator
------------------------------------

The `@inject_logger` decorator automatically adds a logger to a function, named after that function:

.. code-block:: python

    # main.py
    import argparse
    import logging as lg
    import log4data as l4d

    @l4d.inject_logger
    def my_data_processing_function(data, logger=None):
        logger.info(f"Processing data: {data}")
        print(data)
        return data

    if __name__ == "__main__":
        # parse arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", "--data", type=str, default="sample data")
        l4d.set_log_args(parser)
        args = parser.parse_args()

        # Configure logging
        l4d.setup_logger(args)

        # Call the function without providing the logger manually
        my_data_processing_function(args.data)

Calling this:

.. code-block:: sh

    python main.py -d "Hello log for data."

Results in this log:

.. code-block::

    2024-07-03 00:00:00,000 - my_data_processing_function - INFO - Processing data: Hello log for data.
