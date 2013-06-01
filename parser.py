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
		sql.execute("CREATE TABLE classifications(clue_id INTEGER, category_id INTEGER, FOREIGN KEY(clue_id) REFERENCES clues(id), FOREIGN KEY(category_id) REFERENCES categories(id));")
	for i in xrange(1, NUMBER_OF_FILES + 1):
		with open(args.dir + os.sep + "showgame.php?game_id=" + str(i)) as f:
			parse_game(f, sql, i)
	if not args.stdout:
		sql.commit()
	print "All done."

def parse_game(f, sql, gid):
	"""Parses an entire Jeopardy! game and extract individual clues."""
	bsoup = BeautifulSoup(f, "lxml")
	# the title is in the format:
	# J! Archive - Show #XXXX, aired 2004-09-16
	# the last part is all that is required
	airdate = bsoup.title.get_text().split()[-1]
	if not parse_round(bsoup, sql, 1, gid, airdate) or not parse_round(bsoup, sql, 2, gid, airdate):
		# one of the rounds does not exist
		pass
	# the final Jeopardy! round
	r = bsoup.find("table", class_ = "final_round")
	if not r:
		# this game does not have a final clue
		return
	category = r.find("td", class_ = "category_name").get_text()
	text = r.find("td", class_ = "clue_text").get_text()
	answer = BeautifulSoup(r.find("div", onmouseover = True).get("onmouseover"), "lxml")
	answer = answer.find("em").get_text()
	# False indicates no preset value for a clue
	insert(sql, [gid, airdate, 3, category, False, text, answer])

def parse_round(bsoup, sql, rnd, gid, airdate):
	"""Parses and inserts the list of clues from a whole round."""
	round_id = "jeopardy_round" if rnd == 1 else "double_jeopardy_round"
	r = bsoup.find(id = round_id)
	# the game may not have all the rounds
	if not r:
		return False
	# the list of categories for this round
	categories = [c.get_text() for c in r.find_all("td", class_ = "category_name")]
	# the x_coord determines which category a clue is in
	# because the categories come before the clues, we will
	# have to match them up with the clues later on
	x = 0
	for a in r.find_all("td", class_ = "clue"):
		if not a.get_text().strip():
			continue
		value = a.find("td", class_ = re.compile("clue_value")).get_text().lstrip("D: $")
		text = a.find("td", class_ = "clue_text").get_text()
		answer = BeautifulSoup(a.find("div", onmouseover = True).get("onmouseover"), "lxml")
		answer = answer.find("em", class_ = "correct_response").get_text()
		insert(sql, [gid, airdate, rnd, categories[x], value, text, answer])
		# always update x, even if we skip
		# a clue, as this keeps things in order. there
		# are 6 categories, so once we reach the end,
		# loop back to the beginning category
		#
		# x += 1
		# x %= 6
		x = 0 if x == 5 else x + 1
	return True

def insert(sql, clue):
	"""Inserts the given clue into the database."""
	if not sql:
		print clue
		return
	# where clue = [game, airdate, round, category, value, clue, answer]
	# note that at this point, value is False if round is 3
	sql.execute("INSERT OR IGNORE INTO airdates VALUES(?, ?);", (clue[0], clue[1], ))
	sql.execute("INSERT OR IGNORE INTO categories(category) VALUES(?);", (clue[3], ))
	category_id = sql.execute("SELECT id FROM categories WHERE category = ?;", (clue[3], )).fetchone()[0]
	clue_id = sql.execute("INSERT INTO documents(clue, answer) VALUES(?, ?);", (clue[5], clue[6], )).lastrowid
	sql.execute("INSERT INTO clues(game, round, value) VALUES(?, ?, ?);", (clue[0], clue[2], clue[4], ))
	sql.execute("INSERT INTO classifications VALUES(?, ?)", (clue_id, category_id, ))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description = "Parse game files from the J! Archive website.", usage = "%(prog)s [options]", add_help = False)
	parser.add_argument("--help", action = "help", help = "show this help message and exit")
	parser.add_argument("-d", dest = "dir", metavar = "FOLDER", help = "the directory containing the HTML game files", default = "j-archive")
	parser.add_argument("-f", dest = "database", metavar = "FILENAME", help = "the filename for the SQLite database", default = "clues.db")
	parser.add_argument("--stdout", help = "output the clues to stdout and not the database", action = "store_true")
	parser.add_argument("--version", action = "version", version = "2013.06.01")
	main(parser.parse_args())
