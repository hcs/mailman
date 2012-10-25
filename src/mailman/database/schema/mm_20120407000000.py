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

"""3.0b1 -> 3.0b2 schema migrations.

All column changes are in the `mailinglist` table.

* Renames:
 - news_prefix_subject_too -> nntp_prefix_subject_too
 - news_moderation         -> newsgroup_moderation

* Collapsing:
 - archive, archive_private -> archive_policy

* Remove:
 - archive_volume_frequency
 - generic_nonmember_action
 - nntp_host

* Added:
 - list_id

* Changes:
  member.mailing_list holds the list_id not the fqdn_listname

See https://bugs.launchpad.net/mailman/+bug/971013 for details.
"""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'upgrade',
    ]


from mailman.interfaces.archiver import ArchivePolicy


VERSION = '20120407000000'
_helper = None



def upgrade(database, store, version, module_path):
    if database.TAG == 'sqlite':
        upgrade_sqlite(database, store, version, module_path)
    else:
        upgrade_postgres(database, store, version, module_path)



def archive_policy(archive, archive_private):
    """Convert archive and archive_private to archive_policy."""
    if archive == 0:
        return int(ArchivePolicy.never)
    elif archive_private == 1:
        return int(ArchivePolicy.private)
    else:
        return int(ArchivePolicy.public)



def upgrade_sqlite(database, store, version, module_path):
    # Load the first part of the migration.  This creates a temporary table to
    # hold the new mailinglist table columns.  The problem is that some of the
    # changes must be performed in Python, so after the first part is loaded,
    # we do the Python changes, drop the old mailing list table, and then
    # rename the temporary table to its place.
    database.load_schema(
        store, version, 'sqlite_{0}_01.sql'.format(version), module_path)
    results = store.execute("""
        SELECT id, include_list_post_header,
        news_prefix_subject_too, news_moderation,
        archive, archive_private, list_name, mail_host
        FROM mailinglist;
        """)
    for value in results:
        (id, list_post,
         news_prefix, news_moderation,
         archive, archive_private,
         list_name, mail_host) = value
        # Figure out what the new archive_policy column value should be.
        list_id = '{0}.{1}'.format(list_name, mail_host)
        fqdn_listname = '{0}@{1}'.format(list_name, mail_host)
        store.execute("""
            UPDATE ml_backup SET
                allow_list_posts = {0},
                newsgroup_moderation = {1},
                nntp_prefix_subject_too = {2},
                archive_policy = {3},
                list_id = '{4}'
            WHERE id = {5};
            """.format(
                list_post,
                news_moderation,
                news_prefix,
                archive_policy(archive, archive_private),
                list_id,
                id))
        # Also update the member.mailing_list column to hold the list_id
        # instead of the fqdn_listname.
        store.execute("""
            UPDATE member SET
                mailing_list = '{0}'
            WHERE mailing_list = '{1}';
            """.format(list_id, fqdn_listname))
    # Pivot the backup table to the real thing.
    store.execute('DROP TABLE mailinglist;')
    store.execute('ALTER TABLE ml_backup RENAME TO mailinglist;')
    # Now add some indexes that were previously missing.
    store.execute(
        'CREATE INDEX ix_mailinglist_list_id ON mailinglist (list_id);')
    store.execute(
        'CREATE INDEX ix_mailinglist_fqdn_listname '
        'ON mailinglist (list_name, mail_host);')
    # Now, do the member table.
    results = store.execute('SELECT id, mailing_list FROM member;')
    for id, mailing_list in results:
        list_name, at, mail_host = mailing_list.partition('@')
        if at == '':
            list_id = mailing_list
        else:
            list_id = '{0}.{1}'.format(list_name, mail_host)
        store.execute("""
            UPDATE mem_backup SET list_id = '{0}'
            WHERE id = {1};
            """.format(list_id, id))
    # Pivot the backup table to the real thing.
    store.execute('DROP TABLE member;')
    store.execute('ALTER TABLE mem_backup RENAME TO member;')



def upgrade_postgres(database, store, version, module_path):
    # Get the old values from the mailinglist table.
    results = store.execute("""
        SELECT id, archive, archive_private, list_name, mail_host 
        FROM mailinglist;
        """)
    # Do the simple renames first.
    store.execute("""
        ALTER TABLE mailinglist
           RENAME COLUMN news_prefix_subject_too TO nntp_prefix_subject_too;
        """)
    store.execute("""
        ALTER TABLE mailinglist
           RENAME COLUMN news_moderation TO newsgroup_moderation;
        """)
    store.execute("""
        ALTER TABLE mailinglist
           RENAME COLUMN include_list_post_header TO allow_list_posts;
        """)
    # Do the easy column drops next.
    for column in ('archive_volume_frequency',
                   'generic_nonmember_action',
                   'nntp_host'):
        store.execute(
            'ALTER TABLE mailinglist DROP COLUMN {0};'.format(column))
    # Now do the trickier collapsing of values.  Add the new columns.
    store.execute('ALTER TABLE mailinglist ADD COLUMN archive_policy INTEGER;')
    store.execute('ALTER TABLE mailinglist ADD COLUMN list_id TEXT;')
    # Query the database for the old values of archive and archive_private in
    # each column.  Then loop through all the results and update the new
    # archive_policy from the old values.
    for value in results:
        id, archive, archive_private, list_name, mail_host = value
        list_id = '{0}.{1}'.format(list_name, mail_host)
        store.execute("""
            UPDATE mailinglist SET
                archive_policy = {0},
                list_id = '{1}'
            WHERE id = {2};
            """.format(archive_policy(archive, archive_private), list_id, id))
    # Now drop the old columns.
    for column in ('archive', 'archive_private'):
        store.execute(
            'ALTER TABLE mailinglist DROP COLUMN {0};'.format(column))
    # Now add some indexes that were previously missing.
    store.execute(
        'CREATE INDEX ix_mailinglist_list_id ON mailinglist (list_id);')
    store.execute(
        'CREATE INDEX ix_mailinglist_fqdn_listname '
        'ON mailinglist (list_name, mail_host);')
    # Now, do the member table.
    results = store.execute('SELECT id, mailing_list FROM member;')
    store.execute('ALTER TABLE member ADD COLUMN list_id TEXT;')
    for id, mailing_list in results:
        list_name, at, mail_host = mailing_list.partition('@')
        if at == '':
            list_id = mailing_list
        else:
            list_id = '{0}.{1}'.format(list_name, mail_host)
        store.execute("""
            UPDATE member SET list_id = '{0}'
            WHERE id = {1};
            """.format(list_id, id))
    store.execute('ALTER TABLE member DROP COLUMN mailing_list;')
    # Record the migration in the version table.
    database.load_schema(store, version, None, module_path)
