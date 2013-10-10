#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import itertools
import os
import urllib2
import time

current_working_directory = os.path.dirname(os.path.abspath(__file__))
archive_folder = os.path.join(current_working_directory, "j-archive")
SECONDS_BETWEEN_REQUESTS = 5
ERROR_MSG = "ERROR: No game"

def main():
	create_archive_dir()
	print "Downloading game files"
	download_pages()

def create_archive_dir():
	if not os.path.isdir(archive_folder):
		print "Making %s" % archive_folder
		os.mkdir(archive_folder)

def download_pages():
	for page in itertools.count(1):
		new_file_name = "%s.html" % page
		destination_file_path = os.path.join(archive_folder, new_file_name)
		if not os.path.exists(destination_file_path):
			html = download_page(page)
			if ERROR_MSG in html:
				print "Finished downloading. Now parse."
				break
			if html:
				save_file(html, destination_file_path)
				time.sleep(SECONDS_BETWEEN_REQUESTS) # Remember to be kind to the server
		else:
			print "Already downloaded %s" % destination_file_path

def download_page(page):
	url = 'http://j-archive.com/showgame.php?game_id=%s' % page
	html = None
	try:
		response = urllib2.urlopen(url)
		if response.code == 200:
			print "Downloading %s" % url
			html = response.read()
		else:
			print "Invalid URL: %s" % url
	except urllib2.HTTPError:
		print "failed to open %s" % url
	return html

def save_file(html, filename):
	try:
		with open(filename, 'w') as f:
			f.write(html)
	except IOError:
		print "Couldn't write to file %s" % filename

if __name__ == "__main__":
	main()
