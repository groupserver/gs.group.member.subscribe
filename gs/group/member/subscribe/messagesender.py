# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2016 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, unicode_literals, print_function
from zope.cachedescriptors.property import Lazy
from gs.profile.notify import MessageSender
from Products.GSGroup.interfaces import IGSMailingListInfo, IGSGroupInfo


class GroupMessageSender(MessageSender):
    # --=mpj17=-- While you would think that this class would be generic,
    # it turns out that the Confirm subscription notification is the only
    # one that is ever sent from the group.
    def __init__(self, context, toUserInfo):
        super(GroupMessageSender, self).__init__(context, toUserInfo)

    @Lazy
    def groupInfo(self):
        retval = IGSGroupInfo(self.context)
        return retval

    @Lazy
    def mailingListInfo(self):
        retval = IGSMailingListInfo(self.groupInfo.groupObj)
        return retval

    def from_address(self, address=None):
        '''Ensure we have a :mailheader:`From` address

:param str address: The address.
:returns: The ``address`` if it is ``True``, or the **group** email address
          otherwise.
:rtype: str'''
        if not address:
            retval = self.mailingListInfo.get_property('mailto')
        else:
            retval = super(GroupMessageSender, self).from_address(address)
        return retval

    def from_header_from_address(self, address=None):
        '''Ensure we have a pretty address for the :mailheader:`From` header

:param str address: The address.
:returns: An email header, with the display-name and email address.
:rtype: str
:raises ValueError: if a user cannot be found for the ``address``

If the ``address`` is supplied then it is assumed to be the address of a
**user**, and the display name will be set to the name of the user. Otherwise
the name and address of the group will be returned.'''
        if address:
            retval = super(GroupMessageSender, self).from_header_from_address(address)
        else:
            name = self.groupInfo.name
            email = self.mailingListInfo.get_property('mailto')
            retval = self.get_addr_line(name, email)
        return retval
