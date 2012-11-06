#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

from __future__ import with_statement
import re, sys
import sqlite3
from bs4 import BeautifulSoup

try:
  # debugging prints out the clues instead
  # of inserting them into a database; the
  # argparse module may be better for this
  DEBUGGING     = True if sys.argv[1] == "-d" else False
except IndexError:
  DEBUGGING     = False

GAME_FILES_DIR  = "j-archive/"
NUMBER_OF_GAMES = 3970
SQLITE3_DB_NAME = "clues.db"

def create_db():
  """ Creates and returns the SQLite database, None if not needed. """
  if DEBUGGING:
    return None
  try:
    sql = sqlite3.connect(SQLITE3_DB_NAME)
    sql.execute("PRAGMA foreign_keys = ON;") # SQLite has foreign key support disabled by default
    sql.execute("PRAGMA journal_mode = OFF;")
    sql.execute("PRAGMA synchronous = OFF;")
    sql.execute("CREATE TABLE airdates(game INTEGER PRIMARY KEY, airdate TEXT);")
    sql.execute("CREATE TABLE documents(id INTEGER PRIMARY KEY AUTOINCREMENT, clue TEXT, answer TEXT);")
    sql.execute("CREATE TABLE categories(id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT);") # the categories should really be unique, but that requires extra work when inserting
    sql.execute("CREATE TABLE clues(id INTEGER PRIMARY KEY AUTOINCREMENT, game INTEGER, round INTEGER, value INTEGER, FOREIGN KEY(id) REFERENCES documents(id), FOREIGN KEY(game) REFERENCES airdates(game));")
    sql.execute("CREATE TABLE classifications(clueid INTEGER, catid INTEGER, FOREIGN KEY(clueid) REFERENCES clues(id), FOREIGN KEY(catid) REFERENCES categories(id));")
    return sql
  except sqlite3.OperationalError as e:
    print e
    sys.exit(1)

def db_insert(sql, clue):
  """ Inserts the given clue into the database. """
  # where clue = [game, airdate, round, category, value, clue, answer]
  # note that at this point, value = False if round == 3
  sql.execute("INSERT OR IGNORE INTO airdates VALUES(?,?);", tuple(clue[:2]))
  catid = sql.execute("INSERT INTO categories(category) VALUES(?);", tuple([clue[3]])).lastrowid
  clueid = sql.execute("INSERT INTO documents(clue, answer) VALUES(?,?);", tuple(clue[5:7])).lastrowid
  sql.execute("INSERT INTO clues(game, round, value) VALUES(?,?,?);", tuple([clue[0], clue[2], clue[4]]))
  sql.execute("INSERT INTO classifications VALUES(?,?)", tuple([clueid, catid]))

def parse_clue(clue, category):
  """ Returns a list that models a clue in Jeopardy! """
  # using `str.decode()` in this way seems to break a
  # decent number of clues due to some sort of Unicode
  # issue. regardless, it helps to unescape all the things
  category = category.decode("string-escape")
  value = clue.find("td", class_ = re.compile("clue_value")).string.lstrip("D: $")
  clue_ = clue.find("td", class_ = "clue_text").get_text().decode("string-escape")
  answer = BeautifulSoup(clue.find("div", onmouseover = True).get("onmouseover"), "lxml")
  answer = answer.find("em", class_ = "correct_response").get_text().decode("string-escape")
  return [category, value, clue_, answer]

def parse_round(bsoup, sql, rnd, game_id, airdate):
  """ Parses and inserts the list of clues from a whole round. """
  try:
    if rnd == 1:
      r = bsoup.find(id = "jeopardy_round")
    if rnd == 2:
      r = bsoup.find(id = "double_jeopardy_round")
    # the list of categories for this round
    categories = [c.string.decode("string-escape") for c in r.find_all("td", class_ = "category_name")]
    # the x_coord determines which category a clue is in,
    # because the categories come before the clues, we'll
    # have to match them up with the clues later on
    x_coord = 0
    for a in r.find_all("td", class_ = "clue"):
      try:
        clue = [game_id, airdate, rnd] + parse_clue(a, categories[x_coord])
        if not DEBUGGING:
          db_insert(sql, clue)
        else:
          print clue
      except (AttributeError, UnicodeEncodeError):
        # skip the whole clue if any exceptions are encountered,
        # as individual clues are not worth the trouble
        continue
      finally:
        # always update the x_coord, even if we skip
        # a clue, as this keeps things in order. there
        # are 6 categories, so once we reach the end,
        # loop back to the beginning category
        x_coord = 0 if x_coord == 5 else x_coord + 1
  except (AttributeError, UnicodeEncodeError):
    # there was an error in processing
    # the categories, ignore the round
    pass

def parse_game(filehandle, sql, game_id):
  """ Parses an entire Jeopardy! game, extracting individual clues. """
  bsoup = BeautifulSoup(filehandle, "lxml")
  # the title is in the format:
  # J! Archive - Show #XXXX, aired 2004-09-16
  # the last part is all that is required
  airdate = bsoup.title.get_text().split()[-1]
  # the Jeopardy! round
  parse_round(bsoup, sql, 1, game_id, airdate)
  # the double Jeopardy! round
  parse_round(bsoup, sql, 2, game_id, airdate)
  # the final Jeopardy! round
  try:
    r = bsoup.find("table", class_ = "final_round")
    category = r.find("td", class_ = "category_name").get_text().decode("string-escape")
    clue_ = r.find("td", class_ = "clue_text").get_text().decode("string-escape")
    answer = BeautifulSoup(r.find("div", onmouseover = True).get("onmouseover"), "lxml")
    answer = answer.find("em").get_text().decode("string-escape")
    # "nil" indicates no preset value for a clue
    clue = [game_id, airdate, 3, category, False, clue_, answer]
    if not DEBUGGING:
      db_insert(sql, clue)
    else:
      print clue
  except:
    # if anything goes wrong just ignore this whole round
    pass

def main():
  sql = create_db()
  for i in xrange(1, NUMBER_OF_GAMES + 1):
    filename = GAME_FILES_DIR + "showgame.php?game_id=" + str(i)
    try:
      with open(filename) as f:
        parse_game(f, sql, i)
    except IOError:
      continue
  if sql:
    sql.commit()

if __name__ == "__main__":
  main()
  sys.exit(0)
