=============================
``gs.group.member.subscribe``
=============================

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2013-10-07
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.


Introduction
============

This part of the code contains the code that allows people to
subscribe to a group using email. It is *analogous* to the
web-based sign-up system [#signup]_ and related to the join
system [#join]_. Signing up using email is done in two phases:
the `subscribe email-command`_ initially screens the messages
coming in, while the `confirm email-command`_ ensures that people
know what they are getting in for. Three notifications_ are sent
out for various reasons.

Subscribe email-command
========================

The logic behind the *Subscribe* email command [#command]_ is
difficult because it can be sent to a group of any privacy.

* If an existing group member sends a *Subscribe* email to a
  group then it is treated as an ordinary email.

* If a person with a profile, who is not a group member, sends a
  *Subscribe* email to a public group then a *Confirm*
  notification is sent.

* If a person without a profile sends a *Subscribe* email to a
  public group then

  + A profile is created, and
  + A *Confirm* notification is sent.

  The name (``fn``) of the profile is the display-name in the
  ``From`` address, or the local-part of the address (the
  left-hand side of the ``@``) if the display-name is not
  present.

* If a person with a profile, who is not a group member but is a
  site member, sends a *Subscribe* email to a **public to
  site-members** group then a *Confirm* notification is sent.

* In all other cases a *Cannot join* notification is sent.

Confirm email-command
=====================

The *Confirm* notification is, if anything, uglier than the
*Subscribe* command. The email is designed to be sent **back**,
in order to confirm that the sender wants to join the group. So
the subject of the command will start with ``Re: Confirm``; it is
for the *Confirm* command that the ``Re:`` is stripped from the
start of all the emails.

Each confirmation has a unique six-digit (base 62) identifier. It
is shown the end of the subject line for the *Confirm*
command. If stripped the subscription request cannot be
confirmed. When checked not only is the confirmation-ID looked
up, the email-address is also checked. I am unsure what issues
could arise if we let people confirm for others, but it smells
dodgy.

If everything checks out correctly then the member is joined to
the group, using the normal join mechanism [#join]_. Otherwise a
"Contact us" email is sent. Much can go wrong, and rather than
write (around six) separate notifications one message is sent
that asks the person to contact Support.

Notifications
=============

* Confirm: ``gs-group-member-subscribe-confirm.html``
* Cannot subscribe: ``gs-group-member-subscribe-refuse.html``
* Confirmation problems: ``gs-group-member-subscribe-confirm-problems.html``

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
           <https://github.com/groupserver/gs.group.member.join/>

.. [#command] See the ``gs.group.list.command`` product
              <https://github.com/groupserver/gs.group.list.command/>

..  LocalWords:  NotifyNewMember loggedInUser txt msg html groupInfo
..  LocalWords:  joiningUser IGSJoiningUser NotifyAdmin
