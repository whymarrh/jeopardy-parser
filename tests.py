#!/usr/bin/python -O
# -*- coding: utf-8 -*-

import sqlite3
from parser import SQLITE3_DB_NAME
from random import randint, randrange

def main():
  """ Ouputs a random clue (with game ID) from 10 random games for manual verification. """
  sql = sqlite3.connect(SQLITE3_DB_NAME)
  # list of random game ids
  gids = [randint(1, 3790) for i in xrange(10)]
  # output format
  print "GID".rjust(5), "R -> Category -> Clue text -> Answer"
  for gid in gids:
    rows = sql.execute("SELECT round, category, clue, answer FROM clues INNER JOIN documents ON clues.id = documents.id LEFT JOIN classifications ON classifications.clueid = clues.id LEFT JOIN categories ON classifications.catid = categories.id WHERE game = ?;", (gid, ))
    rows = rows.fetchall()
    # some games were skipped over
    if len(rows) > 0:
      meta = "#%d" % gid
      row = randrange(0, len(rows))
      print meta.rjust(5), " -> ".join(str(e) for e in rows[row])

if __name__ == "__main__":
  main()
