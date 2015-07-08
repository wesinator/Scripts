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

import zipfile
import argparse

__author__ = "A.Sanchez <asanchez@koodous.com>"

def unpack(filename, dst):
    to_ret = True

    with open(filename, 'rb') as fd:
	    content = fd.read()
	    fd.close()

    try:
        zipped = zipfile.ZipFile(filename)
        for name in zipped.namelist():
            content += ' ' + zipped.read(name)

    except:
        to_ret = False

    with open(dst, 'wb') as fd:
    	fd.write(content)
    return to_ret

def main():
	parser = argparse.ArgumentParser(
		description='Script to unpack APKs and concatenate in the same file.')

	parser.add_argument('input', action='store', help='APK to unpack')
	parser.add_argument('-o', '--output', dest='output',
					help='output file, by default is "input + .unpacked"', 
					default=None)

	args = parser.parse_args()
	if not args.output:
		args.output = args.input + ".unpacked"

	unpack(args.input, args.output)

if __name__ == '__main__':
	main()