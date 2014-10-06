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
from datetime import datetime
SUBSYSTEM = 'gs.group.member.subscribe'
from logging import getLogger
log = getLogger(SUBSYSTEM)
from pytz import UTC
from zope.cachedescriptors.property import Lazy
from zope.component.interfaces import IFactory
from zope.interface import implementer, implementedBy
from gs.core import to_id
from Products.XWFCore.XWFUtils import munge_date
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, AuditQuery


UNKNOWN = '0'  # Unknown is always "0"
SUBSCRIBE = '1'
CONFIRM = '2'
CANNOT_JOIN = '3'
GROUP_MEMBER = '4'


@implementer(IFactory)
class SubscribeAuditEventFactory(object):
    """A Factory for Subscribe events."""
    title = 'GroupServer Joining Audit Event Factory'
    description = 'Creates a GroupServer event auditor for subscribe events'

    def __call__(self, context, event_id, code, date, userInfo,
                 instanceUserInfo, siteInfo, groupInfo, instanceDatum='',
                 supplementaryDatum='', subsystem=''):
        """Create an event"""
        if subsystem != SUBSYSTEM:
            raise ValueError('Subsystems do not match')

        if code == SUBSCRIBE:
            event = SubscribeEvent(
                context, event_id, date, userInfo, siteInfo,
                groupInfo, instanceDatum)
        elif code == CANNOT_JOIN:
            event = CannotJoinEvent(
                context, event_id, date, userInfo, siteInfo,
                groupInfo, instanceDatum, supplementaryDatum)
        elif code == GROUP_MEMBER:
            event = GroupMemberEvent(
                context, event_id, date, userInfo, siteInfo,
                groupInfo, instanceDatum)
        elif code == CONFIRM:
            event = ConfirmEvent(
                context, event_id, date, userInfo, siteInfo,
                groupInfo, instanceDatum)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date,
                                    userInfo, instanceUserInfo, siteInfo,
                                    groupInfo, instanceDatum,
                                    supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


@implementer(IAuditEvent)
class SubscribeEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person sending in an email
    requesting to subscribe to a group.'''
    def __init__(self, context, eventId, d, userInfo, siteInfo,
                 groupInfo, email):
        super(SubscribeEvent, self).__init__(
            context, eventId,  CONFIRM, d, userInfo, userInfo,
            siteInfo, groupInfo, email, None, SUBSYSTEM)

    def __unicode__(self):
        if self.userInfo:
            r = 'An email from {user.name} ({user.id}) <{email}> arrived '\
                'asking to subscribe to {group.name} ({group.id}) on '\
                '{site.name} ({site.id}).'
        else:
            r = 'An email from <{email}> arrived asking to subscribe to '\
                '{group.name} ({group.id}) on {site.name} ({site.id}).'

        retval = r.format(user=self.userInfo, group=self.groupInfo,
                          site=self.siteInfo, email=self.instanceDatum)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-join-%s' %\
            self.code
        retval = '<span class="%s">Sent in a request to join'\
                 '%s</span>' % (cssClass, self.groupInfo.name)
        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


@implementer(IAuditEvent)
class CannotJoinEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person being refused permission
to join a group.'''
    def __init__(self, context, eventId, d, userInfo, siteInfo,
                 groupInfo, email):
        super(CannotJoinEvent, self).__init__(
            context, eventId,  CONFIRM, d, userInfo, userInfo,
            siteInfo, groupInfo, email, None, SUBSYSTEM)

    def __unicode__(self):
        if self.userInfo:
            r = 'Refusing to allow {user.name} ({user.id}) <{email}> to'\
                'subscribe to {group.name} ({group.id}) on {site.name} '\
                '({site.id}): {reason}'
        else:
            r = 'Refusing to allow the person with the address <{email}>'\
                'to subscribe to {group.name} ({group.id}) on {site.name} '\
                '({site.id}: {reason}'

        retval = r.format(user=self.userInfo, group=self.groupInfo,
                          site=self.siteInfo, email=self.instanceDatum,
                          reason=self.supplementaryDatum)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-join-%s' %\
            self.code
        retval = '<span class="%s">Sent in a request to join'\
                 '%s</span>' % (cssClass, self.groupInfo.name)
        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


