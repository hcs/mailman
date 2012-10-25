# Copyright (C) 2006-2012 by the Free Software Foundation, Inc.
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

"""Base class for all database classes."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'Model',
    ]


from operator import attrgetter

from storm.properties import PropertyPublisherMeta



class ModelMeta(PropertyPublisherMeta):
    """Do more magic on table classes."""

    _class_registry = set()

    def __init__(self, name, bases, dict):
        # Before we let the base class do it's thing, force an __storm_table__
        # property to enforce our table naming convention.
        self.__storm_table__ = name.lower()
        super(ModelMeta, self).__init__(name, bases, dict)
        # Register the model class so that it can be more easily cleared.
        # This is required by the test framework so that the corresponding
        # table can be reset between tests.
        #
        # The PRESERVE flag indicates whether the table should be reset or
        # not.  We have to handle the actual Model base class explicitly
        # because it does not correspond to a table in the database.
        if not getattr(self, 'PRESERVE', False) and name != 'Model':
            ModelMeta._class_registry.add(self)

    @staticmethod
    def _reset(store):
        from mailman.config import config
        config.db._pre_reset(store)
        # Make sure this is deterministic, by sorting on the storm table name.
        classes = sorted(ModelMeta._class_registry,
                         key=attrgetter('__storm_table__'))
        for model_class in classes:
            store.find(model_class).remove()



class Model:
    """Like Storm's `Storm` subclass, but with a bit extra."""
    __metaclass__ = ModelMeta
