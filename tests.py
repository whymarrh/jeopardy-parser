#!/usr/bin/python -OO
# -*- coding: utf-8 -*-

import sqlite3
from parser import SQLITE3_DB_NAME, NUMBER_OF_GAMES
from random import randint, randrange

def main():
  """ Ouputs a random clue (with game ID) from 10 random games for manual verification. """
  sql = sqlite3.connect(SQLITE3_DB_NAME)
  # output the format for reference
  print "GID".rjust(5), "R -> Category -> Clue text -> Answer"
  # list of random game ids
  gids = [randint(1, NUMBER_OF_GAMES) for i in xrange(10)]
  for gid in gids:
    rows = sql.execute("SELECT round, category, clue, answer FROM clues INNER JOIN documents ON clues.id = documents.id LEFT JOIN classifications ON classifications.clueid = clues.id LEFT JOIN categories ON classifications.catid = categories.id WHERE game = ?;", (gid, ))
    rows = rows.fetchall()
    # some games were skipped over
    if len(rows) > 0:
      # the game number
      meta = "#%d" % gid
      # pick a random clue from this game
      row = randrange(0, len(rows))
      # output all the things
      print meta.rjust(5), " -> ".join(str(e) for e in rows[row])

if __name__ == "__main__":
  main()
