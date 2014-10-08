# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
#
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
from setuptools import setup, find_packages
import codecs
import os
from version import get_version

with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()
with codecs.open(os.path.join("docs", "HISTORY.rst"),
                 encoding='utf-8') as f:
    long_description += '\n' + f.read()

version = get_version()

setup(
    name='gs.group.member.subscribe',
    version=version,
    description="Support for the subscribe email-command",
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        "Intended Audience :: Developers",
        'License :: OSI Approved :: Zope Public License',
        "Natural Language :: English",
        "Natural Language :: French",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='user, group, member, group member, subscribe, email',
    author='Michael JasonSmith',
    author_email='mpj17@onlinegroups.net',
    url='https://github.com/groupserver/gs.group.member.subscribe/',
    license='ZPL 2.1',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['gs', 'gs.group', 'gs.group.member'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pytz',
        'SQLAlchemy',
        'zope.browserpage',
        'zope.cachedescriptors',
        'zope.component',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.tal',
        'zope.tales',
        'gs.content.email.base',
        'gs.content.email.layout',
        'gs.core',
        'gs.database',
        'gs.email',
        'gs.group.list.command',
        'gs.group.member.base',
        'gs.group.privacy',
        'gs.profile.email.base',
        'gs.profile.email.verify',
        'gs.profile.notify',
        'Products.GSAuditTrail',
        'Products.GSProfile',
        'Products.XWFCore',
    ],
    test_suite="gs.group.member.subscribe.tests.test_all",
    tests_require=['mock', ],
    entry_points="""# -*- Entry points: -*-
    """,
)
