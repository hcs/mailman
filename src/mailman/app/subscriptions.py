# Copyright (C) 2009-2012 by the Free Software Foundation, Inc.
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

"""Module stuff."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'SubscriptionService',
    'handle_ListDeletingEvent',
    ]


from operator import attrgetter
from passlib.utils import generate_password as generate
from storm.expr import And, Or
from uuid import UUID
from zope.component import getUtility
from zope.interface import implementer

from mailman.app.membership import add_member, delete_member
from mailman.config import config
from mailman.core.constants import system_preferences
from mailman.database.transaction import dbconnection
from mailman.interfaces.address import IEmailValidator
from mailman.interfaces.listmanager import (
    IListManager, ListDeletingEvent, NoSuchListError)
from mailman.interfaces.member import DeliveryMode, MemberRole
from mailman.interfaces.subscriptions import (
    ISubscriptionService, MissingUserError)
from mailman.interfaces.usermanager import IUserManager
from mailman.model.member import Member



def _membership_sort_key(member):
    """Sort function for find_members().

    The members are sorted first by unique list id, then by subscribed email
    address, then by role.
    """
    return (member.list_id, member.address.email, int(member.role))



@implementer(ISubscriptionService)
class SubscriptionService:
    """Subscription services for the REST API."""

    __name__ = 'members'

    def get_members(self):
        """See `ISubscriptionService`."""
        # {list_id -> {role -> [members]}}
        by_list = {}
        user_manager = getUtility(IUserManager)
        for member in user_manager.members:
            by_role = by_list.setdefault(member.list_id, {})
            members = by_role.setdefault(member.role.name, [])
            members.append(member)
        # Flatten into single list sorted as per the interface.
        all_members = []
        address_of_member = attrgetter('address.email')
        for list_id in sorted(by_list):
            by_role = by_list[list_id]
            all_members.extend(
                sorted(by_role.get('owner', []), key=address_of_member))
            all_members.extend(
                sorted(by_role.get('moderator', []), key=address_of_member))
            all_members.extend(
                sorted(by_role.get('member', []), key=address_of_member))
        return all_members

    @dbconnection
    def get_member(self, store, member_id):
        """See `ISubscriptionService`."""
        members = store.find(
            Member,
            Member._member_id == member_id)
        if members.count() == 0:
            return None
        else:
            assert members.count() == 1, 'Too many matching members'
            return members[0]

    @dbconnection
    def find_members(self, store, subscriber=None, list_id=None, role=None):
        """See `ISubscriptionService`."""
        # If `subscriber` is a user id, then we'll search for all addresses
        # which are controlled by the user, otherwise we'll just search for
        # the given address.
        user_manager = getUtility(IUserManager)
        if subscriber is None and list_id is None and role is None:
            return []
        # Querying for the subscriber is the most complicated part, because
        # the parameter can either be an email address or a user id.
        query = []
        if subscriber is not None:
            if isinstance(subscriber, basestring):
                # subscriber is an email address.
                address = user_manager.get_address(subscriber)
                user = user_manager.get_user(subscriber)
                # This probably could be made more efficient.
                if address is None or user is None:
                    return []
                query.append(Or(Member.address_id == address.id,
                                Member.user_id == user.id))
            else:
                # subscriber is a user id.
                user = user_manager.get_user_by_id(subscriber)
                address_ids = list(address.id for address in user.addresses
                                   if address.id is not None)
                if len(address_ids) == 0 or user is None:
                    return []
                query.append(Or(Member.user_id == user.id,
                                Member.address_id.is_in(address_ids)))
        # Calculate the rest of the query expression, which will get And'd
        # with the Or clause above (if there is one).
        if list_id is not None:
            query.append(Member.list_id == list_id)
        if role is not None:
            query.append(Member.role == role)
        results = store.find(Member, And(*query))
        return sorted(results, key=_membership_sort_key)

    def __iter__(self):
        for member in self.get_members():
            yield member

    def join(self, list_id, subscriber,
             display_name=None,
             delivery_mode=DeliveryMode.regular,
             role=MemberRole.member):
        """See `ISubscriptionService`."""
        mlist = getUtility(IListManager).get_by_list_id(list_id)
        if mlist is None:
            raise NoSuchListError(list_id)
        # Is the subscriber an email address or user id?
        if isinstance(subscriber, basestring):
            # It's an email address, so we'll want a real name.  Make sure
            # it's a valid email address, and let InvalidEmailAddressError
            # propagate up.
            getUtility(IEmailValidator).validate(subscriber)
            if display_name is None:
                display_name, at, domain = subscriber.partition('@')
            # Because we want to keep the REST API simple, there is no
            # password or language given to us.  We'll use the system's
            # default language for the user's default language.  We'll set the
            # password to a system default.  This will have to get reset since
            # it can't be retrieved.  Note that none of these are used unless
            # the address is completely new to us.
            password = generate(int(config.passwords.password_length))
            return add_member(mlist, subscriber, display_name, password,
                              delivery_mode,
                              system_preferences.preferred_language, role)
        else:
            # We have to assume it's a UUID.
            assert isinstance(subscriber, UUID), 'Not a UUID'
            user = getUtility(IUserManager).get_user_by_id(subscriber)
            if user is None:
                raise MissingUserError(subscriber)
            return mlist.subscribe(user, role)

    def leave(self, list_id, email):
        """See `ISubscriptionService`."""
        mlist = getUtility(IListManager).get_by_list_id(list_id)
        if mlist is None:
            raise NoSuchListError(list_id)
        # XXX for now, no notification or user acknowledgment.
        delete_member(mlist, email, False, False)



def handle_ListDeletingEvent(event):
    """Delete a mailing list's members when the list is being deleted."""

    if not isinstance(event, ListDeletingEvent):
        return
    # Find all the members still associated with the mailing list.
    members = getUtility(ISubscriptionService).find_members(
        list_id=event.mailing_list.list_id)
    for member in members:
        member.unsubscribe()
