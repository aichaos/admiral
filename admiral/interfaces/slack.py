#!/usr/bin/env python3

"""Slack interface for Admiral.

Commands specific to the Slack interface:

In channels, prefix the command with the bot's username:
* `!leave` - Make the bot leave a channel.
"""

import re
from slackclient import SlackClient
import time

from admiral.interfaces import Interface

class SlackInterface(Interface):
    """Slack chat interface for Admiral.

    Configuration parameters:
    * api_token: Slack API token for a Bot integration.
    """

    def name(self):
        """Return the name of this interface."""
        return "Slack"

    def setup(self, config):
        self.log.info("Set up Slack interface: {}".format(config.id))
        self.last_ping = 0
        self.token = config.api_token
        self.username = config.username
        self.client = None

        # Internal mappings.
        self.user_by_id = dict()      # User ID => details
        self.id_by_name = dict()      # User name => ID
        self.channel_by_uid = dict()  # User ID => channel ID

    def connect(self):
        self.client = SlackClient(self.token)
        self.client.rtm_connect()

        # Cache all the users information.
        for user in self.client.server.users:
            self.user_by_id[user.id] = user
            self.id_by_name[user.name] = user.id

        # Our user ID for @mentions.
        self.user_id = self.id_by_name[self.username]

    def do_one_loop(self):
        """Look for new messages."""
        for message in self.client.rtm_read():
            self.handle_api_message(message)
            self.ping()

    def handle_api_message(self, message):
        """Handle an incoming message from Slack."""
        if "type" in message:
            if message["type"] == "message":
                # Is it a direct message or channel?
                if message["channel"].startswith("D"):
                    # Direct.
                    self.handle_message(message)
                else:
                    # Channel. Message must be prefixed by our username.
                    at_mention = "@" + self.user_id
                    if message["text"].lower().startswith(self.username) or \
                       at_mention in message["text"]:
                        # Handle the message just the same.
                        self.handle_message(message, in_channel=True)

    def handle_message(self, message, in_channel=False):
        """Handle a message that will actually elicit a response."""
        # Store their channel ID for the response.
        self.channel_by_uid[message["user"]] = message["channel"]

        # Get their friendly username.
        username = self.user_by_id[message["user"]].name

        # Format the message.
        message_data = message
        message = re.sub(
            r'^{username}\s*|<?@{username}>?'.format(username=self.username),
            '',
            message["text"]
        )
        if len(message.strip()) > 0:
            # Handle commands.
            if not self.slack_commands(username, message, message_data, in_channel):
                self.on_message(
                    username=username,
                    message=message,
                )

    def send_message(self, username, message):
        """Send a message to the user."""
        self.log.debug("Send Slack message to [{}] {}".format(
            username, message,
        ))

        # Get their channel info.
        try:
            user_id = self.id_by_name[username]
            channel_id = self.channel_by_uid[user_id]
        except KeyError:
            return

        channel = self.client.server.channels.find(channel_id)
        if channel:
            channel.send_message(message)

    def slack_commands(self, username, message, data, in_channel):
        """Process Slack-specific commands in messages.

        Returns True if the message was intercepted by a command.

        Parameters:
        * username
        * message: Just the text of the message.
        * data: The full RTM message payload.
        * in_channel: Whether this is in a public channel or a DM.
        """
        if in_channel:
            if message.startswith("!leave"):
                # Leaving a channel.
                channel = data["channel"]
                self.log.info("Asked to leave channel {} by {}".format(
                    channel, username))
                self.log.debug("Slack API:{}".format(
                    self.client.api_call("channels.leave", channel=channel)
                ))
                return True
        return False

    def ping(self):
        """Ping Slack."""
        now = int(time.time())
        if now > self.last_ping:
            self.client.server.ping()
            self.last_ping = now
