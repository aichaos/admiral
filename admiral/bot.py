#!/usr/bin/env python3

import datetime
import json
import logging
import os
import os.path
import re
from rivescript import RiveScript
from yamlsettings import YamlSettings

from admiral.console import Logger
from admiral.interfaces import Interface

class AdmiralBot(object):
    """Chatbot instance for Admiral."""

    ###
    # Initialization and Configuration
    ###

    def __init__(self, debug=False, config="settings.yml",
                 defaults="defaults.yml", log_console=True):
        """Initialize the Admiral chatbot.

        Parameters:
        * debug:  Enable debug logging to the console.
        * config: The configuration file to use (default settings.yml)
        * defaults: The name of the default config file (defaults.yml)
        * log_console: Write logs to the console (STDOUT) as well as to the
                       log file on disk (default True).
        """

        # Configurable parameters.
        self.debug = debug
        self.config = config
        self.config_defaults = defaults

        # Internal state variables.
        self.running = False  # Whether we're up and running
        self.c = dict()       # App configuration
        self.bots = dict()    # Individual bot interfaces
        self.rs = None        # RiveScript brain

        # Load the bot's config.
        self.load_config()
        self.log = Logger(filename=self.c.logging.status,
                          console=log_console,
                          log_format=self.c.logging.format)
        if debug:
            self.log.set_level(logging.DEBUG)
            self.log.debug("Debug logging enabled.")

        # Run post-config initialization routines.
        self.setup()

    def load_config(self):
        """Load the configuration file from disk."""
        project_settings = YamlSettings(self.config_defaults, self.config,
                                        default_section="admiral")
        self.c = project_settings.get_settings()

    ###
    # Initial Setup Steps
    ###

    def setup(self):
        """Run the setup steps."""
        self.log.info("Welcome to Admiral.")

        # Initialize the RiveScript brain.
        self.reload_brain()

        # Scan through the interfaces and find active bots.
        self.log.info("Setting up interfaces...")
        for interface in self.c.interfaces:
            if not interface.enabled:
                continue

            if interface.id in self.bots:
                self.panic("Duplicate ID: you have two or more interfaces "
                    "that use the ID name `{}` in your bot settings. You "
                    "should pick a unique ID name for each interface!")
            self.bots[interface.id] = interface

            # Get the interface class.
            module = Interface.import_interface(interface.interface)
            self.bots[interface.id].inst = module(master=self)
            self.bots[interface.id].inst.setup(interface)

    def reload_brain(self):
        """(Re)load the RiveScript brain for the bot."""
        self.log.info("Loading RiveScript brain from {}".format(
            self.c.personality.replies
        ))

        self.rs = RiveScript(
            debug=self.c.debug.rivescript,
            utf8=True,
        )
        self.rs.load_directory(self.c.personality.replies)
        self.rs.sort_replies()

    ###
    # Start, stop, run commands.
    ###

    def start(self):
        """Start up all the bots."""
        if not self.running:
            for name, bot in self.bots.items():
                bot.inst.connect()
            self.running = True

    def run(self):
        """Start and run the bot's main loop."""
        self.start()
        while self.running:
            for name, bot in self.bots.items():
                bot.inst.do_one_loop()

    ###
    # Event handlers.
    ###

    def on_message(self, bot, username, remote_username, message):
        """Handle a message from an end user.

        Parameters:
        * bot: A reference to the interface that received the message.
        * username: A unique name for the end user, typically with the
                    interface name prefixed, like `SLACK-kirsle`
        * remote_username: The 'real' username, as the interface knows it.
        * message: The text of the user's message.
        """

        # Load this user's variables.
        self.load_uservars(username)

        # Get a reply for the user.
        reply = self.rs.reply(username, message)

        # Log the transaction.
        self.log_chat(username, message, reply)

        # Store the user's variables.
        self.save_uservars(username)

        # Send the response back.
        # TODO: handle queueing and delayed responses.
        bot.send_message(remote_username, reply)

    def log_chat(self, username, message, reply):
        """Log the chat transaction to disk."""

        # Each user gets their own log directory.
        sanitized = re.sub(r'[^A-Za-z0-9_\-@]+', '', username)
        outdir = os.path.join("logs", "chats", sanitized)
        outfile = os.path.join(outdir, "{}.log".format(sanitized))
        if not os.path.isdir(outdir):
            os.makedirs(outdir, mode=0o755)

        self.log.info("[{}] {}".format(username, message))
        self.log.info("[{}] {}".format(self.c.personality.name, reply))

        with open(outfile, "a", encoding="utf-8") as fh:
            today = datetime.datetime.today()
            ts = today.strftime(self.c.logging.date_format)
            fh.write("{today}\n"
                "[{username}] {message}\n"
                "[{bot}] {reply}\n\n".format(
                today=ts,
                username=username,
                message=message,
                bot=self.c.personality.name,
                reply=reply,
                ))

    def load_uservars(self, username):
        """Load a user's variables from disk."""
        if not os.path.isdir("users"):
            os.mkdir("users")

        sanitized = re.sub(r'[^A-Za-z0-9_\-@]+', '', username)
        filename = "users/{}.json".format(sanitized)
        if not os.path.isfile(filename):
            return

        with open(filename, "r", encoding="utf-8") as fh:
            data = fh.read()
            try:
                params = json.loads(data)
                print(params)
                for key, value in params.items():
                    if type(value) is str:
                        self.rs.set_uservar(username, key, value)
                        print("SET VAR:", username, key, value)
            except:
                pass

    def save_uservars(self, username):
        """Save a user's variables to disk."""
        if not os.path.isdir("users"):
            os.mkdir("users")

        sanitized = re.sub(r'[^A-Za-z0-9_\-@]+', '', username)
        filename = "users/{}.json".format(sanitized)

        with open(filename, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(self.rs.get_uservars(username)))

    ###
    # Utility/Misc functions.
    ###

    def panic(self, error):
        """Exit with a fatal error message."""
        self.log.error(error)
        raise RuntimeError(error)
