# Logging for Data Pipelines

This library simplifies the logging setup process for new data pipelines, eliminating the need to repeatedly look up logger configurations.

## Installation

Install the library via pip:

```sh
pip install log4data
```

## Usage

To start using the library, simply import it in your script, and use the default configuration if you don't want to manually configure the logger.

```python
import src.log4data.main as l4d
import logging as lg


if __name__ == "__main__":
    l4d.default_setup_logger()
    lg.info("Setup complete")
```

With just a few lines of code, you can set up effective logging. This will generate a log like this:

```log
2024-07-03 00:00:00,000 - root - INFO - We are logging!
```

A more advanced use of the library is parametrize the file name or the logging level like this:

```python
# main.py
import log4data as l4d
import logging as lg


if __name__ == "__main__":
    args = l4d.set_log_args(return_args=True)
    l4d.setup_logger_from_args(args)

    lg.info("Setup complete")
```

And then call python:

```sh
python main.py -lglv debug -lgfn etl.log
```

Finally, `@inject_logger` is a decorator to automatically add a logger to a function, named after that function. This is used like this:

```python
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
    l4d.setup_logger_from_args(args)

    # Call the function without providing the logger manually
    my_data_processing_function(args.data)
```

Then, calling this:

```sh
python main.py -d "Hello log for data."
```

Results in this log:

```log
2024-07-03 00:00:00,000 - my_data_processing_function - INFO - Processing data: Hello log for data.
```

## Contributing

This is a small project developed for my team and me, and while major upgrades are not planned, we welcome pull requests. If you encounter bugs or wish to suggest new features, please initiate a discussion by opening an issue.

## License

This repository is under the MIT license.
