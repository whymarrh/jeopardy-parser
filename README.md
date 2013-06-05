# What is this

A script to extract [Jeopardy!][4] clues from the [J! Archive][1] website and dump them into a SQLite database for use elsewhere (no particular application is intended).

Python 2.7.2 and SQLite 3.7.12 are tested.

# The initial download

The download script does not mirror the entire site, it simply gets the game pages. Also note that no media files are downloaded (e.g. pictures or audio files) and the parser does not account for media clues. The complete download of the pages (at the time of writing) is ~300M, and can take ~6.5 hours [(1s per page, plus a 5s wait between downloads, 3970 times)][2].

(Note that [Windows does not allow `?` characters in its filenames][5]. The downloaded files will be renamed to replace `?` with `_` and this will require a small modification of the parser on [line 25][6].)

# Getting started

1. Clone the repo: `git clone git://github.com/whymarrh/jeopardy-parser.git`
2. `cd jeopardy-parser`
3. `chmod +x build.sh`
4. Run `./build.sh` and wait

The "real" running time of the parsing script (i.e. `(time ./parser.py) 2>&1 | grep real`) should be ~20 minutes on a decent machine. The resulting database is ~30M, and in total, the entire process (downloading and parsing) will require [~7 hours][3].

# Querying the database

The database is split into 5 tables:

- `airdates` - airdates for the shows, indexed by game number.
- `documents` - maps clue IDs to clue text and answers.
- `categories` - the categories.
- `clues` - clue IDs with metadata (game number, round, and value).
- `classifications` - maps clue IDs to category IDs.

To get all the clues along with their metadata:

    SELECT clues.id, game, round, value, clue, answer
    FROM clues
    JOIN documents ON clues.id = documents.id
    -- WHERE <expression>
    ;

To get the category that a clue is in, given a clue id:

    SELECT clue_id, category
    FROM classifications
    JOIN categories ON cat_id = categories.id
    -- WHERE <expression>
    ;

To get everything (although it is better to pick and choose what you're looking for):

    SELECT clues.id, clues.game, airdate, round, value, category, clue, answer
    FROM clues
    JOIN airdates ON clues.game = airdates.game
    JOIN documents ON clues.id = documents.id
    JOIN classifications ON clues.id = classifications.clue_id
    JOIN categories ON classifications.cat_id = categories.id
    -- WHERE <expression>
    ;

  [1]:http://j-archive.com/
  [2]:http://www.wolframalpha.com/input/?i=%281s+%2B+5s%29+*+3970
  [3]:http://www.wolframalpha.com/input/?i=%281s+%2B+5s%29+*+3970+%2B+20+minutes
  [4]:http://www.jeopardy.com/
  [5]:http://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx#naming_conventions
  [6]:https://github.com/whymarrh/jeopardy-parser/blob/master/parser.py#L25
