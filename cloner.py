#!/usr/bin/env python

""" Clone all your repositories from github & bitbucket"""

import os
import re
import pickle
import sys

from getpass import getpass
from git import Repo, Git
from git.exc import GitCommandError

from bitbucket_ext import do_bb
from github_ext import do_gh

class SshRepo(object):
    """ Ssh repo object """
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def clone_repo(self, repo, directory):
        """ clone repository """

        string2 = ''
        match = re.match(r'.*\/(.*)\.git', repo)
        sub_dir = '/'+  match.group(1)
        string1 = "Cloning Repo {0}".format(match.group(1))
        sys.stdout.write(string1)
        sys.stdout.flush()
        git_ssh_identity_file = os.path.expanduser('~/.ssh/id_rsa')
        git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

        if os.path.exists(directory + sub_dir):
            string2 = ' - already exists'
            sys.stdout.write(string2)
            success = False
        else:
            try:
                with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                    Repo.clone_from(repo, directory + sub_dir, branch='master')
                    success = True
            except GitCommandError as exception:
                success = False
                string2 = " - error occurred"
                sys.stdout.write(string2)
                self.print_status(success, int(len(string1) + len(string2)))
                sys.stderr.write(str(exception) + '\n')
                return

        self.print_status(success, int(len(string1) + len(string2)))

    @classmethod
    def print_status(cls, success=False, location=False):
        """ print status of current operation at the end of each line"""

        bold = '\033[1m'
        green = '\033[92m'
        red = '\033[31m'
        bold = '\033[1m'
        green = '\033[92m'

        end = '\033[0m'

        # populate OK/FAILED string with color in bold
        status = green + "  OK  " if success else red + 'FAILED'
        status_block = (bold + '[ ' + status + end + bold
                        + ' ]' + end)
        _, columns = os.popen('stty size', 'r').read().split()
        spaces = ' ' * (int(columns) - len(status) - location)
        sys.stdout.write('{0}{1}\n'.format(spaces, status_block))

class GetAuth(dict):
    """get authentication from file or user input if file unavailable """

    def __init__(self, services=None, value=None):
        super(GetAuth, self).__init__()
        home = os.getenv('HOME')
        self.storage = home + '/.clonerrc'
        self.services = services
        if value is not None:
            self.iter_values(value)

    def iter_values(self, value):
        """ iterate through values """
        #print "Calling iter values"
        if value is None:
            pass
        elif isinstance(value, dict):
            #print "is instance dict"
            for key in value:
                #print "key ", key, value[key]
                self.__setitem__(key, value[key])
        else:
            raise TypeError, 'expected dict'

    def __setitem__(self, key, value):
        if '.' in key:
            my_key, rest_of_key = key.split('.', 1)
            target = self.setdefault(my_key, GetAuth())
            if not isinstance(target, GetAuth):
                raise KeyError, 'cannot set "%s" in "%s" (%s)' % (rest_of_key, my_key, repr(target))
            target[rest_of_key] = value
        else:
            if isinstance(value, dict) and not isinstance(value, GetAuth):
                #print "getting here"
                value = GetAuth(value=value)
                #print type(value), 'xxx'
                #print value.username, 'ppp'
                #print key, value
            dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        if '.' not in key:
            return dict.__getitem__(self, key)
        my_key, rest_of_key = key.split('.', 1)
        target = dict.__getitem__(self, my_key)
        if not isinstance(target, GetAuth):
            raise KeyError, 'cannot get "%s" in "%s" (%s)' % (rest_of_key, my_key, repr(target))
        return target[rest_of_key]

    def __contains__(self, key):
        if '.' not in key:
            return dict.__contains__(self, key)
        my_key, rest_of_key = key.split('.', 1)
        target = dict.__getitem__(self, my_key)
        if not isinstance(target, GetAuth):
            return False
        return rest_of_key in target

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default
        return self[key]

    #def save_auth(self):


    def get_auth(self):
        """ try to get auth from file """
        try:
            credentials = pickle.load(open(self.storage, "rb"))
        except (EOFError, IOError):
            credentials = None
        credentials = dict()
        if not credentials:
            for service in self.services:
                username, password = self.auth_input(service)
                credentials[service] = {}
                credentials[service]['username'] = username
                credentials[service]['password'] = password
            self.iter_values(credentials)

            return credentials

    @classmethod
    def auth_input(cls, service):
        """ get user input from console """
        username = raw_input('Enter your {0} username: '.format(service))
        password = getpass(prompt='Enter your {0} password: '.format(service))
        return username, password

    def __getattr__(self, item):
        #print "calling get attr"
        return self[item] if item in self else None

def main():
    """ main func """
    auth = GetAuth(services=['bitbucket', 'github'])
    auth.get_auth()
    print 'poouser', auth.bitbucket.username
    print 'poopass', auth.bitbucket.password
    ssh = SshRepo(auth.bitbucket.username, auth.bitbucket.password)

    path = '/tmp/poo'
    for repo in do_gh(auth.github.username, auth.github.password):
        ssh.clone_repo(repo.ssh_url, path)
    print "gg"
    for repo in do_bb(auth.bitbucket.username, auth.bitbucket.password):
        ssh.clone_repo(repo, path)
if __name__ == '__main__':
    main()
