=============================
``gs.group.member.subscribe``
=============================

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2013-10-01
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.


Introduction
============

This part of the code contains the code that allows people to
subscribe to a group using email. It is *analogous* to the
web-based Sign-up system [#signup]_ and related to the Join
system [#join]_

Subscribe email-command
========================

The logic behind the *Subscribe* email command is difficult
because it can be sent to a group of any privacy.

* If an existing group member sends a *Subscribe* email to a
  group then it is treated as an ordinary email.

* If a person with a profile, who is not a group member, sends a
  *Subscribe* email to a public group then a *Confirm*
  notification is sent.

* If a person without a profile sends a *Subscribe* email to a
  public group then

  + A profile is created, and
  + A *Confirm* notification is sent.

* If a person with a profile, who is not a group member but is a
  site member, sends a *Subscribe* email to a **public to
  site-members** group then a *Confirm* notification is sent.

* In all other cases a *Cannot join* notification is sent.

Confirm email-command
=====================

Notifications
=============

* Cannot subscribe
* Already a member
* Email address mismatch
* Confirmation ID not found

Resources
=========

- Code repository: https://github.com/groupserver/gs.group.member.subscribe
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
..  _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/

.. [#signup] See the ``gs.profile.signup.base`` product
             <https://github.com/groupserver/gs.profile.signup.base/>

.. [#join] See the ``gs.group.member.join`` product
           <https://github.com/groupserver/gs.group.member.invite.csv/>

..  LocalWords:  NotifyNewMember loggedInUser txt msg html groupInfo
..  LocalWords:  joiningUser IGSJoiningUser NotifyAdmin
