# autoglosser

Contact Jonathan Fascetti (jlfascetti@gmail.com) with any questions.

Clone the repository:
  Create a new directory to house all files for this app. Be sure not to name it "autoglosser".
  In terminal, go to the desired directory and run:
    $ git clone https://github.com/jonathanfascetti/autoglosser
  A new directory should be created with the contents of the more recent repository from the web.

Repo contents:
  This README file
  index.html
    to be run in browser 
  test.log
    logging file from most recent time autogloss.py was run
  start_webserver_python.py
    python script needed for web browser
    IMPORTANT: after cloning the repo, this file MUST be moved out of the autoglosser directory one level. It should be at the same level as the cloned autoglosser local repo.
  /other_drafts
    old files that are no longer needed, but are kept for record
  /cgi-bin
    /__pycache__
      can be ingored, but kept
    /storyboard
      houses two .tsv files with example sentences that have been used to test the program
    test.log
      logging file for script
    glossary.csv
      glossary contents pulled from https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw
    glossaryrules.csv
      glossary rules pulled from https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw (DIFFERENT TAB THAN glossary.csv)
    glossaryGlobals.py
      helper python file that autogloss.py calls each time -- used to make sure the main autogloss.py file is not too messy
      If this program is to be adapted for another glossary, most of the changes should be in this script, not autogloss.py
    autogloss.py
      main python file that takes in sentence input (either from terminal or through web interface) and outputs a gloss based off of glossary.csv. The file can handle ambiguity and some (but not all) variations in input syntax.

Run application:
  There are two main ways to run the program: through terminal or through the web interface.
  In terminal:
    In terminal and once you are in /autoglosser, use the folling command to navigate to the proper directory
      $ cd cgi-bin 
    Then, run the script using the following command:
      $ python autogloss.py "[INPUT TEXT]"
    Where [INPUT TEXT] is whatever word(s) or phrase you want to be glossed.
    For example:
      $ python autogloss.py "A Robert, A Bill nẽ John nonga a Mari wuusgo"
    With this example input, there should prompty be an output with the original input text, the normalized spelling and gloss, then LaTeX spelling and gloss
    Depending on the input words, the output may return that there is ambiguity.
    Use the -a flag (described in "Additional termina flags") to get your desired output.
  In web interface:
    In terminal, navigate to one level above the newley added /autoglosser repo.
    Be sure that the file start_webserver_python.py has been moved one level outside autoglosser.py
    Run the command 
      $ python start_webserver_python.py
    Terminal should enter a flow and should not return with a normal $ prompt. Do not exit this terminal window until you are done using the web interface.]
    In a new browser tab (tested with Safari and Chrome), enter "localhost:9000" into the navigation bar (not Google search) and hit return.
    You should see a simple HTML site with a text box and submit button.
    You can paste input words or a phrase into the box (make sure to minimize white space and exess characters) and use the submit button to see results.
    If there is ambiguity in the input words, you will be prompted to choose options which update the gloss

Additional terminal flags:
  -u
    If you would like to update the local .csv files for the glossary and rules, appened the flag -u to your script call.
    A series of output lines will be pushed and then the input phrase will be analyzed.
  -a
    Use -a when there is ambiguity in the input words or phrase.
    As described in the output when needed, use the -a flag followed by the idexes of how you want to handle the ambiguity. 
    The words that are ambiguous can be seen in the gloss sentence where all the options are seperated by slashes.
    For example, appending the following to your terminal call will choose the first input word to be the second ambiguous option and the third input word to be the first ambiguous option:
      -a 0:1/2:0
    Note that these indicies are indexed at zero and include all (even non-ambiguous) input words -- so count carefully!


Packages used:
  It's possible that you will need to install some packages for the program to be able to run. 
  The packages used in this softare are:
    cgi
    cgitb
    os
    json
    subprocess
    csv
    argparse
    logging
    sys
    datetime
  If any one these packages are not installed on your local machine, you will need to use pip (or some other package installer) to use them. 
  For pip, most of these packages can be installed using the following command in any terminal directory:
    $ pip install [PACKAGE NAME]
  If that command doesn't work, there is likely thorough documentation online about how to install the package.

Trouble shooting:
  Make sure the structure of the files (with the exception of start_webserver_python.py) is consistent with how it is on https://github.com/jonathanfascetti/autoglosser
  Review files for no changed filepaths which could inturrupt flow of program.
  Check for excess characters in the input phrase.
  Check test.log files for possible crash explinations.
  Check out the console if running with the web interface.
  Reach out to Jonathan Fascetti (jlfascetti@gmail.com).