@implementer(IAuditEvent)
class GroupMemberEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person being refused permission
to join a group because he or she is a group member.'''
    def __init__(self, context, eventId, d, userInfo, siteInfo,
                 groupInfo, email):
        super(GroupMemberEvent, self).__init__(
            context, eventId,  CONFIRM, d, userInfo, userInfo,
            siteInfo, groupInfo, email, None, SUBSYSTEM)

    def __unicode__(self):
        r = 'Ignoring the request {user.name} ({user.id}) <{email}> to'\
            'subscribe to {group.name} ({group.id}) on {site.name} '\
            '({site.id}) because he or she is already a group member.'
        retval = r.format(user=self.userInfo, group=self.groupInfo,
                          site=self.siteInfo, email=self.instanceDatum)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-join-%s' %\
                   self.code
        retval = '<span class="%s">Already a member of %s </span>' %\
                 (cssClass, self.groupInfo.name)
        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


@implementer(IAuditEvent)
class ConfirmEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person sending in an email
    cornfirming the request to join a group.'''
    def __init__(self, context, eventId, d, instanceUserInfo, siteInfo,
                 groupInfo, email):
        super(ConfirmEvent, self).__init__(
            context, eventId,  CONFIRM, d, None, instanceUserInfo,
            siteInfo, groupInfo, email, None, SUBSYSTEM)

    def __unicode__(self):
        r = '{user.name} ({user.id}) sent an email confirming that he or '\
            'she wants to join {group.name} ({group.id}) on {site.name} '\
            '({site.id}) using the email address <{email}>.'
        retval = r.format(user=self.instanceUserInfo, group=self.groupInfo,
                          site=self.siteInfo, email=self.instanceDatum)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-join-%s' %\
            self.code
        retval = '<span class="%s">Confirmed the request to join '\
            '%s</span>' % (cssClass, self.groupInfo.name)

        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


class SubscribeAuditor(object):
    """An auditor for subscribing a group."""
    def __init__(self, context, userInfo, groupInfo):
        """Create a status auditor."""
        self.context = context
        self.userInfo = userInfo  # May be None
        self.groupInfo = groupInfo

    @Lazy
    def siteInfo(self):
        retval = self.groupInfo.siteInfo
        return retval

    @Lazy
    def factory(self):
        retval = SubscribeAuditEventFactory()
        return retval

    @Lazy
    def queries(self):
        retval = AuditQuery()
        return retval

    def info(self, code, instanceDatum='', supplementaryDatum=''):
        """Log an info event to the audit trail.
            * Creates an ID for the new event,
            * Writes the instantiated event to the audit-table, and
            * Writes the event to the standard Python log."""
        d = datetime.now(UTC)
        if self.userInfo:
            ed = '{0}-{1}-{2}-{4}-{5}-{6}-{7}-{8}'
            eventId = to_id(ed.format(
                self.groupInfo.name, self.groupInfo.id, d,
                self.siteInfo.name, self.siteInfo.id, instanceDatum,
                self.userInfo.name, self.userInfo.id, supplementaryDatum))
        else:
            ed = '{0}-{1}-{2}-{4}-{5}-{6}'
            eventId = to_id(ed.format(
                self.groupInfo.name, self.groupInfo.id, d,
                self.sitenfo.name, self.siteInfo.id, instanceDatum,
                supplementaryDatum))

        e = self.factory(
            self.context, eventId, code, d, self.userInfo, self.userInfo,
            self.siteInfo, self.groupInfo, instanceDatum,
            supplementaryDatum, SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
        return e
