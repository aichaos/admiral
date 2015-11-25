#!/usr/bin/env python3

"""The admiral.interfaces namespace is for providing chat interfaces for the
Admiral bot.

A chat interface is how end users are able to communicate with your bot.
Examples are for connecting your bot to Slack or Hangouts or IRC, etc.

This module contains a base class that all interfaces should extend."""

from importlib import import_module

class Interface(object):
    def __init__(self, master):
        """Set up a new interface. You should NOT override this function!

        This init function receives a reference to the parent bot object as the
        `master`. The bot is available to your interface via `self.bot`."""
        self.bot = master

    def setup(self, config):
        """Run setup steps for your interface.

        The `config` parameter contains the interface configuration from the
        settings.yml, including any necessary authentication or API keys
        for your interface.

        This function should set up the connection and register handlers as
        needed; it should do everything up until the 'actually connect to
        server' step."""
        pass

    def connect(self):
        """Connect to your interface."""
        pass

    def do_one_loop(self):
        """Do one loop or poll for messages in your interface.

        This is called on a main loop by the main bot, once per interface."""
        pass

    def on_message(self, username, message):
        """Send an incoming message from a user up to the bot.

        You should *NOT* override this function.

        Parameters:
        * username: A unique name for the end user.
        * message: The text of the user's message."""

        # Prefix the username with the interface ID to make it unique across
        # different interfaces.
        user_id = "-".join([self.name().upper(), username])
        self.bot.on_message(self, user_id, username, message)

    def send_message(self, username, message):
        """The bot requests that your interface deliver a message to a user."""
        pass

    @property
    def log(self):
        """Alias to `self.bot.log` for logging from within the interface."""
        return self.bot.log

    @staticmethod
    def import_interface(name):
        """Dynamically import an interface at run-time."""
        module = import_module("admiral.interfaces.{}".format(name))
        class_name = name[0].upper() + name[1:].lower() + "Interface"
        return getattr(module, class_name)
