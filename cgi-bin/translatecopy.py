#!/usr/bin/env python3
# coding: utf-8

"""
TO DO: -- this script
    first parse words in cell, and check for question
    handle two word cells


    Make function to split cell into words seperated by commas (like ColN,Row44)
    work with '...'
    items that are two words in the glossary (ex row 43) {!Maybe fixed by three above?!}
    recognize moore vs english vs latex {!maybe solvable by labeling colomns!}
    ###SPELLCHECK###
TO DO: -- in general
    Create list of types of glosses
    Save search results into log file from site

"""


"""
RUN SCRIPT
Make sure relavent glossary .csv file is in the same directory as this script. When calling, the arguments should be in single quotes. All moore input should be preceeded by -m with a space between each word (inlc -m) Ex: ~ python3 translate.py '-m -(w)ã ãnd(ã) b'

RETIREVE DATA FROM glossary
glossary is a list where each element is a tuple. All of the elements are parallel tuples where index 0 is blank, 1 is "Word in Mòoré (high tones marked)", etc. (following rules below). glossary[n][m] can be used where n is to access a certain moore word, and m is the category.

"""

import cgi
import cgitb
import os
import json

import argparse, logging, csv, sys
from datetime import datetime
from glossaryGlobals import (
    commaParse,
    GLOSSARY,
    MOOREWORD,
    MORPH,
    LATEXSPL,
    POS,
    FLEXSPL,
    RECORDING,
    GLOSS,
    LATEXGLOSS,
    SILSPL,
    SILTONAL,
    SILSLNK,
    ENGMEAN,
    SPLVAR,
    TEOSPL,
    SRCPGN,
    QSTNS,
    EXPLS,
    KAYE,
)

logger = logging.getLogger(os.path.basename(__file__))
fh = logging.FileHandler("test.log", mode="w")
formatter = logging.Formatter(
    "%(lineno)d --> %(levelname)s --> %(name)s:%(message)s"
)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)
logger.critical("Starting " + __file__)


# TO FIND WHICH ROW IN GLOSSARY INPUT WORD IS
def wordToKey(word):
    word = word.lower()
    keys = []
    for i in [
        MOOREWORD,
        SPLVAR,
        MORPH,
        FLEXSPL,
        SILSPL,
    ]:
        for j in range(len(GLOSSARY)):  # run through each row
            if "," in GLOSSARY[j][i]:
                logger.info("Found ',' in " + str(GLOSSARY[j][i]))
                # if there are multiple phrases within the cell
                GLOSSARY[j][i] = commaParse(GLOSSARY[j][i])
                # parse them into a list
                for k in GLOSSARY[j][i]:
                    # check each sub element for a match
                    if word == k:
                        keys.append(matchFound(word, j, i, "moore"))
                        # return matchFound(word, j, i, "moore")
                # break
            elif type(GLOSSARY[j][i]) == list:
                for k in GLOSSARY[j][i]:
                    # check each sub element for a match
                    if word == k:
                        keys.append(matchFound(word, j, i, "moore"))
                        # return matchFound(word, j, i, "moore")
                # break
            else:
                # if only one word in cell, check for match
                if word == GLOSSARY[j][i]:  # if 1:1 match
                    # print(matchFound(word, j, i, "moore"))
                    keys.append(matchFound(word, j, i, "moore"))
                    # return matchFound(word, j, i, "moore")
                # break

    # trim duplicates of same row matches (found in diff cols)
    for i in range(len(keys)):
        for j in range(len(keys)):
            try:
                if keys[i][0] == keys[j][0] and keys[i][1] != keys[j][1]:
                    keys.pop(j)
            except IndexError:
                pass

    return keys


# LOGGING STUFF FOR WHEN MATCHES ARE FOUND
def matchFound(word, row, col, givenLang):
    key = row
    givenCat = col
    logger.info(
        " "
        + str(datetime.now().time())
        + " ~~> Match found: "
        + str(word)
        + " -> row #"
        + str(row)
    )
    logger.info(
        " "
        + str(datetime.now().time())
        + " ~~> Moore: '"
        + str(GLOSSARY[row][MOOREWORD])
        + "', Gloss: '"
        + str(GLOSSARY[row][GLOSS])
        + "', English: '"
        + str(GLOSSARY[row][ENGMEAN])
        + "'."
    )
    return (key, givenCat, givenLang)


# FIND THE FINAL GLOSS
def findGloss(keys):
    gloss = []
    logger.debug(keys)
    for i in keys:
        if type(i[0][0]) == int:
            if GLOSSARY[i[0][0]][GLOSS] != "":
                gloss.append(GLOSSARY[i[0][0]][GLOSS])
            else:
                gloss.append("?")
        elif i[0][0] == None:
            gloss.append("NEG")
        else:
            gloss.append("?")

    return gloss


# FIND THE FINAL LATEX GLOSS
def findLGloss(keys):
    latexgloss = []
    for i in keys:
        if type(i[0][0]) == int:
            if GLOSSARY[i[0][0]][LATEXGLOSS] != "":
                latexgloss.append(GLOSSARY[i[0][0]][LATEXGLOSS])
            else:
                latexgloss.append("?")
        elif i[0][0] == None:
            latexgloss.append("\\neg{}")
        else:
            latexgloss.append("?")

    return latexgloss


