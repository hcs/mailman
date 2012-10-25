# Copyright (C) 2009-2012 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

"""The 'help' subcommand."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'Help',
    ]


from zope.interface import implementer

from mailman.interfaces.command import ICLISubCommand



@implementer(ICLISubCommand)
class Help:
    # Lowercase, to match argparse's default --help text.
    """show this help message and exit"""

    name = 'help'

    def add(self, parser, command_parser):
        """See `ICLISubCommand`."""
        self.parser = parser

    def process(self, args):
        """See `ICLISubCommand`."""
        self.parser.print_help()
