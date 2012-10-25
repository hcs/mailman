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

"""SQLite database support."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'SQLiteDatabase',
    'make_temporary',
    ]


import os
import types
import shutil
import tempfile

from functools import partial
from urlparse import urlparse

from mailman.database.base import StormBaseDatabase
from mailman.testing.helpers import configuration



class SQLiteDatabase(StormBaseDatabase):
    """Database class for SQLite."""

    TAG = 'sqlite'

    def _database_exists(self, store):
        """See `BaseDatabase`."""
        table_query = 'select tbl_name from sqlite_master;'
        table_names = set(item[0] for item in
                          store.execute(table_query))
        return 'version' in table_names

    def _prepare(self, url):
        parts = urlparse(url)
        assert parts.scheme == 'sqlite', (
            'Database url mismatch (expected sqlite prefix): {0}'.format(url))
        path = os.path.normpath(parts.path)
        fd = os.open(path, os.O_WRONLY |  os.O_NONBLOCK | os.O_CREAT, 0666)
        # Ignore errors
        if fd > 0:
            os.close(fd)



# Test suite adapter for ITemporaryDatabase.

def _cleanup(self, tempdir):
    shutil.rmtree(tempdir)


def make_temporary(database):
    """Adapts by monkey patching an existing SQLite IDatabase."""
    tempdir = tempfile.mkdtemp()
    url = 'sqlite:///' + os.path.join(tempdir, 'mailman.db')
    with configuration('database', url=url):
        database.initialize()
    database._cleanup = types.MethodType(
        partial(_cleanup, tempdir=tempdir),
        database)
    # bool column values in SQLite must be integers.
    database.FALSE = 0
    database.TRUE = 1
    return database
