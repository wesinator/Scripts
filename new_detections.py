#!/usr/bin/python
"""
Copyright (c) 2016. The Koodous Authors. All Rights Reserved.

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
import time

__author__ = "A.Sanchez <asanchez@koodous.com>"


RULENAMES = ["SMSFraud"]
TOKEN = "YOUR TOKEN HERE"

WAITING_TIME = 5*60


def send_to_another_system(rulename, sha256):
    print("Sending %s from %s to my another big system" % (sha256, rulename))
    time.sleep(1) #Simulating the time to send to another system

def mark_as_read(id):
    try:
        res = requests.patch(url="https://koodous.com/api/notifications/%s" % id,
                             headers={"Authorization": "Token %s" % TOKEN},
                             data={"read":True})
    except:
        print("Unable to mark %s as read" % id)
def main():
    while True:

        next_url = "https://api.koodous.com/notifications?read=False"
        results = list()
        while next_url:
            res = requests.get(url=next_url, 
                               headers={"Authorization": "Token %s" % TOKEN}) 

            json_response = res.json()

            next_url = json_response.get("next", None)
            results += json_response.get("results", [])

        for notification in results:
            if notification['type'] == 'ruleset':
                if notification['ruleset']['name'] in RULENAMES:
                    rulename = notification['ruleset']['name']
                    sha256 = notification['apk']['sha256']
                    #md5 = notification['apk']['md5']
                    #sha1 = notification['apk']['sha1']
                    id = notification['id']
                    send_to_another_system(rulename, sha256)
                    mark_as_read(id)

        time.sleep(WAITING_TIME)

if __name__ == '__main__':
    main()
