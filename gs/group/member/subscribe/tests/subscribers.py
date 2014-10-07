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
from gs.group.member.subscribe.subscribers import (
    OddSubscriber, SecretSubscriber, PrivateSubscriber,
    PublicToSiteMemberSubscriber, PublicSubscriber, CannotJoin, GroupMember)
import gs.group.member.subscribe.subscribers   # lint:ok
from .faux import FauxVisibility, FauxUserInfo, faux_email


class FailSubscriberTest(TestCase):
    '''Test the Subscribers that always prevent joining.'''
    def assertFailSubscribe(self, j, m=''):
        'Assert that trying to join with j raises a CannotJoin error with m'
        u = FauxUserInfo()
        with self.assertRaises(CannotJoin) as e:
            j.subscribe(u, 'person@example.com', None)
        if m:
            msg = str(e.exception)
            self.assertIn(m, msg)

    def test_odd_subscribe_fail(self):
        'Test that we always fail at joining an odd group'
        j = OddSubscriber(FauxVisibility())
        j.groupVisibility.isOdd = True
        self.assertFailSubscribe(j, 'cannot')

    def test_secret_subscribe_fail(self):
        'Test that we always fail at joining a secret group'
        j = SecretSubscriber(FauxVisibility())
        j.groupVisibility.isSecret = True
        self.assertFailSubscribe(j, 'invited')

    def test_private_join_fail(self):
        'Test that we always fail at joining a secret group'
        j = PrivateSubscriber(FauxVisibility())
        j.groupVisibility.isPrivate = True
        self.assertFailSubscribe(j, 'request')


class SuccessSubscriberTest(TestCase):
    '''Test the Subscribers that can succeed'''

    def test_ptsm_join_anon(self):
        'Ensure Anonymous cannot join a Public To Site Member site'
        j = PublicToSiteMemberSubscriber(FauxVisibility())
        j.groupVisibility.isPublicToSite = True
        with self.assertRaises(CannotJoin) as e:
            j.subscribe(None, faux_email(), None)
        self.assertIn('Only members', str(e.exception))

    @patch('gs.group.member.subscribe.subscribers.user_member_of_site')
    def test_ptsm_join_not_site_member(self, umos):
        'Ensure that people that are not site members are blocked'
        j = PublicToSiteMemberSubscriber(FauxVisibility())
        j.groupVisibility.isPublicToSite = True
        u = FauxUserInfo()
        umos.return_value = False
        with self.assertRaises(CannotJoin) as e:
            j.subscribe(u, faux_email(), None)
        self.assertIn('Only members', str(e.exception))

    @patch('gs.group.member.subscribe.subscribers.user_member_of_site')
    def test_ptsm_join_group_member(self, umos):
        'Ensure that group members cannot join a group'
        j = PublicToSiteMemberSubscriber(FauxVisibility())
        j.groupVisibility.isPublicToSite = True
        u = FauxUserInfo()
        umos.return_value = True
        n = 'gs.group.member.subscribe.subscribers.user_member_of_group'
        with patch(n) as umog:
            umog.return_value = True
            with self.assertRaises(GroupMember):
                j.subscribe(u, faux_email(), None)

    @patch('gs.group.member.subscribe.subscribers.user_member_of_site')
    def test_ptsm_join(self, umos):
        'Ensure that site members can join a group'
        u = FauxUserInfo()
        umos.return_value = True
        email = faux_email()
        with patch.object(PublicToSiteMemberSubscriber,
                          'send_confirmation') as sc:
            j = PublicToSiteMemberSubscriber(FauxVisibility())
            j.groupVisibility.isPublicToSite = True
            n = 'gs.group.member.subscribe.subscribers.user_member_of_group'
            with patch(n) as umog:
                umog.return_value = False
                j.subscribe(u, email, None)
        sc.assert_called_once_with(email, 'member@example.com', u, None)

    @patch('gs.group.member.subscribe.subscribers.user_member_of_group')
    def test_public_member(self, umog):
        umog.return_value = True
        u = FauxUserInfo()
        email = faux_email()
        j = PublicSubscriber(FauxVisibility())
        j.groupVisibility.isPublic = True
        with self.assertRaises(GroupMember):
            j.subscribe(u, email, None)

    @patch('gs.group.member.subscribe.subscribers.user_member_of_group')
    def test_public(self, umog):
        'Test a person with an existing profile joining a group'
        umog.return_value = False
        u = FauxUserInfo()
        email = faux_email()
        with patch.object(PublicSubscriber, 'send_confirmation') as sc:
            j = PublicSubscriber(FauxVisibility())
            j.groupVisibility.isPublic = True
            j.subscribe(u, email, None)
        sc.assert_called_once_with(email, 'member@example.com', u, None)

    @patch('gs.group.member.subscribe.subscribers.user_member_of_group')
    def test_public_new(self, umog):
        'Test a person without an existing profile joining a group'
        umog.return_value = False
        email = faux_email()
        u = FauxUserInfo()
        with patch.object(PublicSubscriber, 'send_confirmation') as sc:
            with patch.object(PublicSubscriber, 'create_user') as cu:
                cu.return_value = u
                j = PublicSubscriber(FauxVisibility())
                j.groupVisibility.isPublic = True
                j.subscribe(None, email, None)
        sc.assert_called_once_with(email, 'member@example.com', u, None)
        cu.assert_called_once_with('<member@example.com>')


class SendConfirmationTest(TestCase):

    def test_best_fn_no_name(self):
        'Test that we extract the name from the email address'
        j = PublicSubscriber(FauxVisibility())
        f = 'From: <member@example.com>'
        r = j.get_best_fn(f)
        self.assertEqual('member', r)

    def test_best_fn_name(self):
        'Test we extract the name from the From header'
        j = PublicSubscriber(FauxVisibility())
        f = 'From: A Person <member@example.com>'
        r = j.get_best_fn(f)
        self.assertEqual('A Person', r)

    def test_generate_confirmation_id(self):
        'Test the generation of the confirmation ID'
        j = PublicSubscriber(FauxVisibility())
        r1 = j.generate_confirmation_id('This is not an email')
        r2 = j.generate_confirmation_id('This is not a pipe')
        r3 = j.generate_confirmation_id(faux_email())

        self.assertEqual(6, len(r1))
        self.assertEqual(6, len(r2))
        self.assertEqual(6, len(r3))
        self.assertNotEqual(r1, r2)
        self.assertNotEqual(r1, r3)
        self.assertNotEqual(r2, r3)

    @patch.object(PublicSubscriber, 'generate_confirmation_id')
    def test_send_confirmation(self, gci):
        gci.return_value = 'a0b1c2'
        e = faux_email()
        u = FauxUserInfo()
        v = FauxVisibility()
        n = 'gs.group.member.subscribe.subscribers.ConfirmationNotifier'
        with patch(n) as cn:
            with patch.object(PublicSubscriber, 'query') as q:
                j = PublicSubscriber(v)
                j.send_confirmation(e, 'person@example.com', u, None)
        gci.assert_called_once_with(e)
        q.add_confirmation.assert_called_once_with(
            'person@example.com',  'a0b1c2', u.id, v.groupInfo.id,
            v.groupInfo.siteInfo.id)
        cn.assert_called_once_with('This is not a folder', None)
