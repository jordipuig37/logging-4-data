import log4data as l4d
import logging as lg


if __name__ == "__main__":
    args = l4d.set_log_args(return_args=True)
    l4d.setup_logger(args)

    lg.info("Setup complete")
