#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

import itertools
import os
import urllib2
import time
import futures as futures

current_working_directory = os.path.dirname(os.path.abspath(__file__))
archive_folder = os.path.join(current_working_directory, "j-archive")
SECONDS_BETWEEN_REQUESTS = 5
ERROR_MSG = "ERROR: No game"
NUM_THREADS = 2 # Be conservative
try:
    import multiprocessing
    # Since it's a lot of IO let's double # of actual cores
    NUM_THREADS = multiprocessing.cpu_count() * 2
    print 'Using {} threads'.format(NUM_THREADS)
except (ImportError, NotImplementedError):
    pass

def main():
	create_archive_dir()
	print "Downloading game files"
	download_pages()

def create_archive_dir():
	if not os.path.isdir(archive_folder):
		print "Making %s" % archive_folder
		os.mkdir(archive_folder)

def download_pages():
	page = 1
	with futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
		# We submit NUM_THREADS tasks at a time since we don't know how many
		# pages we will need to download in advance
		while True:
			l = []
			for i in range(NUM_THREADS):
				f = executor.submit(download_and_save_page, page)
				l.append(f)
				page += 1
			# Block and stop if we're done downloading the page
			if not all(f.result() for f in l):
				break

def download_and_save_page(page):
	new_file_name = "%s.html" % page
	destination_file_path = os.path.join(archive_folder, new_file_name)
	if not os.path.exists(destination_file_path):
		html = download_page(page)
		if ERROR_MSG in html:
			# Now we stop
			print "Finished downloading. Now parse."
			return False
		elif html:
			save_file(html, destination_file_path)
			time.sleep(SECONDS_BETWEEN_REQUESTS) # Remember to be kind to the server
	else:
		print "Already downloaded %s" % destination_file_path
	return True

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
