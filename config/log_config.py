import logging.config
import os
import pathlib

from yaml import safe_load

LOG_DIR_PATH = pathlib.Path(os.path.join('log'))


def config():
    create_log_dir()

    logging.config.dictConfig(safe_load(get_log_config()))


def create_log_dir():
    LOG_DIR_PATH.mkdir(parents=True, exist_ok=True)


def get_log_config():
    return get_log_config_path().read_text(encoding="UTF-8")


def get_log_config_path():
    return pathlib.Path(__file__).with_suffix(".yaml")


if __name__ == "__main__":
    config()

    root = logging.getLogger()
    root.debug("Root logs debug example")
    root.info("Root logs written to console without colours")
    root.warning("Root logs warning")
    root.error("Root logs error")
    root.critical("Root logs critical")

    unknown = logging.getLogger("unknown")
    unknown.debug("Unknown logs debug example")
    unknown.info("Unknown logs propagated to root logger")
    unknown.warning("Unknown logs warning")
    unknown.error("Unknown logs error")
    unknown.critical("Unknown logs critical")

    application = logging.getLogger("application")
    application.debug("Application logs debug filtered by log level")
    application.info("Application logs written to console and file")
    application.warning("Application logs not propagated to the root logger")
    application.error("Application logs error example")
    application.critical("Application logs critical example")

    example = logging.getLogger("example")
    example.debug("Example logs debug filtered by log level")
    example.info("Example logs configured to write to file")
    example.warning("Example logs propagated to the root logger")
    example.error("Example logs error example")
    example.critical("Example logs critical example")
