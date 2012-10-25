=================
Schema migrations
=================

The SQL database schema will over time require upgrading to support new
features.  This is supported via schema migration.

Migrations are embodied in individual Python classes, which themselves may
load SQL into the database.  The naming scheme for migration files is:

    mm_YYYYMMDDHHMMSS_comment.py

where `YYYYMMDDHHMMSS` is a required numeric year, month, day, hour, minute,
and second specifier providing unique ordering for processing.  Only this
component of the file name is used to determine the ordering.  The prefix is
required due to Python module naming requirements, but it is actually
ignored.  `mm_` is reserved for Mailman's own use.

The optional `comment` part of the file name can be used as a short
description for the migration, although comments and docstrings in the
migration files should be used for more detailed descriptions.

Migrations are applied automatically when Mailman starts up, but can also be
applied at any time by calling in the API directly.  Once applied, a
migration's version string is registered so it will not be applied again.

We see that the base migration, as well as subsequent standard migrations, are
already applied.

    >>> from mailman.model.version import Version
    >>> results = config.db.store.find(Version, component='schema')
    >>> results.count()
    2
    >>> versions = sorted(result.version for result in results)
    >>> for version in versions:
    ...     print version
    00000000000000
    20120407000000


Migrations
==========

Migrations can be loaded at any time, and can be found in the migrations path
specified in the configuration file.

.. Create a temporary directory for the migrations::

    >>> import os, sys, tempfile
    >>> tempdir = tempfile.mkdtemp()
    >>> path = os.path.join(tempdir, 'migrations')
    >>> os.makedirs(path)
    >>> sys.path.append(tempdir)
    >>> config.push('migrations', """
    ... [database]
    ... migrations_path: migrations
    ... """)

.. Clean this up at the end of the doctest.
    >>> def cleanup():
    ...     import shutil
    ...     from mailman.config import config
    ...     config.pop('migrations')
    ...     shutil.rmtree(tempdir)
    >>> cleanups.append(cleanup)

Here is an example migrations module.  The key part of this interface is the
``upgrade()`` method, which takes four arguments:

 * `database` - The database class, as derived from `StormBaseDatabase`
 * `store` - The Storm `Store` object.
 * `version` - The version string as derived from the migrations module's file
   name.  This will include only the `YYYYMMDDHHMMSS` string.
 * `module_path` - The dotted module path to the migrations module, suitable
   for lookup in `sys.modules`.

This migration module just adds a marker to the `version` table.

    >>> with open(os.path.join(path, '__init__.py'), 'w') as fp:
    ...     pass
    >>> with open(os.path.join(path, 'mm_20129999000000.py'), 'w') as fp:
    ...     print >> fp, """
    ... from __future__ import unicode_literals
    ... from mailman.model.version import Version
    ... def upgrade(database, store, version, module_path):
    ...     v = Version(component='test', version=version)
    ...     store.add(v)
    ...     database.load_schema(store, version, None, module_path)
    ... """

This will load the new migration, since it hasn't been loaded before.

    >>> config.db.load_migrations()
    >>> results = config.db.store.find(Version, component='schema')
    >>> for result in sorted(result.version for result in results):
    ...     print result
    00000000000000
    20120407000000
    20129999000000
    >>> test = config.db.store.find(Version, component='test').one()
    >>> print test.version
    20129999000000

Migrations will only be loaded once.

    >>> with open(os.path.join(path, 'mm_20129999000001.py'), 'w') as fp:
    ...     print >> fp, """
    ... from __future__ import unicode_literals
    ... from mailman.model.version import Version
    ... _marker = 801
    ... def upgrade(database, store, version, module_path):
    ...     global _marker
    ...     # Pad enough zeros on the left to reach 14 characters wide.
    ...     marker = '{0:=#014d}'.format(_marker)
    ...     _marker += 1
    ...     v = Version(component='test', version=marker)
    ...     store.add(v)
    ...     database.load_schema(store, version, None, module_path)
    ... """

The first time we load this new migration, we'll get the 801 marker.

    >>> config.db.load_migrations()
    >>> results = config.db.store.find(Version, component='schema')
    >>> for result in sorted(result.version for result in results):
    ...     print result
    00000000000000
    20120407000000
    20129999000000
    20129999000001
    >>> test = config.db.store.find(Version, component='test')
    >>> for marker in sorted(marker.version for marker in test):
    ...     print marker
    00000000000801
    20129999000000

We do not get an 802 marker because the migration has already been loaded.

    >>> config.db.load_migrations()
    >>> results = config.db.store.find(Version, component='schema')
    >>> for result in sorted(result.version for result in results):
    ...     print result
    00000000000000
    20120407000000
    20129999000000
    20129999000001
    >>> test = config.db.store.find(Version, component='test')
    >>> for marker in sorted(marker.version for marker in test):
    ...     print marker
    00000000000801
    20129999000000


Partial upgrades
================

It's possible (mostly for testing purposes) to only do a partial upgrade, by
providing a timestamp to `load_migrations()`.  To demonstrate this, we add two
additional migrations, intended to be applied in sequential order.

    >>> from shutil import copyfile
    >>> from mailman.testing.helpers import chdir
    >>> with chdir(path):
    ...     copyfile('mm_20129999000000.py', 'mm_20129999000002.py')
    ...     copyfile('mm_20129999000000.py', 'mm_20129999000003.py')
    ...     copyfile('mm_20129999000000.py', 'mm_20129999000004.py')

Now, only migrate to the ...03 timestamp.

    >>> config.db.load_migrations('20129999000003')

You'll notice that the ...04 version is not present.

    >>> results = config.db.store.find(Version, component='schema')
    >>> for result in sorted(result.version for result in results):
    ...     print result
    00000000000000
    20120407000000
    20129999000000
    20129999000001
    20129999000002
    20129999000003


.. cleanup:
    Because the Version table holds schema migration data, it will not be
    cleaned up by the standard test suite.  This is generally not a problem
    for SQLite since each test gets a new database file, but for PostgreSQL,
    this will cause migration.rst to fail on subsequent runs.  So let's just
    clean up the database explicitly.

    >>> results = config.db.store.execute("""
    ...     DELETE FROM version WHERE version.version >= '201299990000'
    ...                            OR version.component = 'test';
    ...     """)
    >>> config.db.commit()
