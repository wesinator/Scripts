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

import subprocess
import hashlib
import os
import requests
import argparse

__author__ = "A. Sánchez <asanchez@koodous.com>"

URL = 'https://koodous.com/api/apks/%s%s'

def check_device():
    """
        Check if the device and adb program are availables
    """
    try:
        output = subprocess.Popen(['adb', 'devices'], 
                                stdout = subprocess.PIPE).communicate()[0]
    except:
        print "You must to install adb"
        return False

    try:
        device = output.split('\n')[1]
        if device.split('\t')[1] == 'device':
            return True
    except:
        return False
    return False

def extract_apk(path):
    """
        Extract an APK from the phone to "sample.apk"
    """
    output = subprocess.Popen(['adb', 'pull', path, 'sample.apk'], 
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE).communicate()[0]
    if "bytes in" in output:
        return True
    return False


def hash256(filename):
    """
        Calculate sha256 hash of filename
    """
    return hashlib.sha256(open(filename, 'rb').read()).hexdigest()

def check_detected(sha256, token):
    """
        Check against Koodous database is a sha256 has been detected or not
        Return:
            True: Detected
            False: Not detected
            None: Sample is not in koodous
    """
    headers = {'Authorization': 'Token %s' % token}
    url = URL % (sha256, '')
    response = requests.get(url=url, headers=headers)
    json_res = response.json()
    if json_res.get('detail', None):
        return None
    else:
        return json_res.get('detected', False)

def upload(sha256, filename, token):
    """
        Function to upload files to koodous
    """
    
    headers = {'Authorization': 'Token %s' % token}
    
    url = URL % (sha256, '/get_upload_url')
    response = requests.get(url=url, headers=headers)

    if response.status_code == 200:
        files = {'file': open(filename, 'rb')}
        response = requests.post(url=response.json()['upload_url'], 
                          files=files)
        return response.status_code
    else:
        return response.status_code

        
def get_apps():
    """
        Generate a list of apks from the phone using ADB
        Return:
            List of tuples
            Example: (('data/application.apk', 'com.package.name'),
                      (..., ...), ...)
    """
    to_ret = list()
    try:
        output = subprocess.Popen('adb shell pm list packages -f'.split(),
                                stdout = subprocess.PIPE).communicate()[0]
        app_list = output.split('\n')
        for app_line in app_list:
            if len(app_line) > 1:
                #package:/system/app/HPLegacyPlugin/HPLegacyPlugin.apk=com.hp.android.printservice
                apk = app_line.split(':')[1].split('=')[0]
                package_name = app_line.split(':')[1].split('=')[1]
                to_ret.append((apk.strip(), package_name.strip()))
        return to_ret
    except:
        return False

    return to_ret


def main():
    """
        Main function (check parameters and launch process)
    """
    parser = argparse.ArgumentParser(
        description='Script to examine your mobile phone against Koodous database.')

    parser.add_argument('token', action='store', help='Koodous token API')
    args = parser.parse_args()
    if check_device():
        apks = get_apps()
        print "Total APKs to check %d" % len(apks)
        if apks == False:
            print "Device connection problem, retry"
        for apk in apks:
            print "Extracting %s" % apk[1]
            extract_apk(apk[0])
            sha256 = hash256('sample.apk')
            detected = check_detected(sha256, args.token)
            if detected == True:
                print "Detected %s" % apk[1]
            elif detected == None:
                print "Not in Koodous, uploading [%s] %s" % (apk[1], sha256)
                upload(sha256, 'sample.apk', args.token)
            elif detected == False:
                print "%s is OK" % apk[1]

        #Remove the last sample
        os.remove('sample.apk')
    else:
        print "No device connected"

if __name__ == '__main__':
    main()