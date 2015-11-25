#!/usr/bin/env python3

import argparse
from admiral.bot import AdmiralBot

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Admiral chatbot.")
    parser.add_argument("--debug", "-d",
        help="Enable debug mode (verbose logging to console).",
        action="store_true",
    )
    parser.add_argument("--config", "-c",
        help="Configuration file to use, default is settings.yml",
        type=str,
        default="settings.yml",
    )
    parser.add_argument("--quiet", "-q",
        help="Suppress logging to the console; only write logs into the "
            "status log file (default is logs/status.log)",
        action="store_false",
    )
    args = parser.parse_args()

    bot = AdmiralBot(
        debug=args.debug,
        config=args.config,
        log_console=args.quiet,
    )
    bot.run()
