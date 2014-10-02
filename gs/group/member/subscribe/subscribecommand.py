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
from logging import getLogger
log = getLogger('gs.group.member.subscribe.listcommand')
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from gs.group.list.command import CommandResult, CommandABC
from gs.group.privacy.visibility import GroupVisibility
#from .audit import (SubscribeAuditor, CONFIRM)
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
        try:
            subscriber.subscribe(userInfo, email, request)
            retval = CommandResult.commandStop
        except CannotJoin as cj:
            groupsFolder = self.groupInfo.groupObj.aq_parent
            notifier = NotifyCannotSubscribe(groupsFolder, request)
            notifier.notify(cj, addr, self.groupInfo)
            retval = CommandResult.commandStop
        except GroupMember:
            m = 'Ignorning the "subscribe" command from {user.name} '\
                '({user.id}) <{addr}> because the person is already a '\
                'member of {group.name} ({group.id}) on {site.name} '\
                '({site.id}).'
            msg = m.format(user=userInfo, addr=addr, group=self.groupInfo,
                           site=self.groupInfo.siteInfo)
            log.info(msg)
            retval = CommandResult.notACommand
        return retval
