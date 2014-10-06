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
import shlex
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from gs.group.list.command import CommandResult, CommandABC
from gs.group.member.base import user_member_of_group
from gs.group.member.join.utils import join
from gs.profile.email.base import EmailUser
from gs.profile.email.verify import EmailVerificationUser
from .audit import (SubscribeAuditor, CONFIRM)
from .subscribers import GroupMember
from .notify import (NotifyAlreadyAMember, NotifyCannotConfirmAddress,
                     NotifyCannotConfirmId)
from .queries import ConfirmationQuery


class ConfirmCommand(CommandABC):
    'The ``confirm subscription`` command.'

    @Lazy
    def query(self):
        retval = ConfirmationQuery()
        return retval

    @staticmethod
    def get_confirmation_id(email):
        '''Get the confirmation ID from the subject line of the email

:param email.message.Message email: The email to process.
:returns: The confirmation-identifier from the ``Subject`` if present,
          ``None`` otherwise.
:rtype: str'''
        # Use shlex.split rather than self.get_command_components because
        # it is important that we are case-preserving.
        idComponents = [idc for idc in shlex.split(email['Subject'])
                        if idc[:3] == 'ID-']
        retval = idComponents[0].split('-')[1] if idComponents else None
        return retval

    def process(self, email, request):
        'Process the subscription confirmation'
        addr = parseaddr(email['From'])[1]
        confirmationId = self.get_confirmation_id(email)
        if confirmationId:
            ci = self.query.get_confirmation(addr, confirmationId)
            if ci:
                confirmationInfo = Confirmation(self.context, **ci)
                if (confirmationInfo.email == addr):
                    try:
                        auditor = SubscribeAuditor(
                            self.context, confirmationInfo.userInfo,
                            confirmationInfo.groupInfo)
                        auditor.info(CONFIRM, addr)
                        # VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV
                        self.join(confirmationInfo, request)
                        # AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
                    except GroupMember:
                        notifier = NotifyAlreadyAMember(
                            confirmationInfo.site, request)
                        notifier.notify(confirmationInfo.userInfo,
                                        confirmationInfo.groupInfo)
                    retval = CommandResult.commandStop
                else:  # confirmationInfo.email != addr
                    m = 'Email address <{addr}> does not match that in '\
                        'the confirmation info <{confirmationAddr}>: '\
                        '{subject}'
                    msg = m.format(
                        addr=addr, confirmationAddr=confirmationInfo.email,
                        subject=email['Subject'])
                    log.info(msg)
                    notifier = NotifyCannotConfirmAddress(
                        confirmationInfo.site, request)
                    notifier.notify(confirmationInfo.userInfo,
                                    confirmationInfo.groupInfo,
                                    addr, confirmationInfo.email)
                    retval = CommandResult.commandStop
            else:  # confirmationId and (not ci)
                # Found an "ID-" in the confirmation-email, but no matching
                # confirmation ID in the database.
                m = 'No confirmation information found in command from '\
                    '<{addr}>: {subject}'
                msg = m.format(addr=addr, subject=email['Subject'])
                log.info(msg)
                notifier = NotifyCannotConfirmId(self.context, request)
                notifier.notify(addr, confirmationId)
                retval = CommandResult.commandStop
        else:  # not confirmationId
            # Assume it is a normal email.
            m = 'No confirmation ID found in command from <{addr}>: '\
                '{subject}'
            msg = m.format(addr=addr, subject=email['Subject'])
            log.info(msg)
            retval = CommandResult.notACommand
        return retval

    def get_groupInfo_siteInfo(self, confirmationInfo):
        'Get the groupInfo and siteInfo from the confirmationInfo'

    def verify_address(self, userInfo, addr):
        # TODO: Now the Add code and this code does this. Cut 'n' paste
        #       software engineereing for now, but the verification code
        #       should provide this as a utility.
        eu = EmailUser(self.context, userInfo)
        if not eu.is_address_verified(addr):
            evu = EmailVerificationUser(self.context, userInfo, addr)
            verificationId = evu.create_verification_id()
            evu.add_verification_id(verificationId)
            evu.verify_email(verificationId)

    def join(self, confirmationInfo, request):
        if user_member_of_group(confirmationInfo.userInfo,
                                confirmationInfo.groupInfo):
            raise GroupMember('Already a member of the group')

        auditor = SubscribeAuditor(
            confirmationInfo.site, confirmationInfo.groupInfo,
            confirmationInfo.userInfo)
        auditor.info(CONFIRM)

        self.verify_address(confirmationInfo.userInfo,
                            confirmationInfo.email)

        join(confirmationInfo.groupInfo.groupObj, request,
             confirmationInfo.userInfo, confirmationInfo.groupInfo)
        self.query.clear_confirmations(confirmationInfo.userInfo.id,
                                       confirmationInfo.groupInfo.id)


class Confirmation(object):

    def __init__(self, context, email, confirmationId, userId, groupId,
                 siteId):
        self.context = context
        self.email = email
        self.confirmationId = confirmationId
        self.userId = userId
        self.groupId = groupId
        self.siteId = siteId

        # Because the email comes into Support we may be on a totally
        # different site. Get the correct site as the context.
        siteRoot = self.context.site_root()
        self.site = getattr(siteRoot.Content, siteId)
        self.siteInfo = createObject('groupserver.SiteInfo', self.site)
        # Get the user and group with the right context.
        self.userInfo = createObject('groupserver.UserFromId', self.site,
                                     userId)
        self.groupInfo = createObject('groupserver.GroupInfo', self.site,
                                      groupId)
