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
from __future__ import absolute_import, unicode_literals
from zope.cachedescriptors.property import Lazy
from zope.i18n import translate
from gs.content.email.base import GroupEmail, TextMixin
from . import GSMessageFactory as _


class ConfirmSubscription(GroupEmail):
    'Subscription confirm message'
    @Lazy
    def supportEmail(self):
        subject = _('support-message-confirm-subscription-subject',
                    'Confirm subscription')
        translatedSubject = translate(subject)
        body = _('support-message-confirm-subscription-body',
                 'Hello,\n\nI received an email asking me to confirm '
                 'my subscription to\n${groupName}\n    '
                 '${groupUrl}\nand...',
                 mapping={'groupName': self.groupInfo.name,
                          'groupUrl': self.groupInfo.url})
        translatedBody = translate(body)
        retval = self.mailto(self.siteInfo.get_support_email(),
                             translatedSubject, translatedBody)
        return retval


class ConfirmSubscriptionText(ConfirmSubscription, TextMixin):
    def __init__(self, context, request):
        super(ConfirmSubscriptionText, self).__init__(context, request)
        filename = 'confirm-%s.txt' % self.groupInfo.id
        self.set_header(filename)


class RefuseSubscription(GroupEmail):
    'Subscription refused message'
    @Lazy
    def supportEmail(self):
        subject = _('support-message-refuse-subscription-subject',
                    'Cannot subscribe')
        translatedSubject = translate(subject)
        body = _('support-message-confirm-subscription-body',
                 'Hello,\n\nI received an email saying that I could not '
                 'subscribe to\n${groupName}\n    '
                 '${groupUrl}\nand...',
                 mapping={'groupName': self.groupInfo.name,
                          'groupUrl': self.groupInfo.url})
        translatedBody = translate(body)
        retval = self.mailto(self.siteInfo.get_support_email(),
                             translatedSubject, translatedBody)
        return retval


class RefuseSubscriptionText(RefuseSubscription, TextMixin):
    def __init__(self, context, request):
        super(RefuseSubscriptionText, self).__init__(context, request)
        filename = 'refuse-%s.txt' % self.groupInfo.id
        self.set_header(filename)