#!/usr/bin/env python3

"""Logging and console-related logic."""

import logging
import os

class Logger(object):
    def __init__(self, filename="logs/status.log", console=True,
                 log_format="%(asctime)s - %(levelname)s - %(message)s"):
        """Initialize the main logger for the Admiral bot.

        Parameters:
        * filename: The log file to write to.
        * console: Whether to also log to the console (STDOUT).
        * log_format: Format for the log lines to be written as.
        """
        self.logger = logging.getLogger("admiral")
        self.set_level(logging.INFO)

        # Make sure the log directory exists.
        self.mkpaths(filename)

        # Log formatting.
        formatter = logging.Formatter(log_format)

        # Console handler.
        if console:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        # File handler.
        fh = logging.FileHandler(filename, encoding="utf-8")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def mkpaths(self, filename):
        """Create the log directory."""
        parts = filename.split("/")
        parts.pop() # Remove the filename extension.
        if parts:
            path = "/".join(parts)
            if not os.path.isdir(path):
                os.makedirs(path, mode=0o755)

    def set_level(self, level):
        """Adjust the log level."""
        self.logger.setLevel(level)

    ### The following are proxies to the logging module ###

    def info(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message)

    def warn(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
