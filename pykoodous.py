#!/usr/bin/python
# -*- coding: utf-8 -*-
header = \
    """
--------------Koodous Script Manage--------------------
Url:\t\thttps://koodous.com
Twitter:\t@koodous_project
Author:\t\tframirez@koodous.com
\t\t2015
Get your TOKEN --> https://koodous.com/settings/profile

"""

import requests
import json
from os import listdir
from os.path import isfile, join

import urllib
import hashlib
import argparse


class wmup:

    TOKEN = '****YOUR TOKEN****'
    URL = 'https://koodous.com/api/%s/%s/%s'

    def __init__(self, token=None):
        if token is not None:
            self.TOKEN = token
        self.headers = {'Authorization': 'Token %s' % self.TOKEN}
        self.sha256 = ''

    def hash256(self, tfile):
        """
			Generate the hash from file
		"""

        f = open(tfile, 'rb')
        fr = f.read()
        hasher_256 = hashlib.sha256()
        hasher_256.update(fr)
        self.sha256 = hasher_256.hexdigest()
        return self.sha256

    def upload(self, ffile):
        """
			Function to upload files
		"""

        url = self.URL % ('apks', self.hash256(ffile), 'get_upload_url')
        r = requests.get(url=url, headers=self.headers)

        if r.status_code == 200:
            j = r.json()
            files = {'file': open(ffile, 'rb')}
            s = requests.post(url=j['upload_url'], files=files)
            return s.status_code
        else:

            return r.status_code

    def download(self, sha256, ffile=None):
        """
			Function to download files
		"""

        url = self.URL % ('apks', sha256, 'download')
        r = requests.get(url=url, headers=self.headers)

        if r.status_code is 200:
            j = r.json()
            testfile = urllib.URLopener()
            testfile.retrieve(j['download_url'], ffile)

        return r.status_code

    def is_apk(self, content):
        """
			Check if a filetype is APK
		"""

        zip = zipfile.ZipFile(StringIO.StringIO(content))
        for i in zip.namelist():
            if i == 'AndroidManifest.xml':
                return True

        return False

    def vote_apk(self, sha256, kind):
        """
			Vote apk positive || negative
		"""

        url = self.URL % ('apks', sha256, 'votes')
        return requests.post(url, data={'kind': kind},
                             headers=self.headers)

    def comment_apk(self, sha256, text):
        """
			Comment apks
		"""

        url = self.URL % ('apks', sha256, 'comments')
        return requests.post(url, data={'text': text},
                             headers=self.headers)

    def follow_user(self, username):
        """
			Follow user
		"""

        url = self.URL % ('analysts', username, 'follow')
        return requests.get(url, headers=self.headers)

    def write_tag(self, sha256, tag):
        """
			Write a tag in apk
		"""

        url = self.URL % ('apks', sha256, 'tags')
        return requests.post(url, headers=self.headers,
                             data={'name': tag})


if __name__ == '__main__':
                                #All is done - upload to VT
    status_response = {
    				200: "All is done",
    				201: "Created",
                    415: "It,s not a apk",
                	412: "Policy exception",
	      			408: "The url is lapsed",
	      			409: "Apk already exist in our database",
	      			401: "Invalid token",
	      			429: "Api limit reached"
	      			}
    print header
    parser = \
        argparse.ArgumentParser(description='Script for upload and download files to Koodous')

    parser.add_argument('action', action='store',
                        help='upload | download | checkApk | tag | vote | comment | follow')
    parser.add_argument('-s', '--sha256', dest='sha256',
                        help='hash for file', default=None)
    parser.add_argument('-p', '--path', dest='path',
                        help='specify the path', default='/tmp/')
    parser.add_argument('-f', '--file', dest='file', help='filename',
                        default=None)
    parser.add_argument('-k', '--kind', dest='kind_vote',
                        help='kind vote', default=None)
    parser.add_argument('-c', '--comment', dest='comment',
                        help='comment', default=None)
    parser.add_argument('-u', '--username', dest='username',
                        help='username', default=None)
    parser.add_argument('-t', '--tag', dest='tag', help='tag',
                        default=None)

    parser.add_argument('-T', '--token', dest='token', help='token',
                        default=None)
    args = parser.parse_args()
    results = parser.parse_args()

    a = wmup(results.token)

    if results.action == 'upload':
        if results.path is not '/tmp/' and results.file is None:
            onlyfiles = [f for f in listdir(results.path)
                         if isfile(join(results.path, f))]

            for row in onlyfiles:
                try:
                    print 'Uploading %s' % (results.path + row)
                    code = a.upload(results.path + row)
                    print status_response[code]
                    if code is 429:
                    	print "Sleeping %i seconds for api reached" % 60
                    	time.sleep(60)

                except Exception, error:
                    print 'Error upload %s' % error
        elif results.file is not None:

            print 'Uploading %s' % results.file
            code = a.upload(results.file)
            print status_response[code]

        else:
            print 'You need specify file to upload [-f] or path [-p]'
    elif results.action == 'download':

        if results.sha256 is not None:
            if results.file is None:
                results.file = results.path + results.sha256
            print 'Downloading %s in %s' % (results.sha256,
                    results.file)
            code = a.download(results.sha256, results.file)
            print status_response[code]

        else:

            print 'You need specify sha256 to download [-s]'
    elif results.action == 'checkApk':

        if results.file is not None:
            f = open(results.file, 'rb')
            content = f.read()

            if content[:2] == 'PK':
                if a.is_apk(content):
                    print "It's APK"
                else:
                    print "It's not APK"
    elif results.action == 'vote':

        if results.sha256 is not None and results.kind_vote \
            in ['positive', 'negative']:
            if a.vote_apk(results.sha256,
                          results.kind_vote).status_code in [200, 201]:
                print 'Vote apk %s sucesfully' % results.sha256
        else:
            print 'You need specify sha256 [-s] and vote [-k] (negative || positive) '
    elif results.action == 'comment':

        if results.sha256 is not None and results.comment:
            if a.comment_apk(results.sha256,
                             results.comment).status_code in [200, 201]:
                print 'Comment apk %s sucesfully' % results.sha256
        else:

            print 'You need specify sha256 [-s] and comment [-c]'
    elif results.action == 'follow':

        if results.username:
            if a.follow(results.username).status_code in [200, 201]:
                print 'You follow %s' % results.username
        else:
            print 'You need specify username [-u]'
    elif results.action == 'tag':

        if results.sha256 is not None and results.tag is not None:
            if a.write_tag(results.sha256, results.tag).status_code \
                in [200, 201]:
                print 'Tag %s to %s' % (results.sha256, results.tag)
        else:
            print 'You need specify sha256 [-s] and tag [-t]'

			