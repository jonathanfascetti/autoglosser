# Autoglosser

Contact Marco Raigoza (mraigoza@bu.edu) or Jonathan Fascetti (jlfascetti@gmail.com) with any questions.

Clone the repository (repo):

git clone https://github.com/jonathanfascetti/autoglosser.git

then in main directory, install packages with the command $ pip3 install -r requirements.txt

### How to start project:
  1. Visit https://autoglosser.herokuapp.com/

    If changes need to be made, then open the terminal in the autoglosser directory, run the commands:
      heroku login
      git push heroku main

  2. Locally run the website: 
    
    Open the terminal in the autoglosser directory, run the commands:
      cd website/frontend
      npm install --save --legacy-peer-deps (be patient, could take a while)
      npm run build
      cd ../..
      flask run

  3. Run autogloss.py:

    Open the terminal in the autoglosser directory, run the command:
      python3 autogloss.py "[INPUT TEXT]" -u -a [WORD INDEX]/[AMBIGUITY OPTION]

### Additional information on autogloss.py
  For command line interaction run:
      `python3 autogloss.py "[INPUT TEXT]"`
  Where [INPUT TEXT] is whatever word(s) or phrase you want to be glossed. Add optional flags as needed.
  For example:
    $ python3 autogloss.py "A Robert, A Bill nẽ John nonga a Mari wuusgo"
  For each input, it output with the original input text, the normalized spelling and gloss, then LaTeX spelling and gloss. Depending on the input words, the output may return that there is ambiguity with orders deliminated by a slash.

  Optional flags:

  -u
    If you would like to update the local .csv files for the glossary and rules. glossary.csv contains glossary contents pulled from https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw and
    glossaryrules.csv contains glossary rules pulled from https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw 
  
  -a
    Use when there is ambiguity in the input words or phrase.
    Depending on the word you would like to choose, use the -a flag followed by the idexes of how you want to handle the ambiguity. 
    The words that are ambiguous can be seen in the gloss sentence where all the options are seperated by slashes.
    For example, appending the following to your terminal call will choose the first input word to be the second ambiguous option and the third input word to be the first ambiguous option:
      -a 0:1/2:0
    Note that these indicies are indexed at zero and include all (even non-ambiguous) input words -- so count carefully!

### Repo overview
  * `/website`
    contains React JS code and API endpoints in order to run app.py, the flask app.
  * `test.log`
    is the logging file from most recent time autogloss.py was run.
  * `/assets`
    * `/alphabet`
      contains dictionary used to run translate-beta.py.
    * `/storyboard`
      contains two .tsv files with example sentences that have been used to test the autogloss.py.
    * `/glossary`
      contains helper files that autogloss.py calls each time -- used to make sure the main autogloss.py file is not too messy.
      If this program is to be adapted for another language's glossary, most of the changes should be in this script, not autogloss.py.
  * `autogloss.py`
    is the main python file that takes in sentence input (either from terminal or through web interface).
     The file can handle ambiguity and some (but not all) variations in input syntax.

Created by Jonathan Fascetti and Marco Raigoza overseen by Dr. Elizabeth Coppock.
