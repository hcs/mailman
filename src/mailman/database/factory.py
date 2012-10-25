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

"""Database factory."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'DatabaseFactory',
    'DatabaseTemporaryFactory',
    'DatabaseTestingFactory',
    ]


import types

from zope.component import getAdapter
from zope.interface import implementer
from zope.interface.verify import verifyObject

from mailman.config import config
from mailman.interfaces.database import (
    IDatabase, IDatabaseFactory, ITemporaryDatabase)
from mailman.utilities.modules import call_name



@implementer(IDatabaseFactory)
class DatabaseFactory:
    """Create a new database."""

    @staticmethod
    def create():
        """See `IDatabaseFactory`."""
        database_class = config.database['class']
        database = call_name(database_class)
        verifyObject(IDatabase, database)
        database.initialize()
        database.load_migrations()
        database.commit()
        return database



def _reset(self):
    """See `IDatabase`."""
    from mailman.database.model import ModelMeta
    self.store.rollback()
    self._pre_reset(self.store)
    ModelMeta._reset(self.store)
    self._post_reset(self.store)
    self.store.commit()


@implementer(IDatabaseFactory)
class DatabaseTestingFactory:
    """Create a new database for testing."""

    @staticmethod
    def create():
        """See `IDatabaseFactory`."""
        database_class = config.database['class']
        database = call_name(database_class)
        verifyObject(IDatabase, database)
        database.initialize()
        database.load_migrations()
        database.commit()
        # Make _reset() a bound method of the database instance.
        database._reset = types.MethodType(_reset, database)
        return database



@implementer(IDatabaseFactory)
class DatabaseTemporaryFactory:
    """Create a temporary database for some of the migration tests."""

    @staticmethod
    def create():
        """See `IDatabaseFactory`."""
        database_class_name = config.database['class']
        database = call_name(database_class_name)
        verifyObject(IDatabase, database)
        adapted_database = getAdapter(
            database, ITemporaryDatabase, database.TAG)
        return adapted_database
