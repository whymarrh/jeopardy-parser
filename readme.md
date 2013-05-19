# What is this

This, `parser.py`, is a script to extract [Jeopardy!][4] clues from the [J! Archive][1] website and dump them into a SQLite database for use elsewhere. No particular application is intended, but a fair number of clues are skipped over when parsing, and any application requiring the complete set of clues will not find it here.

To test the database, `test.py` outputs a single random clue from each of 10 random games. Manually comparing these clues to the J! Archive website is a way to verify that the clues are being matched to the proper category, game, etc.

Python 2.7.2 and SQLite 3.7.12 are tested.

# The initial download

The download script does not mirror the entire site, it simply gets the game pages. Also note that no media files are downloaded (e.g. pictures or audio files) and the parser does not account for media clues. The complete download of the pages (at the time of writing) is approx. 295M, and can take up to 6.5 hours [(1s per page, plus a 5s wait between downloads, 3970 times)][2].

(Note that [Windows does not allow `?` characters in its filenames][5]. The downloaded files will be renamed to replace `?` with `_` and this will require a small modification of the parser on [line 25][6].)

# Getting started

1. Clone the repo: `git clone git://github.com/whymarrh/jeopardy-parser.git`
2. `cd jeopardy-parser`
3. `chmod +x build.sh`
4. Run `./build.sh` and wait

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

    SELECT clues.id, clues.game, airdate, round, value, category, clue, answer
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
  [4]:http://www.jeopardy.com/
  [5]:http://msdn.microsoft.com/en-us/library/windows/desktop/aa365247(v=vs.85).aspx#naming_conventions
  [6]:https://github.com/whymarrh/jeopardy-parser/blob/master/parser.py#L25
