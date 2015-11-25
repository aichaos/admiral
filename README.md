# Admiral

Admiral is a Python chatbot that utilizes RiveScript and connects to some chat
platforms.

Currently it only connects to Slack. Integrating it with Google Hangouts (via
[hangups](https://github.com/tdryer/hangups)) is on the road map too.

# Requirements

This bot requires [Python 3](https://www.python.org/) to run. It's recommended
to use [virtualenv](https://virtualenv.readthedocs.org/en/latest/) and
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/) to
create an isolated environment to install this bot's dependencies in.

Quick start:

```bash
$ git clone https://github.com/aichaos/admiral
$ cd admiral/
$ mkvirtualenv -p /usr/bin/python3 admiral
(admiral)$ pip install -r requirements.txt
```

# Configuration

This bot is configured via a YAML config file. The default configuration comes
from the `defaults.yml` file, which you **should not edit.**

To configure the bot, create a file named `settings.yml` and fill in the keys
to override the desired settings from `defaults.yml`. For the lazy you can just
copy `defaults.yml` and name it `settings.yml` and then go through and edit it
in your text editor.

An example `settings.yml` which leaves all the defaults but just configures the
Slack interface would look like the following:

```yaml
admiral:
  interfaces:
    - interface: slack
      id: "Admiral-Slack"
      enabled: true
      username: admiral
      api_token: xxxfakekeyxxx
```

# Running the Bot

Run the bot by executing the `admiral-cli.py` script from your virtualenv.

Usage:

```
usage: admiral-cli.py [-h] [--debug] [--config CONFIG] [--quiet]

Admiral chatbot.

optional arguments:
  -h, --help            show this help message and exit
  --debug, -d           Enable debug mode (verbose logging to console).
  --config CONFIG, -c CONFIG
                        Configuration file to use, default is settings.yml
  --quiet, -q           Suppress logging to the console; only write logs into
                        the status log file (default is logs/status.log)
```

By default it will log INFO-level messages to your console as well as to the
`logs/admiral.log` file.

Chat messages with users are stored in the `logs/chats/` directory, one for
each username the bot interacted with.

# License

```
Admiral Chatbot
Copyright (C) 2015  Noah Petherbridge

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
```
