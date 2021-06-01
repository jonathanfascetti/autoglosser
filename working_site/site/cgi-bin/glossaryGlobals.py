#!/usr/bin/env python3
# coding: utf-8


import os
import csv
import logging
from datetime import datetime

gg_logger = logging.getLogger(os.path.basename(__file__))
fh = logging.FileHandler("test.log", mode="a")
formatter = logging.Formatter(
    "%(lineno)d --> %(levelname)s --> %(name)s:%(message)s"
)
fh.setFormatter(formatter)
gg_logger.addHandler(fh)
gg_logger.setLevel(logging.INFO)  ## logging level
gg_logger.critical("Starting " + __file__)


# TO PARSE CELLS THAT HAVE COMMAS INTO LISTS
def commaParse(inputPhrase):
    if "," in inputPhrase:
        parsedPhrase = inputPhrase.split(", ")
    return parsedPhrase


# get glossary info and store in list of tuples (described at the top)
filepath = os.path.dirname(__file__)
filename = filepath + "/" + "mooreglossary.csv"
with open(os.path.join(filename)) as f:
    glossaryTemp = [tuple(line) for line in csv.reader(f)]

GLOSSARY = []
for i in range(len(glossaryTemp)):
    glossaryTemp[i] = list(glossaryTemp[i])
    glossaryTemp[i].pop(0)  # first element is not needed for our set up
    glossaryTemp[i] = list(glossaryTemp[i])
    if i == 0:  # skip headder line
        HEADDER = glossaryTemp[i][:]
    else:
        GLOSSARY.append(glossaryTemp[i])

###
MOOREWORD = HEADDER.index("Wordform in Mòoré (high tones marked)")
MORPH = HEADDER.index("Morph. breakdown (high tones marked)")
LATEXSPL = HEADDER.index("LaTex Spelling (with breakdown)")
POS = HEADDER.index("POS (webonary categories)")
FLEXSPL = HEADDER.index("FLEX Spelling")
RECORDING = HEADDER.index("Recording")
GLOSS = HEADDER.index("Gloss")
LATEXGLOSS = HEADDER.index("Latex Gloss")
SILSPL = HEADDER.index("SIL spelling")
SILTONAL = HEADDER.index("Tonal Pattern in SIL")
SILSLNK = HEADDER.index("Link of SIL Spelling")
ENGMEAN = HEADDER.index("Translation / Meaning")
SPLVAR = HEADDER.index("Spelling variants")
TEOSPL = HEADDER.index("Teo/Pacchiaroti spelling")
SRCPGN = HEADDER.index("Source(s) & Page #")
QSTNS = HEADDER.index("Questions")
EXPLS = HEADDER.index("Examples/Notes")

# parse cells in SPLVAR, ENGMEAN, GLOSS that have commas into sub-lists
for i in GLOSSARY:  # by row
    for j in [SPLVAR, ENGMEAN, GLOSS]:
        if "," in i[j]:
            i[j] = commaParse(i[j])
gg_logger.debug(
    " "
    + str(datetime.now().time())
    + " ~~> Parsed cells in SPLVAR, ENGMEAN, and GLOSS that have commas into sub-lists."
)

# check for a question mark in some cells
## for future version, spesify which col the question mark is in -- might be useful for webside implementation
questions = []
for i in range(len(GLOSSARY)):  # by row
    for j in [
        MOOREWORD,
        GLOSS,
        SILSPL,
        ENGMEAN,
        SPLVAR,
    ]:  # selected cols
        if type(GLOSSARY[i][j]) == str:  # if already a string
            if (
                "?" in GLOSSARY[i][j] and "https" not in GLOSSARY[i][j]
            ):  # if there is a ? and not a website link
                questions.append([i, j])  # append row and col
        elif type(GLOSSARY[i][j]) == list:  # if a list
            for k in GLOSSARY[i][j]:  # go through each element
                if (
                    "?" in k and "https" not in k
                ):  # if there is a ? and not a website link
                    questions.append([i, j])  # append row and col

# replace second item with global var names
HEADDERLIST = [
    "MOOREWORD",
    "MORPH",
    "LATEXSPL",
    "RECORDING",
    "GLOSS",
    "LATEXGLOSS",
    "POS",
    "SPLVAR",
    "TEOSPL",
    "SILSLNK",
    "SILTONAL",
    "FLEXSPL",
    "RECORDING",
    "ENGMEAN",
    "SRCPGN",
    "QSTNS",
    "EXPLS",
]
for i in questions:
    i[1] = HEADDERLIST[
        i[1]
    ]  # get second element and replace from int to str

gg_logger.critical("Exiting " + __file__)
