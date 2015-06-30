#!/usr/bin/python
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
import sys

headers = None

help_text = """Script to search against Koodous database according certain terms
    Syntax: 
        ./%s <token> <search terms>
    Example: 
        ./%s 12345 "package_name:\\"com.whatsapp\\" and not developer:\\"WhatsApp Inc.\\""
""" % (sys.argv[0], sys.argv[0])

def search(string, token, limit=None):
    """
        Return hashes list according a search string
    """
    to_ret = list()
    headers = {'Authorization': 'Token %s' % token}

    if not limit:
        limit = float('Inf')
    next_page = 'https://koodous.com/api/apks?search=%s' % string
    while next_page and len(to_ret) < limit:
        res = requests.get(url=next_page, 
                           headers=headers)
        next_page = res.json().get('next', None)
        for sample in res.json().get('results', []):
            to_ret.append(sample.get('sha256', None))
        
    return to_ret

def main():
    if len(sys.argv) != 3:
        print help_text
        return
    token = sys.argv[1]
    search_terms = sys.argv[2]
    hashes = search(search_terms, token, limit=5000)
    for sha256 in hashes:
        print sha256

if __name__ == '__main__':
    main()