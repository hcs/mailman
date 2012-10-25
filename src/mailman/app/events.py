# Copyright (C) 2011-2012 by the Free Software Foundation, Inc.
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

"""Global events."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'initialize',
    ]


from zope import event

from mailman.app import domain, moderator, subscriptions
from mailman.core import i18n, switchboard
from mailman.languages import manager as language_manager
from mailman.styles import manager as style_manager
from mailman.utilities import passwords



def initialize():
    """Initialize global event subscribers."""
    event.subscribers.extend([
        domain.handle_DomainDeletingEvent,
        moderator.handle_ListDeletingEvent,
        passwords.handle_ConfigurationUpdatedEvent,
        subscriptions.handle_ListDeletingEvent,
        switchboard.handle_ConfigurationUpdatedEvent,
        i18n.handle_ConfigurationUpdatedEvent,
        style_manager.handle_ConfigurationUpdatedEvent,
        language_manager.handle_ConfigurationUpdatedEvent,
        ])
