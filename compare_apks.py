#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2015. The Koodous Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0
   
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import requests
import argparse

error_msg = """
There was an error with report extraction. 
Please send us an email to asanchez@koodous.com with the hashes and we will fix ASAP.

Thank for your collaboration.
"""

BLUE = '\033[94m'
GREEN = '\033[92m'
ORANGE = '\033[93m'
ENDC = '\033[0m'

__author__ = "A. Sánchez <asanchez@koodous.com>"

def download_report(sha256, token):
    url_report = 'https://koodous.com/api/apks/%s/analysis'
    headers = {'Authorization': 'Token %s' % token}
    res = requests.get(url=url_report % sha256,
                      headers=headers)
    try:
        return res.json().get('androguard', None)
    except:
        return None

def main():
    parser = argparse.ArgumentParser(
        description='Script to compare permissions of 2 APKs based on Koodous.')

    parser.add_argument('hash1', action='store', help='sha256 of first APK')
    parser.add_argument('hash2', action='store', help='sha256 of seconds APK')
    parser.add_argument('token', action='store', help='Koodous token API')

    args = parser.parse_args()
    report1 = download_report(args.hash1, args.token)
    report2 = download_report(args.hash2, args.token)
    try:
        perms1 = report1.get('permissions')
        #print report2
        perms2 = report2.get('permissions')
        commons = list(set(perms1) & set(perms2))        
        print "\n***** Common permissions *****"
        for perm in commons:
            print GREEN + perm
        print ENDC + "\n***** Permissions only for hash1 *****"
        for perm in perms1:
            if perm not in commons:
                print ORANGE + perm
        print ENDC + "\n***** Permissions only for hash2 *****"
        for perm in perms2:
            if perm not in commons:
                print BLUE + perm
        print ENDC
        
    except:
        print error_msg

if __name__ == '__main__':
    main()