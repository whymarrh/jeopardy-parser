#!/usr/bin/python -O

import re
from sys import argv
from bs4 import BeautifulSoup

try:
  DEBUGGING     = argv[1]
except IndexError:
  DEBUGGING     = False
GAME_FILES_DIR  = "j-archive/"
NUMBER_OF_GAMES = 3970

def range_inclusive(start, stop, step = 1):
  """ A range() clone that includes the rightmost extreme value. """
  # http://zeta-puppis.com/2008/03/06/inclusive-range-in-python/
  l = []
  while start <= stop:
    l.append(start)
    start += step
  return l

def parse_clue(clue, category):
  """ Returns a list that models a question in Jeopardy. """
  
  # using `str.decode()` in this way seems to break a
  # decent number of clues due to some sort of Unicode
  # issue. regardless, it helps to unescape all the things
  
  category = category.decode("string-escape")
  value = clue.find("td", class_ = re.compile("clue_value")).string
  clue_ = clue.find("td", class_ = "clue_text").get_text().decode("string-escape")
  answer = BeautifulSoup(clue.find("div", onmouseover = True).get("onmouseover"), "lxml")
  answer = answer.find("em", class_ = "correct_response").get_text().decode("string-escape")
  return [category, value, clue_, answer]

def parse_round(bsoup, rnd, game_id, airdate):
  """ Parses and returns the list of questions from a whole round. """
  try:
    
    # the list of questions for this round all structured
    # like so: [game_id, airdate, round, category, value, clue, answer]
    questions = []
    
    if rnd == "1":
      r = bsoup.find(id = "jeopardy_round")
    if rnd == "2":
      r = bsoup.find(id = "double_jeopardy_round")
    
    # the list of categories for this round
    categories = []
    for c in r.find_all("td", class_ = "category_name"):
      category = c.string.decode("string-escape")
      categories.append(category)
    
    # the x_coord determines which category a question is in,
    # because the categories come before the questions, we'll have
    # to match them up on the fly
    x_coord = 0
    for a in r.find_all("td", class_ = "clue"):
      try:
        question = [game_id, airdate, rnd] + parse_clue(a, categories[x_coord])
        questions.append(question)
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
    
    if DEBUGGING is not False:
      for q in questions:
        print q
    
  except (AttributeError, UnicodeEncodeError):
    # there was an error in processing
    # the categories, ignore the round
    pass
    

def parse_game(filehandle, game_id):
  """ Parses an entire Jeopardy game, extracting individual clues. """
  bsoup = BeautifulSoup(filehandle, "lxml")
  airdate = bsoup.title.get_text().split()[-1]

  parse_round(bsoup, "1", game_id, airdate)
  parse_round(bsoup, "2", game_id, airdate)
  
  # the final Jeopardy round
  try:
    r = bsoup.find("table", class_ = "final_round")
    category = r.find("td", class_ = "category_name").get_text().decode("string-escape")
    clue = r.find("td", class_ = "clue_text").get_text().decode("string-escape")
    answer = BeautifulSoup(r.find("div", onmouseover = True).get("onmouseover"), "lxml")
    answer = answer.find("em").get_text().decode("string-escape")
    question = [game_id, airdate, "3", category, "nil", clue, answer]
    if DEBUGGING is not False: print question
  except:
    # if anything goes wrong just ignore this whole round
    pass

def main():
  for i in range_inclusive(1, NUMBER_OF_GAMES):
    filename = GAME_FILES_DIR + "showgame.php?game_id=" + str(i)
    f = open(filename)
    parse_game(f, i)
    f.close()

if __name__ == "__main__": main()
