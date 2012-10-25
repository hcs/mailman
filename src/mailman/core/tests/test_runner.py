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

"""Test some Runner base class behavior."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'TestRunner',
    ]


import unittest

from mailman.app.lifecycle import create_list
from mailman.config import config
from mailman.core.runner import Runner
from mailman.interfaces.runner import RunnerCrashEvent
from mailman.testing.helpers import (
    configuration, event_subscribers, get_queue_messages,
    make_testable_runner, specialized_message_from_string as mfs)
from mailman.testing.layers import ConfigLayer



class CrashingRunner(Runner):
    def _dispose(self, mlist, msg, msgdata):
        raise RuntimeError('borked')



class TestRunner(unittest.TestCase):
    """Test the Runner base class behavior."""

    layer = ConfigLayer

    def setUp(self):
        self._mlist = create_list('test@example.com')
        self._events = []

    def _got_event(self, event):
        self._events.append(event)

    @configuration('runner.crashing',
                   **{'class': 'mailman.core.tests.CrashingRunner'})
    def test_crash_event(self):
        runner = make_testable_runner(CrashingRunner, 'in')
        # When an exception occurs in Runner._process_one_file(), a zope.event
        # gets triggered containing the exception object.
        msg = mfs("""\
From: anne@example.com
To: test@example.com
Message-ID: <ant>

""")
        config.switchboards['in'].enqueue(msg, listname='test@example.com')
        with event_subscribers(self._got_event):
            runner.run()
        # We should now have exactly one event, which will contain the
        # exception, plus additional metadata containing the mailing list,
        # message, and metadata.
        self.assertEqual(len(self._events), 1)
        event = self._events[0]
        self.assertTrue(isinstance(event, RunnerCrashEvent))
        self.assertEqual(event.mailing_list, self._mlist)
        self.assertEqual(event.message['message-id'], '<ant>')
        self.assertEqual(event.metadata['listname'], 'test@example.com')
        self.assertTrue(isinstance(event.error, RuntimeError))
        self.assertEqual(event.error.message, 'borked')
        self.assertTrue(isinstance(event.runner, CrashingRunner))
        # The message should also have ended up in the shunt queue.
        shunted = get_queue_messages('shunt')
        self.assertEqual(len(shunted), 1)
        self.assertEqual(shunted[0].msg['message-id'], '<ant>')
