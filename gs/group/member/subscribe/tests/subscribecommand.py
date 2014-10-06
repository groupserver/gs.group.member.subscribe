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
from mock import patch
from unittest import TestCase
from gs.group.member.subscribe.subscribecommand import (SubscribeCommand)
import gs.group.member.subscribe.subscribecommand  # lint:ok
from gs.group.list.command.result import CommandResult
from .faux import (FauxGroup, FauxGroupInfo, FauxUserInfo, faux_email)


class TestSubscribeCommand(TestCase):

    @patch.object(SubscribeCommand, 'groupInfo')
    @patch.object(SubscribeCommand, 'get_userInfo')
    @patch.object(
        gs.group.member.subscribe.subscribecommand.SubscribeAuditor,
        'info')
    def test_member(self, gi, g_ui, a):
        'Test a member sending a "Subscribe" command'
        gi.return_value = FauxGroupInfo()

        u = FauxUserInfo()
        g_ui.return_value = u

        with patch('gs.group.member.subscribe.subscribecommand.'
                   'ISubscriber') as sub:
            sInstance = sub.return_value
            sInstance.subscribe.side_effect =\
                gs.group.member.subscribe.subscribecommand.GroupMember

            sc = SubscribeCommand(FauxGroup)
            e = faux_email()
            r = sc.process(e, None)

        sInstance.subscribe.assert_called_once_with(u, e, None)
        self.assertEqual(CommandResult.notACommand, r)

    @patch.object(SubscribeCommand, 'groupInfo')
    @patch.object(SubscribeCommand, 'get_userInfo')
    @patch.object(
        gs.group.member.subscribe.subscribecommand.SubscribeAuditor,
        'info')
    def test_cannot(self, gi, g_ui, audit):
        '''Test sending a "Subscribe" command to a group that cannot be
        joined'''
        gi.return_value = FauxGroupInfo()
        g_ui.return_value = None

        with patch('gs.group.member.subscribe.subscribecommand.'
                   'ISubscriber') as sub:
            sInstance = sub.return_value
            sInstance.subscribe.side_effect =\
                gs.group.member.subscribe.subscribecommand.CannotJoin

            with patch('gs.group.member.subscribe.subscribecommand.'
                       'NotifyCannotSubscribe') as notify:
                sc = SubscribeCommand(FauxGroup)
                e = faux_email()
                r = sc.process(e, None)

        sInstance.subscribe.assert_called_once_with(None, e, None)
        self.assertEqual(1, notify.call_count, 'Not notified')
        self.assertEqual(CommandResult.commandStop, r)

    @patch.object(SubscribeCommand, 'groupInfo')
    @patch.object(SubscribeCommand, 'get_userInfo')
    @patch.object(
        gs.group.member.subscribe.subscribecommand.SubscribeAuditor,
        'info')
    def test_subscribe(self, gi, g_ui, a):
        'Test sending a "Subscribe" command'
        gi.return_value = FauxGroupInfo()

        u = FauxUserInfo()
        g_ui.return_value = u

        with patch('gs.group.member.subscribe.subscribecommand.'
                   'ISubscriber'):
            sc = SubscribeCommand(FauxGroup)
            e = faux_email()
            r = sc.process(e, None)
        self.assertEqual(CommandResult.commandStop, r)
