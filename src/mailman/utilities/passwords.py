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

"""A wrapper around passlib."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'handle_ConfigurationUpdatedEvent',
    ]



from passlib.context import CryptContext
from pkg_resources import resource_string

from mailman.interfaces.configuration import ConfigurationUpdatedEvent



class PasswordContext:
    def __init__(self, config):
        # Is the context coming from a file system or Python path?
        if config.passwords.path.startswith('python:'):
            resource_path = config.passwords.path[7:]
            package, dot, resource = resource_path.rpartition('.')
            config_string = resource_string(package, resource + '.cfg')
        else:
            with open(config.passwords.path, 'rb') as fp:
                config_string = fp.read()
        self._context = CryptContext.from_string(config_string)

    def encrypt(self, secret):
        return self._context.encrypt(secret)

    def verify(self, hashed, password):
        # Support hash algorithm migration.  Yes, the order of arguments is
        # reversed, for backward compatibility with flufl.password.  XXX fix
        # this eventually.
        return self._context.verify_and_update(password, hashed)



def handle_ConfigurationUpdatedEvent(event):
    if isinstance(event, ConfigurationUpdatedEvent):
        # Just reset the password context.
        event.config.password_context = PasswordContext(event.config)
