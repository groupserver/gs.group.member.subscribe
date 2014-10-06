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
from email.utils import parseaddr
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from gs.group.list.command import CommandResult, CommandABC
from gs.group.privacy.visibility import GroupVisibility
from .audit import (SubscribeAuditor, SUBSCRIBE, CANNOT_JOIN, GROUP_MEMBER)
from .interfaces import ISubscriber
from .notify import NotifyCannotSubscribe
from .subscribers import CannotJoin, GroupMember


class SubscribeCommand(CommandABC):
    'The ``subscribe`` command.'

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.group)
        return retval

    def get_userInfo(self, addr):
        'Get the userInfo from the ``From`` in the email message'
        retval = None
        sr = self.group.site_root()
        u = sr.acl_users.get_userByEmail(addr)
        if u:
            retval = createObject('groupserver.UserFromId', self.group,
                                  u.getId())
        return retval

    def process(self, email, request):
        'Process the email command ``subscribe``'
        addr = parseaddr(email['From'])[1]
        userInfo = self.get_userInfo(addr)
        groupVisibility = GroupVisibility(self.groupInfo)
        subscriber = ISubscriber(groupVisibility)
        auditor = SubscribeAuditor(self.context, userInfo, self.groupInfo)
        auditor.info(SUBSCRIBE, addr)
        try:
            subscriber.subscribe(userInfo, email, request)
            retval = CommandResult.commandStop
        except CannotJoin as cj:
            auditor.info(CANNOT_JOIN, addr, cj.message)
            groupsFolder = self.groupInfo.groupObj.aq_parent
            notifier = NotifyCannotSubscribe(groupsFolder, request)
            notifier.notify(cj, addr, self.groupInfo)
            retval = CommandResult.commandStop
        except GroupMember:
            assert userInfo, 'None is a group member.'
            auditor.info(GROUP_MEMBER, addr)
            retval = CommandResult.notACommand
        return retval
