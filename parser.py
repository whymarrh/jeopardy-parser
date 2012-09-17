#!/usr/bin/python -O

import re
from bs4 import BeautifulSoup

GAME_FILES_DIR  = "j-archive/"
NUMBER_OF_GAMES = 44

def inclusive_range(start, stop, step = 1):
  """ A range() clone that includes the rightmost extreme value. """
  # http://zeta-puppis.com/2008/03/06/inclusive-range-in-python/
  l = []
  while start <= stop:
    l.append(start)
    start += step
  return l

def print_game(g):
  """ Pretty-prints a completely parsed Jeopardy game. """
  tab = "\t"
  print
  print g[0]
  for e in g[1]:
    print tab,
    print e
  print

def parse_clue(clue, round, category):
  """ Returns a list that models a question in Jeopardy. """
  # [round, category, value, question, answer]
  question = [round]
  question.append(category.decode("string-escape"))
  question.append(clue.find("td", class_ = re.compile("clue_value")).string)
  question.append(clue.find("td", class_ = "clue_text").get_text().decode("string-escape"))
  answer = BeautifulSoup(clue.find("div", onmouseover = True).get("onmouseover"), "lxml")
  answer = answer.find("em", class_ = "correct_response").get_text().decode("string-escape")
  question.append(answer)
  return question

def parse_game(filehandle):
  """ Returns a list containing the game's metadata and question list. """
  bsoup = BeautifulSoup(filehandle, "lxml")
  metadata = bsoup.find(id = "game_title").string
  # stores the list of questions, each of which is a list itself
  questions = []
  
  try:
    jeopardy_round = bsoup.find(id = "jeopardy_round")
    # the list of categories for the Jeopardy round of questions
    categories = []
    for c in jeopardy_round.find_all("td", class_ = "category_name"):
      categories.append(c.string.decode("string-escape"))
    # the x-coord is which category the question fall into
    x_coord = 0
    for a in jeopardy_round.find_all("td", class_ = "clue"):
      try:
        questions.append(parse_clue(a, "1", categories[x_coord]))
      except (AttributeError, UnicodeEncodeError):
        continue
      finally:
        x_coord = 0 if x_coord == 5 else x_coord + 1
  except (AttributeError, UnicodeEncodeError):
    # there was an error in processing
    # the categories. ignore the round
    pass
  
  try:
    double_jeopardy = bsoup.find(id = "double_jeopardy_round")
    # the list of categories for the double Jeopardy round of questions
    categories = []
    for c in double_jeopardy.find_all("td", class_ = "category_name"):
      categories.append(c.string.decode("string-escape"))
    # the x-coord is which category the question falls into
    x_coord = 0
    for a in double_jeopardy.find_all("td", class_ = "clue"):
      try:
        questions.append(parse_clue(a, "2", categories[x_coord]))
      except (AttributeError, UnicodeEncodeError):
        continue
      finally:
        x_coord = 0 if x_coord == 5 else x_coord + 1
  except (AttributeError, UnicodeEncodeError):
    # there was an error in processing
    # the categories. ignore the round
    pass
  
  # final Jeopardy round
  try:
    fj = bsoup.find("table", class_ = "final_round")
    question = ["3"]
    question.append(fj.find("td", class_ = "category_name").get_text().decode("string-escape"))
    question.append("nil")
    question.append(fj.find("td", class_ = "clue_text").get_text().decode("string-escape"))
    answer = BeautifulSoup(fj.find("div", onmouseover = True).get("onmouseover"), "lxml")
    answer = answer.find("em").get_text().decode("string-escape")
    question.append(answer)
    questions.append(question)
  except:
    # if anything goes wrong just ignore this whole clue
    pass
  
  return [metadata, questions]

def main():
  games = []
  for i in inclusive_range(1, NUMBER_OF_GAMES):
    filename = GAME_FILES_DIR + "showgame.php?game_id=" + str(i)
    f = open(filename)
    games.append(parse_game(f))
    f.close()
  for game in games:
    print_game(game)

if __name__ == "__main__":
  main()

