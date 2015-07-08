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

help_description="""

	The script will look for all the common strings between files in A group and
	it will remove all strings found in the files of B group

    All given Zip files will be extracted and the strings will be retrieved from
	them

	framirez@koodous.com | 2015

 """

import os
import re
import sys
import magic
import shutil
import string
import zipfile
import argparse
import tempfile
import re

def get_file_type(file_name):
	file_type = ""
	content = ""

	with open(file_name, "rb") as f:
		content = f.read()

	ms = magic.open(magic.MAGIC_NONE)
	ms.load()
	file_type = ms.buffer(content)
	ms.close()

	return file_type

def is_zip_file(file_name):
	file_type = get_file_type(file_name)
	is_zip = "Zip" in file_type

	return is_zip

def strings(file_name, min_string_length):
	with open(file_name, "rb") as f:
		result = ""
		for char in f.read():
			if char in string.printable[:-2]:
				result += char
				continue
			if len(result) >= min_string_length:
				yield result
			result = ""

def get_zip_files_strings(zip_file, files_include, min_string_length):
	print '\x1b[%sm%s\x1b[0m' % (';'.join(['32']), zip_file), " UnZipping file and get the strings"

	found_strings = []
	content = ""
	with open(zip_file, 'rb') as fh:
		content = fh.read()
		fh.close()

	
	zipped = zipfile.ZipFile(zip_file)
	for name in zipped.namelist():
	
		if files_include is None or name in files_include:
			content += ' ' + zipped.read(name)

	strings = re.findall("[\x1f-\x7e]{%s,}" % min_string_length, content)
	strings += [str(ws.decode("utf-16le")) for ws in re.findall("(?:[\x1f-\x7e][\x00]){%s,}" % min_string_length, content)]
	
	return strings





def process_group(file_list, files_include, operation_type, min_string_length):
	group_strings = []
	
	for file_name in file_list:
#		if is_zip_file(file_name):
		try:
			file_strings = get_zip_files_strings(file_name, \
				files_include, min_string_length)
		except Exception, e:
#		else:
			print e
			print '\x1b[%sm%s\x1b[0m' % (';'.join(['32']), file_name), " Get the strings"

			file_strings = strings(file_name, min_string_length)
		
		group_strings.append(set(file_strings))

	if operation_type == "intersection":
		processed_strings = reduce(set.__and__, group_strings)

	elif operation_type == "union":
		processed_strings = reduce(set.__or__, group_strings)

	return processed_strings
			
def pretty_print(group):
	for similar in group:
		similar = similar.replace("\n","").replace("\t","").replace("\r","")
		if not re.search("^\s*$", similar):
			print similar


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description=help_description)

	parser.add_argument('-f', '--files', dest="files", \
		help='Files to get the strings, for default all of them', default=None)
	parser.add_argument('-m', '--min-string', dest="min_string_length", \
		help='Minimum length for each strings', default=8)
	parser.add_argument('-a', action='append', dest='a_group', default=[], \
		help='Add files to compare A group')
	parser.add_argument('-b', action='append', dest='b_group', default=[], \
		help='Add files to compare B group')

	args = parser.parse_args()
	results = parser.parse_args()

	if results.a_group:
		a_group = process_group(results.a_group, results.files, "intersection", int(results.min_string_length))

	if results.b_group:
		b_group = process_group(results.b_group, results.files, "union", int(results.min_string_length))
	
	if results.b_group:
		difference = a_group - b_group
		pretty_print(difference)

	else:
		pretty_print(a_group)


	if results.a_group:	
		print '\x1b[%sm%s\x1b[0m' % (';'.join(['1']), str(len(a_group))), "\tcommon string found between all files in A group"
		
	if results.b_group:
		print '\x1b[%sm%s\x1b[0m' % (';'.join(['1']), str(len(b_group))), "\tunion strings found in B group"
	
	if results.a_group and results.b_group:
		print '\x1b[%sm%s\x1b[0m' % (';'.join(['1']), str(len(a_group - b_group))), "\tstring from A group not present in B group" 
