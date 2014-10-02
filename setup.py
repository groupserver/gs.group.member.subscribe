# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2010, 2011, 2012, 2013, 2014 OnlineGroups.net and
# Contributors.
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
    url='https://github/groupserver/gs.group.member.subscribe/',
    license='ZPL 2.1',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['gs', 'gs.group', 'gs.group.member'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pytz',
        'zope.browserpage',
        'zope.cachedescriptors',
        'zope.component',
        'zope.event',
        'zope.formlib',
        'zope.interface',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.tal',
        'zope.tales',
        'zope.viewlet',
        'Zope2',
        'gs.content.email.base',
        'gs.content.email.layout',
        'gs.content.form.base',
        'gs.content.layout',
        'gs.core',
        'gs.group.base',
        'gs.group.member.base',
        'gs.group.member.viewlet',
        'gs.profile.email.base',
        'gs.profile.notify',
        'Products.GSAuditTrail',
        'Products.GSGroup',
        'Products.GSProfile',
        'Products.XWFCore',
    ],
    extras_require={'docs': ['Sphinx', ], },
    test_suite="gs.group.member.join.tests.test_all",
    tests_require=['mock', ],
    entry_points="""# -*- Entry points: -*-
    """,
)