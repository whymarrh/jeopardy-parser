# What it is

`parser.py` extracts Jeopardy! clues from the [J! Archive][1] website and dumps them into a SQLite database for use elsewhere. No particular application is intended, but a fair number of clues are skipped over when parsing. Any application requiring the complete set of clues will not find it here.

# Getting started

Clone the repo: `git clone git://github.com/whymarrh/parser.git` and `cd parser`  
`chmod +x download.sh`  
`chmod +x parser.py`  
Run the download script and parser: `./download.sh && ./parser.py`)  

The "real" running time of the parsing script (i.e. `(time ./parser.py) 2>&1 | grep real`) should not be more than 30 minutes on a decent machine. I know even that is quite a lot, but there are **a lot** of clues to go through. With [FTS][2] enabled, the resulting database is sized at around 70M.

# Regarding the initial download

The download script does not mirror the entire site, it simply gets the game pages. Also note that no media files are downloaded (e.g. pictures) and the parser does not account for media clues. The complete download of the pages (at the time of writing) is approx. 295M.

  [1]: http://j-archive.com/
  [2]: http://www.sqlite.org/fts3.html