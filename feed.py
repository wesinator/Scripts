################################################################################
#
# Copyright (C) 2016, Koodous
# Author: Antonio Sanchez <asanchez@koodous.com>
# All rights reserved.
#
################################################################################

import argparse
import requests
import time
import os
import sys
from datetime import datetime, timedelta

APKS_FOLDER = 'apks'
ANALYSIS_FOLDER = 'analysis'

ERROR_MSG = """You have no permissions to use this feed.
Please contact with support@koodous.com"""

TOKEN = ""

header = {"Authorization": "Token %s" % TOKEN}

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

def create_folders():
    try:
        os.mkdir(APKS_FOLDER)
    except:
        pass
    try:
        os.mkdir(ANALYSIS_FOLDER)
    except:
        pass

def retrieve_apks_feed(period):
    params = {}
    if period == 60:
        params= {"package": (datetime.utcnow() - timedelta(hours = 1)).strftime("%Y%m%dT%H")}
    res = requests.get("https://api.koodous.com/feed/apks", headers=header, params=params)
    if res.status_code == 401:
        print ERROR_MSG
        sys.exit(0)
    filename = res.headers["Content-Disposition"].split("'")[-1]
    with open(os.path.join(APKS_FOLDER, filename), "wb") as fd:
        fd.write(res.content)
    print "Downloaded file %s with samples download link" % \
                                            os.path.join(APKS_FOLDER, filename)

def retrieve_analysis_feed(period):
    params = {}
    if period == 60:
        params= {"package": (datetime.utcnow() - timedelta(hours = 1)).strftime("%Y%m%dT%H")}
    res = requests.get("https://api.koodous.com/feed/analyses", headers=header, params=params)
    if res.status_code == 401:
        print ERROR_MSG
        sys.exit(0)
    filename = res.headers["Content-Disposition"].split("'")[-1]
    with open(os.path.join(ANALYSIS_FOLDER, filename), "wb") as fd:
        fd.write(res.content)
    print "Downloaded analysis in %s" % os.path.join(ANALYSIS_FOLDER, filename)

def wait_minutes(minutes):
    for i in range(1, minutes+1):
        print "Waiting %s minutes" % (minutes)
        time.sleep(60)
        print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('period', type=int, help='period in minutes', 
                        choices=[5,60])
    parser.add_argument('--apks', dest='apks', action='store_true',
                        help="Download the zip with apks download link")
    parser.add_argument('--analysis', dest='analysis', action='store_true',
                        help="Download the zip with the analysis feed")
    args = parser.parse_args()

    if not TOKEN or len(TOKEN) < 40:
        print "Please, set a correct TOKEN in the script"
        return
        
    create_folders()
    while True:
        if args.apks:
            retrieve_apks_feed(args.period)
        if args.analysis:
            retrieve_analysis_feed(args.period)
        print "Waiting for the next package"

        wait_minutes(args.period)

if __name__ == '__main__':
    main()
