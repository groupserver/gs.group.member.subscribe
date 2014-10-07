# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
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
from __future__ import unicode_literals
from zope.i18n import translate
from gs.content.email.base import (NotifierABC, GroupNotifierABC,
                                   AnonymousNotifierABC)
from gs.email import send_email
from gs.profile.email.base.emailuser import EmailUser
from gs.profile.notify import MessageSender
from . import GSMessageFactory as _
UTF8 = 'utf-8'


class ConfirmationNotifier(GroupNotifierABC):
    '''The email asking someone to confirm they want to be in a group.'''
    textTemplateName = 'gs-group-member-subscribe-confirm.txt'
    htmlTemplateName = 'gs-group-member-subscribe-confirm.html'

    def notify(self, userInfo, toAddr, confirmationId):
        subject = _('confirm-subject',
                    'Confirm you want to subscribe to ${groupName} (action '
                    'required) ID-${confirmationId}',
                    mapping={'groupName': self.groupInfo.name,
                             'confirmationId': confirmationId})
        translatedSubject = translate(subject)
        emailUser = EmailUser(userInfo.user, userInfo)
        text = self.textTemplate(userInfo=userInfo, userEmail=emailUser)
        html = self.htmlTemplate(userInfo=userInfo, userEmail=emailUser)
        ms = MessageSender(self.context, userInfo)
        # We have to explicitly state the address because it has not
        # (necessarially) been verified yet.
        ms.send_message(translatedSubject, text, html, toAddresses=[toAddr])
        self.reset_content_type()


class NotifyCannotSubscribe(AnonymousNotifierABC):
    'The email telling someone that they cannot be in the group'
    textTemplateName = 'gs-group-member-subscribe-refuse.txt'
    htmlTemplateName = 'gs-group-member-subscribe-refuse.html'

    def notify(self, message, addr, groupInfo):
        subject = _('refuse-subject',
                    'Cannot subscribe to ${groupName}',
                    mapping={'groupName': groupInfo.name})
        translatedSubject = translate(subject)
        text = self.textTemplate(groupInfo=groupInfo, reason=message)
        html = self.htmlTemplate(groupInfo=groupInfo, reason=message)

        fromAddr = self.fromAddr(groupInfo.siteInfo)
        message = self.create_message(addr, fromAddr, translatedSubject,
                                      text, html)
        send_email(groupInfo.siteInfo.get_support_email(), addr, message)
        self.reset_content_type()


class NotifyAlreadyAMember(NotifierABC):
    'The email telling the member that he or she has already confirmed'
    textTemplateName = 'gs-group-member-subscribe-member.txt'
    htmlTemplateName = 'gs-group-member-subscribe-member.html'

    def notify(self, userInfo, groupInfo):
        subject = _('already-subscribed-subject',
                    'Already subscribed ${groupName}',
                    mapping={'groupName': groupInfo.name})
        translatedSubject = translate(subject)
        text = self.textTemplate(userInfo=userInfo, groupInfo=groupInfo)
        html = self.htmlTemplate(userInfo=userInfo, groupInfo=groupInfo)

        ms = MessageSender(self.context, userInfo)
        ms.send_message(translatedSubject, text, html)
        self.reset_content_type()


class NotifyCannotConfirm(AnonymousNotifierABC):
    'The email telling someone that the Confirmation ID is garbled'
    textTemplateName = 'gs-group-member-subscribe-confirm-problems.txt'
    htmlTemplateName = 'gs-group-member-subscribe-confirm-problems.html'

    def notify(self, groupInfo, addr, confirmationId):
        subject = _('confirm-failed-id-subject',
                    'Problem confirming your subscription (action '
                    'required)')
        translatedSubject = translate(subject)
        text = self.textTemplate(address=addr,
                                 confirmationId=confirmationId)
        html = self.htmlTemplate(address=addr,
                                 confirmationId=confirmationId)

        fromAddr = self.fromAddr(groupInfo.siteInfo)
        message = self.create_message(addr, fromAddr, translatedSubject,
                                      text, html)
        send_email(groupInfo.siteInfo.get_support_email(), addr, message)
        self.reset_content_type()
