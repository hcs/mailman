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

"""PostgreSQL database support."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'PostgreSQLDatabase',
    'make_temporary',
    ]


import types

from functools import partial
from operator import attrgetter
from urlparse import urlsplit, urlunsplit

from mailman.database.base import StormBaseDatabase
from mailman.testing.helpers import configuration



class PostgreSQLDatabase(StormBaseDatabase):
    """Database class for PostgreSQL."""

    TAG = 'postgres'

    def _database_exists(self, store):
        """See `BaseDatabase`."""
        table_query = ('SELECT table_name FROM information_schema.tables '
                       "WHERE table_schema = 'public'")
        results = store.execute(table_query)
        table_names = set(item[0] for item in results)
        return 'version' in table_names

    def _post_reset(self, store):
        """PostgreSQL-specific test suite cleanup.

        Reset the <tablename>_id_seq.last_value so that primary key ids
        restart from zero for new tests.
        """
        super(PostgreSQLDatabase, self)._post_reset(store)
        from mailman.database.model import ModelMeta
        classes = sorted(ModelMeta._class_registry,
                         key=attrgetter('__storm_table__'))
        # Recipe adapted from
        # http://stackoverflow.com/questions/544791/
        # django-postgresql-how-to-reset-primary-key
        for model_class in classes:
            store.execute("""\
                SELECT setval('"{0}_id_seq"', coalesce(max("id"), 1),
                              max("id") IS NOT null)
                       FROM "{0}";
                """.format(model_class.__storm_table__))



# Test suite adapter for ITemporaryDatabase.

def _cleanup(self, store, tempdb_name):
    from mailman.config import config
    store.rollback()
    store.close()
    # From the original database connection, drop the now unused database.
    config.db.store.execute('DROP DATABASE {0}'.format(tempdb_name))


def make_temporary(database):
    """Adapts by monkey patching an existing PostgreSQL IDatabase."""
    from mailman.config import config
    parts = urlsplit(config.database.url)
    assert parts.scheme == 'postgres'
    new_parts = list(parts)
    new_parts[2] = '/mmtest'
    url = urlunsplit(new_parts)
    # Use the existing database connection to create a new testing
    # database.
    config.db.store.execute('ABORT;')
    config.db.store.execute('CREATE DATABASE mmtest;')
    with configuration('database', url=url):
        database.initialize()
    database._cleanup = types.MethodType(
        partial(_cleanup, store=database.store, tempdb_name='mmtest'),
        database)
    # bool column values in PostgreSQL.
    database.FALSE = 'False'
    database.TRUE = 'True'
    return database
