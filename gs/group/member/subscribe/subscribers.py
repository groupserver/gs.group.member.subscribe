# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
from __future__ import absolute_import, unicode_literals
from abc import ABCMeta, abstractmethod
from email.utils import parseaddr
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from gs.core import to_id
from gs.group.member.base import user_member_of_site, user_member_of_group
from Products.GSProfile.utils import create_user_from_email
from . import GSMessageFactory as _
from .notify import ConfirmationNotifier
from .queries import ConfirmationQuery


class CannotJoin(Exception):
    '''Raised when a person cannot join the group'''


class GroupMember(Exception):
    '''Raised when a group member tries to join the group.'''


class Subscriber(object):
    __metaclass__ = ABCMeta

    def __init__(self, groupVisibility):
        self.groupInfo = groupVisibility.groupInfo

    @abstractmethod
    def subscribe(self, userInfo, email, request):
        '''Subscribe the person to the group.'''


class PublicSubscriber(Subscriber):
    @Lazy
    def query(self):
        retval = ConfirmationQuery()
        return retval

    def subscribe(self, userInfo, email, request):
        if userInfo and user_member_of_group(userInfo, self.groupInfo):
            raise GroupMember()
        ui = userInfo if userInfo else self.create_user(email['From'])
        addr = parseaddr(email['From'])[1]
        self.send_confirmation(email, addr, ui, request)

    def send_confirmation(self, email, addr, userInfo, request):
        # Generate the confirmation ID
        confirmationId = self.generate_confirmation_id(email)
        self.query.add_confirmation(
            addr, confirmationId, userInfo.id, self.groupInfo.id,
            self.groupInfo.siteInfo.id)
        # Send the notification
        notifier = ConfirmationNotifier(self.groupInfo.groupObj, request)
        notifier.notify(userInfo, addr, confirmationId)

    @staticmethod
    def get_best_fn(fromHeader):
        emailLHS, addr = parseaddr(fromHeader)
        retval = emailLHS if emailLHS else addr.split('@')[0]
        return retval

    def create_user(self, fromHeader):
        'Create a user from the From header, setting the ``fn``.'
        addr = parseaddr(fromHeader)[1]
        group = self.groupInfo.groupObj
        user = create_user_from_email(group, addr)
        fn = self.get_best_fn(fromHeader)
        user.manage_changeProperties(fn=fn)
        retval = createObject('groupserver.UserFromId',
                              group, user.id)
        assert retval, 'Could not create a user info '\
                       'from {0}'.format(fromHeader)
        return retval

    def generate_confirmation_id(self, email):
        id22 = to_id(str(email) + self.groupInfo.name + self.groupInfo.id)
        retval = id22[:6]
        return retval


class PublicToSiteMemberSubscriber(PublicSubscriber):
    @Lazy
    def query(self):
        retval = ConfirmationQuery()
        return retval

    def subscribe(self, userInfo, email, request):
        siteInfo = self.groupInfo.siteInfo
        if ((not userInfo) or (not user_member_of_site(userInfo,
                                                       siteInfo))):
            msg = _('public-site-group-cannot-join',
                    'Only members of ${siteName} can join ${groupName}',
                    mapping={'siteName': siteInfo.name,
                             'groupName': self.groupInfo.name})
            raise CannotJoin(msg)
        elif user_member_of_group(userInfo, self.groupInfo):
            raise GroupMember()
        addr = parseaddr(email['From'])[1]
        self.send_confirmation(email, addr, userInfo, request)


class PrivateSubscriber(Subscriber):
    def subscribe(self, userInfo, email, request):
        msg = _('private-group-cannot-join',
                'Visit the page for ${groupName} to request membership: '
                '${groupUrl}',
                mapping={'groupName': self.groupInfo.name,
                         'groupUrl': self.groupInfo.url})
        raise CannotJoin(msg)


class SecretSubscriber(Subscriber):
    def subscribe(self, userInfo, email, request):
        msg = _('secret-group-cannot-join',
                'Only people that have been invited can join ${groupName}',
                mapping={'groupName': self.groupInfo.name})
        raise CannotJoin(msg)


class OddSubscriber(Subscriber):
    def subscribe(self, userInfo, email, request):
        msg = _('odd-group-cannot-join', 'People cannot join ${groupName}',
                mapping={'groupName': self.groupInfo.name})
        raise CannotJoin(msg)
