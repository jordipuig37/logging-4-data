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