# FIND LATEX SPELLING
def findLSpl(keys):
    latexSpl = []
    for i in keys:
        if type(i[0][0]) == int:
            if GLOSSARY[i[0][0]][LATEXSPL] != "":
                latexSpl.append(GLOSSARY[i[0][0]][LATEXSPL])
            else:
                latexSpl.append("?")
        else:
            latexSpl.append("?")

    return latexSpl


# FIND NORMSPL
def findNormspl(keys):
    normSpl = []
    for i in keys:
        if type(i[0][0]) == int:
            if GLOSSARY[i[0][0]][MOOREWORD] != "":
                normSpl.append(GLOSSARY[i[0][0]][MOOREWORD])
            else:
                normSpl.append("?")
        else:
            normSpl.append("?")
    return normSpl


# DO THE FINAL PRINTOUT
def resultsDict(givenWords, keys, gloss, latexGloss, latexSpl, normSpl):
    for i in range(len(givenWords)):
        logger.info(
            "["
            + str(givenWords[i])
            + ", "
            + str(gloss[i])
            + ", "
            + str(latexGloss[i])
            + ", "
            + str(normSpl[i])
            + "]"
        )

    givenWords = " ".join(givenWords)
    normSpl = " ".join(normSpl)
    gloss = " ".join(gloss)
    latexSpl = " ".join(latexSpl)
    latexGloss = " ".join(latexGloss)

    results = {}
    results["moore"] = givenWords
    results["normSpl"] = normSpl
    results["gloss"] = gloss
    results["latexSpelling"] = latexSpl
    results["latexGloss"] = latexGloss
    return results


def checkForKaYe(keys):
    for i in range(len(keys)):
        try:
            if GLOSSARY[keys[i]][MOOREWORD] == "ká":
                for j in range(len(keys)):
                    if GLOSSARY[keys[j]][MOOREWORD] == "yé":
                        logger.info(
                            " "
                            + str(datetime.now().time())
                            + " Found ká...yé."
                        )
                        for k in range(len(GLOSSARY)):
                            if KAYE in GLOSSARY[k]:
                                keys[i] = k
                                keys[j] = None
                        return keys
        except TypeError:
            pass
    return keys


def checkForMultiTranslate(keys):
    return keys


def main(args):
    ###
    # check for if more than one word in cell (nested list)
    # append to each keys, givenCat, and givenLang
    # logger
    # questionmark for no matches
    # only look for 1:1 match
    ###
    lofkeys = []
    # list where each element is a list where each element is a tuple of a match found

    for i in moore:
        lofkeys.append(wordToKey(i))

    for i in range(len(lofkeys)):
        if lofkeys[i] == []:
            lofkeys[i] = ["?", "?", "?"]

    # sys.exit()

    # see if there is a ká...yé
    for word in lofkeys:
        for key in word:
            keys = checkForKaYe(key)

    logger.debug("keys --> " + str(lofkeys))

    gloss = findGloss(lofkeys)

    latexGloss = findLGloss(lofkeys)

    latexSpl = findLSpl(lofkeys)

    normSpl = findNormspl(lofkeys)

    # finalPrintout(moore, keys, givenCat, givenLang, gloss, latexGloss)
    rd = resultsDict(moore, keys, gloss, latexGloss, latexSpl, normSpl)

    ###
    ## PUT COMMAND LINE PRINT STATEMENTS HERE
    ##
    ###

    # Start JSON block
    if "GATEWAY_INTERFACE" in os.environ:
        print("Content-type: application/json")
        print("")
        print(json.JSONEncoder().encode(rd))
    else:
        print(
            "Original: \n \t %s \n Normalized Spelling + Gloss: \n \t %s \n \t %s \n LaTex Spelling + Gloss: \n \t %s \n \t %s \n"
            % (
                rd["moore"],
                rd["normSpl"],
                rd["gloss"],
                rd["latexSpelling"],
                rd["latexGloss"],
            )
        )

    # end of function, return to main flow control
    ################
    # sys.exit()


if __name__ == "__main__":

    moore = None  # declare

    if "GATEWAY_INTERFACE" in os.environ:  # WEB EXECUTION
        form = cgi.FieldStorage()
        logger.debug(form)

        if "moore" in cgi.FieldStorage():
            moore = form.getvalue("moore")
            logger.debug(moore)
            moore = moore.split(" ")

    else:  # COMMAND LINE EXECUTION
        # split arguments given at start into words in a list under variable moore
        parser = argparse.ArgumentParser(
            description="Translate from Mòore to English"
        )
        parser.add_argument(
            type=str, nargs="+", help="Input text.", dest="moore"
        )

        args = parser.parse_args()
        logger.info(
            " "
            + str(datetime.now().time())
            + " ~~> Arguments: "
            + str(vars(args))
        )
        moore = args.moore

        # if clumped together in one element
        if " " in moore[0]:
            moore = moore[0].split()

        # string period and quotes
        if moore[0][0] == "'" or moore[0][0] == '"':
            moore[0] = moore[0][1:]
        for i in range(2):
            if (
                moore[-1][-1] == "."
                or moore[-1][-1] == "'"
                or moore[-1][-1] == '"'
            ):
                moore[-1] = moore[-1][:-1]
            logger.debug(
                " " + str(datetime.now().time()) + ": Trimmed the input."
            )

    logger.info(" " + str(datetime.now().time()) + " ~~> Moore: ")
    logger.info(moore)

    main(moore)

    logger.info(
        " " + str(datetime.now().time()) + " ~~> Sucessfully executed."
    )
