# What is this

This, `parser.py`, is a script to extract Jeopardy! clues from the [J! Archive][1] website and dump them into a SQLite database for use elsewhere. No particular application is intended, but a fair number of clues are skipped over when parsing, and any application requiring the complete set of clues will not find it here.

To test the database, `test.py` outputs a random clue from each of 10 random games. Manually comparing these clues to the J! Archive website is a way to verify that the clues are being matched to the proper category, game, etc.

# The initial download

The download script does not mirror the entire site, it simply gets the game pages. Also note that no media files are downloaded (e.g. pictures or audio files) and the parser does not account for media clues. The complete download of the pages (at the time of writing) is approx. 295M, and can take up to 6.5 hours [(1s per page, plus a 5s wait between downloads, 3970 times)][2].

# Getting started

Clone the repo: `git clone git://github.com/whymarrh/jeopardy-parser.git`  
`cd jeopardy-parser`  
`chmod u+x download.sh`  
`chmod u+x tests.py`  
`chmod u+x parser.py`  
Run the download script, parser, and test: `./download.sh && ./time.sh && ./test.py`)  

The "real" running time of the parsing script (i.e. `(time ./parser.py) 2>&1 | grep real`) should not be more than 20 minutes on a decent machine. While that is quite a lot, know that there are **a lot** of clues to go through. The resulting database is ~30M, and in total, the entire process (downloading and parsing) will require approximately [7 hours][3].

# Querying the database

The database (`clues.db`) is split into 5 tables:

* `airdates` - air dates for the shows, indexed by game number.
* `documents` - maps clue ids to clue text and answers.
* `categories` - the categories.
* `clues` - clue ids with metadata (game number, round, and value).
* `classifications` - maps clue ids to category ids.

To get all the clues along with their metadata:

    SELECT clues.id, game, round, value, clue, answer
    FROM clues
    JOIN documents ON clues.id = documents.id
    -- WHERE <expression>
    ;

To get the category that a clue is in, given a clue id:

    SELECT clueid, category
    FROM classifications
    JOIN categories ON catid = categories.id
    -- WHERE <expression>
    ;

To get everything (although it is better to pick and choose what you're looking for):

    SELECT clues.id, clues.game, airdate, round, value, clue, answer, category
    FROM clues
    JOIN airdates ON clues.game = airdates.game
    JOIN documents ON clues.id = documents.id
    JOIN classifications ON clues.id = classifications.clueid
    JOIN categories ON classifications.catid = categories.id
    -- WHERE <expression>
    ;

  [1]: http://j-archive.com/
  [2]:http://www.wolframalpha.com/input/?i=%281s+%2B+5s%29+*+3970
  [3]:http://www.wolframalpha.com/input/?i=%281s+%2B+5s%29+*+3970+%2B+20+minutes