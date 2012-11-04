# What is this

`parser.py` extracts Jeopardy! clues from the [J! Archive][1] website and dumps them into a SQLite database for use elsewhere. No particular application is intended, but a fair number of clues are skipped over when parsing. Any application requiring the complete set of clues will not find it here.

`tests.py` spits out 10 random clues from various games. Manually comparing these clues to the J! Archive website is a simple way to verify that the clues are being matched to the proper category, round, value, game, etc.

# Getting started

Clone the repo: `git clone git://github.com/whymarrh/jeopardy-parser.git`  
`cd jeopardy-parser`  
`chmod u+x download.sh`  
`chmod u+x parser.py`  
Run the download script and parser: `./download.sh && ./parser.py`)  

The "real" running time of the parsing script (i.e. `(time ./parser.py) 2>&1 | grep real`) should not be more than 160 minutes on a decent machine. I know even that is quite a lot, but there are **a lot** of clues to go through. The resulting database is ~30M.

# Regarding the initial download

The download script does not mirror the entire site, it simply gets the game pages. Also note that no media files are downloaded (e.g. pictures) and the parser does not account for media clues. The complete download of the pages (at the time of writing) is approx. 295M, and can take up to [6.5 hours][2] (1s per page, plus a 5s wait between downloads, 3970 times).

# Querying the database

The database is split into 5 tables:

* `airdates` - air dates for the shows, indexed by game number.
* `documents` - maps clue ids to clue text and answers.
* `categories` - the categories.
* `clues` - clue ids with metadata (game number, round, and value).
* `classifications` - maps clue ids to category ids.

To get all the clues with their metadata:

    SELECT clues.id, game, round, value, clue, answer
    FROM clues
    INNER JOIN documents ON clues.id = documents.id
    -- WHERE <expression>
    ;

To get all the categories that a clue is in, given a clue id:

    SELECT clueid, category
    FROM classifications
    INNER JOIN categories ON classifications.catid = categories.id
    -- WHERE <expression>
    ;

  [1]: http://j-archive.com/
  [2]:http://www.wolframalpha.com/input/?i=%281s+%2B+5s%29+*+3970