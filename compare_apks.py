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
try:
    import ssdeep
    IMPORT_SSDEEP = True
except:
    IMPORT_SSDEEP = False

error_msg = """
There was an error with report extraction. 
Please send us an email to asanchez@koodous.com with the hashes and we will fix ASAP.

Thank for your collaboration.
"""

HEADER = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
ORANGE = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'

__author__ = "A. Sánchez <asanchez@koodous.com>"

def download_report(sha256, token):
    url_report = 'https://koodous.com/api/apks/%s/analysis'
    headers = {'Authorization': 'Token %s' % token}
    res = requests.get(url=url_report % sha256,
                      headers=headers)
    try:
        return res.json()
    except:
        return None

def compare_ssdeep(report1, report2):
    try:
        ssdeep1 = report1['cuckoo']['target']['file']['ssdeep']
        ssdeep2 = report2['cuckoo']['target']['file']['ssdeep']
        print HEADER + "***** APK SSDEEP COMPARISON *****" + ENDC
        print "File 1: %s" % ssdeep1
        print "File 2: %s" % ssdeep2
        print "Similarity: %.2f%%" % ssdeep.compare(ssdeep1, ssdeep2)

        dexes1 = report1['androguard']['dexes']
        dexes2 = report2['androguard']['dexes']

        print HEADER + '***** SIMILARITY BETWEEN DEX FILES ****' + ENDC
        for dex1 in dexes1.iteritems():
            for dex2 in dexes2.iteritems():
                print "[%s - %s]: %.2f%%" % \
                (dex1[0], dex2[0] ,
                 ssdeep.compare(dex1[1]['ssdeep'], dex2[1]['ssdeep']))
    except:
        print RED + error_msg + ENDC

def compare_permissions(report1, report2):
    perms1 = report1.get('androguard', {}).get('permissions')
    perms2 = report2.get('androguard', {}).get('permissions')
    package1 = report1.get('androguard', {}).get('package_name', '')
    package2 = report2.get('androguard', {}).get('package_name', '')
    commons = list(set(perms1) & set(perms2))        
    print HEADER + '\n***** Common permissions *****'
    for perm in commons:
        print GREEN + perm
    print HEADER + "\n***** Permissions only for first APK (%s)*****" % \
                                                                package1
    for perm in perms1:
        if perm not in commons:
            print ORANGE + perm
    print HEADER + "\n***** Permissions only for second APK (%s)*****" % \
                                                                package2
    for perm in perms2:
        if perm not in commons:
            print BLUE + perm
    print ENDC

def main():
    parser = argparse.ArgumentParser(
        description='Script to compare permissions of 2 APKs based on Koodous.')

    parser.add_argument('hash1', action='store', help='sha256 of first APK')
    parser.add_argument('hash2', action='store', help='sha256 of seconds APK')
    parser.add_argument('token', action='store', help='Koodous token API')
    parser.add_argument('--ssdeep', dest='ssdeep', action='store_true',
                        help="Calculate several comparisons between APKs based on ssdeep hash")

    args = parser.parse_args()
    report1 = download_report(args.hash1, args.token)
    report2 = download_report(args.hash2, args.token)

    try:
        compare_permissions(report1, report2)
        if args.ssdeep:
            if IMPORT_SSDEEP:
                compare_ssdeep(report1, report2)
            else:
                print "You must to install ssdeep for python (https://pypi.python.org/pypi/ssdeep)"
        
    except:
        print RED + error_msg + ENDC

if __name__ == '__main__':
    main()
    