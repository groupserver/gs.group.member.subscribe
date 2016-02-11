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
from mock import (MagicMock, patch, PropertyMock)
from unittest import TestCase
from gs.group.member.subscribe.messagesender import GroupMessageSender


class TestGroupMessageSender(TestCase):

    @patch.object(GroupMessageSender, 'mailingListInfo', new_callable=PropertyMock)
    def test_from_address_none(self, m_mLI):
        'Test that we get the default From address'
        e = 'group@example.com'
        m_mLI().get_property.return_value = e
        ms = GroupMessageSender(MagicMock(), MagicMock())
        r = ms.from_address(None)

        self.assertEqual(e, r)

    def test_from_address(self):
        e = 'other@example.com'
        ms = GroupMessageSender(MagicMock(), MagicMock())
        r = ms.from_address(e)

        self.assertEqual(e, r)

    @patch.object(GroupMessageSender, 'groupInfo', new_callable=PropertyMock)
    @patch.object(GroupMessageSender, 'mailingListInfo', new_callable=PropertyMock)
    def test_from_header_from_address_none(self, m_mLI, m_gI):
        m_gI().name = 'Example group'
        m_mLI().get_property.return_value = 'group@example.com'
        ms = GroupMessageSender(MagicMock(), MagicMock())
        r = ms.from_header_from_address()

        self.assertEqual('Example group <group@example.com>', r)

    @patch('gs.group.member.subscribe.messagesender.MessageSender.from_header_from_address')
    def test_from_header_from_address(self, m_super_fhfa):
        e = 'Other address <other@example.com>'
        m_super_fhfa.return_value = e
        ms = GroupMessageSender(MagicMock(), MagicMock())
        r = ms.from_header_from_address('other@example.com')

        self.assertEqual(e, r)
