#!/usr/bin/python -O
# -*- coding: utf-8 -*-

import sqlite3
from parser import SQLITE3_DB_NAME
from random import randint, randrange

def main():
  """ Ouputs a random clue (with game ID) from 10 random games for checking. """
  sql = sqlite3.connect(SQLITE3_DB_NAME)
  # list of random game id numbers
  gids = [randint(1, 3790) for i in xrange(10)]
  # output format
  print "GID".rjust(5), "R -> Category -> Clue text -> Answer"
  for gid in gids:
    rows = sql.execute("select * from clues where game = ?", (gid, ))
    rows = rows.fetchall()
    # some games were skipped over
    if len(rows) > 0:
      meta = "#%d" % gid
      print meta.rjust(5),
      row = randrange(0, len(rows))
      print rows[row][2], "->", rows[row][3], "->", rows[row][5], "->", rows[row][6]

if __name__ == "__main__":
  main()
