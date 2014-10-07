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
from mock import patch, DEFAULT
from unittest import TestCase
from gs.group.member.subscribe.confirmcommand import (ConfirmCommand)
import gs.group.member.subscribe.confirmcommand  # lint:ok
import gs.group.member.subscribe.subscribecommand  # lint:ok
from gs.group.list.command.result import CommandResult
from .faux import (FauxGroup, faux_email, FauxConfirmation)


class TestConfirmCommand(TestCase):
    confirmSubject = 'Confirm some text ID-1a2b3c'
    confirmNoIdSubject = 'Confirm subject without an identifier'

    def setUp(self):
        self.fauxGroup = FauxGroup()

    def test_get_confirmation_id_true(self):
        'Can the confirmation ID be extracted from the subject?'
        c = ConfirmCommand(self.fauxGroup)
        e = faux_email(self.confirmSubject)
        r = c.get_confirmation_id(e)

        self.assertEqual('1a2b3c', r)

    def test_get_confirmation_id_false(self):
        'Is None returned when ther e is no ID in the subject?'
        c = ConfirmCommand(self.fauxGroup)
        e = faux_email(self.confirmNoIdSubject)
        r = c.get_confirmation_id(e)

        self.assertIs(None, r)

    def test_not_id(self):
        'Is an email without an ID seen as not a command?'
        c = ConfirmCommand(self.fauxGroup)
        e = faux_email(self.confirmNoIdSubject)
        r = c.process(e, None)
        self.assertEqual(CommandResult.notACommand, r)

    @patch.object(ConfirmCommand, 'query')
    def test_no_info_found(self, mockQuery):
        'Is a stop called if there is no confirmation info found?'
        mockQuery.get_confirmation.return_value = None
        e = faux_email(self.confirmSubject)
        with patch('gs.group.member.subscribe.confirmcommand.'
                   'NotifyCannotConfirm'):
            c = ConfirmCommand(self.fauxGroup)
            r = c.process(e, None)

        self.assertEqual(CommandResult.commandStop, r)

    @staticmethod
    def faux_query(email):
        retval = {
            'email': email,
            'confirmationId': '1a2b3c',
            'userId': 'durk',
            'groupId': 'example_group',
            'siteId': 'example',
            'responseDate': '', }
        return retval

    # --=mpj17=-- I am rarely this fiddly when it comes to tests, but
    # I was tracking down an error.

    def test_no_confirmation_data(self):
        'Test that we cannot confirm when we have no data'
        c = ConfirmCommand(self.fauxGroup)
        r = c.can_confirm('a.person@example.com', None)
        self.assertFalse(r)

    def test_no_confirmation_respose(self):
        'Test that we cannot confirm when we already processed the response'
        c = ConfirmCommand(self.fauxGroup)
        fc = FauxConfirmation()
        fc.hasResponse = True
        r = c.can_confirm('a.person@example.com', fc)
        self.assertFalse(r)

    def test_no_confirmation_addr_missmatch(self):
        'Ensure that we do not confirm with an email address missmatch'
        c = ConfirmCommand(self.fauxGroup)
        fc = FauxConfirmation()
        r = c.can_confirm('missmatch', fc)
        self.assertFalse(r)

    @patch('gs.group.member.subscribe.confirmcommand.user_member_of_group')
    def test_no_confirmation_member(self, umog):
        'Ensure that group members cannot confirm'
        umog.return_value = True
        c = ConfirmCommand(self.fauxGroup)
        fc = FauxConfirmation()
        r = c.can_confirm('a.person@example.com', fc)
        self.assertFalse(r)

    @patch('gs.group.member.subscribe.confirmcommand.user_member_of_group')
    def test_confirmation_ok(self, umog):
        'Test that we can confirm when we should'
        umog.return_value = True
        c = ConfirmCommand(self.fauxGroup)
        fc = FauxConfirmation()
        r = c.can_confirm('a.person@example.com', fc)
        self.assertFalse(r)

    # End of tests of ConfirmCommand.can_confirm

    @patch.object(gs.group.member.subscribe.confirmcommand.log, 'info')
    @patch.multiple(ConfirmCommand, query=DEFAULT, can_confirm=DEFAULT)
    def test_cannot_confirm(self, info, query, can_confirm):
        'Is a stop called if we cannot confirm?'
        queryReturn = self.faux_query('missmatch')
        query.get_confirmation.return_value = queryReturn
        can_confirm.return_value = False
        with patch('gs.group.member.subscribe.confirmcommand.'
                   'Confirmation') as pc:
            pc.return_value = FauxConfirmation()
            with patch('gs.group.member.subscribe.confirmcommand.'
                       'NotifyCannotConfirm') as ncc:
                notifyInstance = ncc.return_value
                c = ConfirmCommand(self.fauxGroup)
                e = faux_email(self.confirmSubject)
                r = c.process(e, None)
        self.assertEqual(CommandResult.commandStop, r)
        args, varArgs = info.call_args
        self.assertIn('Issues', args[0])
        ncc.assert_called_once_with(self.fauxGroup, None)
        notifyInstance .notify.assert_called_once_with(
            'member@example.com', queryReturn['confirmationId'])

    @patch('gs.group.member.subscribe.confirmcommand.SubscribeAuditor')
    @patch.multiple(ConfirmCommand, query=DEFAULT, can_confirm=DEFAULT,
                    join=DEFAULT)
    def test_confirm(self, info, query, can_confirm, join):
        'Can we confirm?'
        query.get_confirmation.return_value = self.faux_query('missmatch')
        e = faux_email(self.confirmSubject)
        n = 'gs.group.member.subscribe.confirmcommand.Confirmation'
        with patch(n) as pc:
            fc = FauxConfirmation()
            pc.return_value = fc
            can_confirm.return_value = True
            c = ConfirmCommand(self.fauxGroup)
            r = c.process(e, None)
        self.assertEqual(CommandResult.commandStop, r)
        join.assert_called_once_with(fc, None)
