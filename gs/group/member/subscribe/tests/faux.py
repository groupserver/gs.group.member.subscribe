from email.parser import Parser
from gs.group.list.command.tests.faux import FauxGroup  # lint:ok


class FauxSiteInfo(object):
    name = 'An Example Site'
    id = 'example'


class FauxGroupInfo(object):
    name = 'An Example Group'
    id = 'example_group'
    url = 'https://lists.example.com/groups/example_group'
    siteInfo = FauxSiteInfo()
    groupObj = 'This is not a folder'


class FauxUserInfo(object):
    name = 'An Example user'
    id = 'exampleuser'


class FauxVisibility(object):
    groupInfo = FauxGroupInfo()


def faux_email(subject='join'):
    retval = Parser().parsestr(
        'From: <member@example.com>\n'
        'To: <group@example.com>\n'
        'Subject: {0}\n'
        '\n'
        'Body would go here\n'.format(subject))
    return retval


class FauxConfirmation(object):

    def __init__(self, context=None, email='a.person@example.com',
                 confirmationId='a0b1c2', userId='durk',
                 groupId='example_group', siteId='example'):
        self.context = context
        self.email = email
        self.confirmationId = confirmationId
        self.userId = userId
        self.groupId = groupId
        self.siteId = siteId

        self.site = 'This is not a site'
        self.siteInfo = FauxSiteInfo()
        self.siteInfo.id = siteId

        self.userInfo = FauxUserInfo()
        self.userInfo.id = userId

        self.groupInfo = FauxGroupInfo()
        self.groupInfo.id = groupId
