#!/usr/bin/env python -OO
# -*- coding: utf-8 -*-

from __future__ import with_statement
from bs4 import BeautifulSoup
import argparse, re, os, sys, sqlite3

def main(args):
	"""Loop thru all the game files and parse them."""
	if not os.path.isdir(args.dir):
		print "The specified folder is not a directory."
		sys.exit(1)
	NUMBER_OF_FILES = len(os.listdir(args.dir))
	print "Parsing", NUMBER_OF_FILES, "files."
	sql = None
	if not args.stdout:
		sql = sqlite3.connect(args.database)
		sql.execute("PRAGMA foreign_keys = ON;")
		sql.execute("CREATE TABLE airdates(game INTEGER PRIMARY KEY, airdate TEXT);")
		sql.execute("CREATE TABLE documents(id INTEGER PRIMARY KEY AUTOINCREMENT, clue TEXT, answer TEXT);")
		sql.execute("CREATE TABLE categories(id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT UNIQUE);")
		sql.execute("CREATE TABLE clues(id INTEGER PRIMARY KEY AUTOINCREMENT, game INTEGER, round INTEGER, value INTEGER, FOREIGN KEY(id) REFERENCES documents(id), FOREIGN KEY(game) REFERENCES airdates(game));")
		sql.execute("CREATE TABLE classifications(clue_id INTEGER, cat_id INTEGER, FOREIGN KEY(clueid) REFERENCES clues(id), FOREIGN KEY(catid) REFERENCES categories(id));")
	for i in xrange(1, NUMBER_OF_FILES + 1):
		with open(args.dir + os.sep + "showgame.php?game_id=" + str(i)) as f:
			pgame(f, sql, i)
	if not args.stdout:
		sql.commit()
	print "All done."

def pgame(f, sql, gid):
	"""Parses an entire Jeopardy! game and extract individual clues."""
	bsoup = BeautifulSoup(f, "lxml")
	# the title is in the format:
	# J! Archive - Show #XXXX, aired 2004-09-16
	# the last part is all that is required
	airdate = bsoup.title.get_text().split()[-1]
	if not pround(bsoup, sql, 1, gid, airdate) or not pround(bsoup, sql, 2, gid, airdate):
		return
	# the final Jeopardy! round
	r = bsoup.find("table", class_ = "final_round")
	if not r:
		# this game doesn't have a final clue
		return
	category = r.find("td", class_ = "category_name").get_text()
	text = r.find("td", class_ = "clue_text").get_text()
	answer = BeautifulSoup(r.find("div", onmouseover = True).get("onmouseover"), "lxml")
	answer = answer.find("em").get_text()
	# False indicates no preset value for a clue
	insert(sql, [gid, airdate, 3, category, False, text, answer])

def pround(bsoup, sql, rnd, gid, airdate):
	"""Parses and inserts the list of clues from a whole round."""
	if rnd == 1:
		r = bsoup.find(id = "jeopardy_round")
	if rnd == 2:
		r = bsoup.find(id = "double_jeopardy_round")
	# the game may not have all the rounds
	if not r:
		return False
	# the list of categories for this round
	categories = [c.get_text() for c in r.find_all("td", class_ = "category_name")]
	# the x_coord determines which category a clue is in
	# because the categories come before the clues, we'll
	# have to match them up with the clues later on
	x_coord = 0
	for a in r.find_all("td", class_ = "clue"):
		if not a.get_text().strip():
			continue
		value = a.find("td", class_ = re.compile("clue_value")).get_text() #.lstrip("D: $")
		text = a.find("td", class_ = "clue_text").get_text()
		answer = BeautifulSoup(a.find("div", onmouseover = True).get("onmouseover"), "lxml")
		answer = answer.find("em", class_ = "correct_response").get_text()
		insert(sql, [gid, airdate, rnd, categories[x_coord], value, text, answer])
		# always update the x_coord, even if we skip
		# a clue, as this keeps things in order. there
		# are 6 categories, so once we reach the end,
		# loop back to the beginning category
		x_coord = 0 if x_coord == 5 else x_coord + 1
	return True

def insert(sql, clue):
	"""Inserts the given clue into the database."""
	if not sql:
		print clue
		return
	# where clue = [game, airdate, round, category, value, clue, answer]
	# note that at this point, value is False if round is 3
	sql.execute("INSERT OR IGNORE INTO airdates VALUES(?,?);", (clue[0], clue[1], ))
	sql.execute("INSERT OR IGNORE INTO categories(category) VALUES(?);", (clue[3], ))
	catid = sql.execute("SELECT id FROM categories WHERE category = ?;", (clue[3], )).fetchone()[0]
	clueid = sql.execute("INSERT INTO documents(clue, answer) VALUES(?,?);", (clue[5], clue[6], )).lastrowid
	sql.execute("INSERT INTO clues(game, round, value) VALUES(?,?,?);", (clue[0], clue[2], clue[4], ))
	sql.execute("INSERT INTO classifications VALUES(?,?)", (clueid, catid, ))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Parse game files from the J! Archive website.", usage = "%(prog)s [options]", add_help = False)
	parser.add_argument("--help", action = "help", help = "show this help message and exit")
	parser.add_argument("-d", dest = "dir", metavar = "FOLDER", help = "the directory containing the HTML game files", default = "j-archive")
	parser.add_argument("-f", dest = "database", metavar = "FILENAME", help = "the filename for the SQLite database", default = "clues.db")
	parser.add_argument("--stdout", help = "output the clues to stdout and not the database", action = "store_true")
	parser.add_argument("--version", action = "version", version = "2013.05.16")
	main(parser.parse_args())
