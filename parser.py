#!/usr/bin/python -O
# -*- coding: utf-8 -*-

import re
import sqlite3
from sys import argv
from bs4 import BeautifulSoup

try:
  DEBUGGING     = True if argv[1] == "-d" else False
except IndexError:
  DEBUGGING     = False
GAME_FILES_DIR  = "j-archive/"
NUMBER_OF_GAMES = 3790
SQLITE3_DB_NAME = "clues.db"

def create_db():
  # http://www.sqlite.org/fts3.html
  a = "CREATE VIRTUAL TABLE clues USING fts3"
  b = "(game, airdate, round, category, value, clue, answer)"
  
  sql = sqlite3.connect(SQLITE3_DB_NAME)
  sql.execute("%s%s" % (a, b))
  return sql

def db_insert(sql, clue):
  sql.execute("insert into clues values(?,?,?,?,?,?,?)", tuple(clue))
  sql.commit()

def parse_clue(clue, category):
  """ Returns a list that models a clue in Jeopardy. """

  # using `str.decode()` in this way seems to break a
  # decent number of clues due to some sort of Unicode
  # issue. regardless, it helps to unescape all the things

  category = category.decode("string-escape")
  value = clue.find("td", class_ = re.compile("clue_value")).string
  clue_ = clue.find("td", class_ = "clue_text").get_text().decode("string-escape")
  answer = BeautifulSoup(clue.find("div", onmouseover = True).get("onmouseover"), "lxml")
  answer = answer.find("em", class_ = "correct_response").get_text().decode("string-escape")
  return [category, value, clue_, answer]

def parse_round(bsoup, sql, rnd, game_id, airdate):
  """ Parses and returns the list of clues from a whole round. """
  try:

    if rnd == 1:
      r = bsoup.find(id = "jeopardy_round")
    if rnd == 2:
      r = bsoup.find(id = "double_jeopardy_round")

    # the list of categories for this round
    categories = [c.string.decode("string-escape") for c in r.find_all("td", class_ = "category_name")]

    # the x_coord determines which category a clue is in,
    # because the categories come before the clues, we'll have
    # to match them up on the fly
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
  """ Parses an entire Jeopardy game, extracting individual clues. """
  bsoup = BeautifulSoup(filehandle, "lxml")
  airdate = bsoup.title.get_text().split()[-1]

  parse_round(bsoup, sql, 1, game_id, airdate)
  parse_round(bsoup, sql, 2, game_id, airdate)

  # the final Jeopardy round
  try:
    r = bsoup.find("table", class_ = "final_round")
    category = r.find("td", class_ = "category_name").get_text().decode("string-escape")
    clue_ = r.find("td", class_ = "clue_text").get_text().decode("string-escape")
    answer = BeautifulSoup(r.find("div", onmouseover = True).get("onmouseover"), "lxml")
    answer = answer.find("em").get_text().decode("string-escape")
    clue = [game_id, airdate, 3, category, "nil", clue_, answer]
    if not DEBUGGING:
      db_insert(sql, clue)
    else:
      print clue
  except:
    # if anything goes wrong just ignore this whole round
    pass

def main():
  try:
    sql = create_db()
  except sqlite3.OperationalError:
    # if the `clues` table alredy exists
    print "The `clues` table already exists. Overwriting it would be a mistake."
    exit(1)
  
  for i in xrange(1, NUMBER_OF_GAMES + 1):
    filename = GAME_FILES_DIR + "showgame.php?game_id=" + str(i)
    f = open(filename)
    parse_game(f, sql, i)
    f.close()

if __name__ == "__main__":
  main()
