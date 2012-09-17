## J! Archive Parser

`parser.py` extracts the Jeopardy! clues from the [J! Archive][1] website.

## Set-up

Clone the repo: `git clone git://github.com/whymarrh/parser.git` and `cd parser`.  
Make sure that the download script is executable: `chmod +x download.sh`.  
Run the download script (`./download.sh`) to get all the pages.  
Run the parser (`python parser.py`) and sit back ... this may take a bit of time.  

The running time of the parsing script (i.e. `(time python parser.py) 2>&1 | grep real`) should not be more than ~20 minutes on a decent machine. Even that is a lot, I know, but there are **a lot** of clues to go through.

  [1]: http://j-archive.com/