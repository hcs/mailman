# Copyright (C) 2012 by the Free Software Foundation, Inc.
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

"""Test the system-wide global configuration."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'TestConfiguration',
    ]


import unittest

from mailman.interfaces.configuration import ConfigurationUpdatedEvent
from mailman.testing.helpers import configuration, event_subscribers
from mailman.testing.layers import ConfigLayer



class TestConfiguration(unittest.TestCase):
    layer = ConfigLayer

    def test_push_and_pop_trigger_events(self):
        # Pushing a new configuration onto the stack triggers a
        # post-processing event.
        events = []
        def on_event(event):
            if isinstance(event, ConfigurationUpdatedEvent):
                # Record both the event and the top overlay.
                events.append(event.config.overlays[0].name)
        with event_subscribers(on_event):
            with configuration('test', _configname='my test'):
                pass
        # There should be two pushed configuration names on the list now, one
        # for the push leaving 'my test' on the top of the stack, and one for
        # the pop, leaving the ConfigLayer's 'test config' on top.
        self.assertEqual(events, ['my test', 'test config'])
