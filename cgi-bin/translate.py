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


def createAlpha():
    ###source file used for creating alphabet (copy and pasted MOOREWORD from main glossary w/o ka...ye)
    dictfilepath = os.path.dirname(__file__)
    dictfilename = dictfilepath + "/" + "dictionary.txt"
    with open(os.path.join(dictfilename)) as file:
        data = file.readlines()

    for i in range(len(data)):
        if "\n" in data[i]:
            data[i] = data[i][:-1]

    alphabet = []
    for i in data:
        for j in i:
            if j not in alphabet:
                alphabet.append(j)

    return alphabet


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
                    print(matchFound(word, j, i, "moore"))
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


# TO PARSE CELLS THAT HAVE COMMAS INTO LISTS
def commaParse(inputPhrase):
    if "," in inputPhrase:
        parsedPhrase = inputPhrase.split(", ")
    return parsedPhrase


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


# GENERATE POSSIBLE WORDS
def possibleWordGen(word, singeOrDouble):
    def singleLetterSwitch():
        if len(word) >= 3:  # only if the word is longer than two letters
            logger.debug(
                " Running through single letter switches in "
                + str(word)
                + "."
            )
            for i in range(len(word)):
                # through each letter in given word
                for j in ALPHABET:  # through each letter in moore alphabet
                    tempWord = ""  # create tempword
                    if i == 0:
                        # if it's the beginning of the word...
                        tempWord = j + word[1:]
                        # the tempword should be the alphabet letter plus the given word minus first letter
                        possibleWords.append(tempWord)
                        # add to possible words list
                    elif i == len(word):
                        # if it's the end of the word...
                        tempWord = word[:-1] + j
                        # the temp word should be the while given word minue the last letter which is replaced by the given alphabet letter
                        possibleWords.append(tempWord)
                        # add to possible words list
                    else:
                        # if working through the middle of the word...
                        tempWord = word[:i] + j + word[i + 1 :]
                        # the temp word should be the given word up till given letter, exchanged with given alphabet letter, then the rest of the given word
                        possibleWords.append(tempWord)
                        # add to possible words list

    def doubleLetterSwitch():
        if len(word) > 4:
            logger.debug(
                " Running through double letter switches in "
                + str(word)
                + "."
            )
            for i in range(len(word)):
                for k in range(len(word)):
                    # through each letter in given word again
                    if i == k:
                        # if i and k are the same, skip
                        # print("broke")
                        pass
                    else:
                        # print(" i -->", i)
                        # print("k -->", k)
                        for j in ALPHABET:
                            # through each letter in moore alphabet
                            for l in ALPHABET:
                                # through each letter in moore alphabet again
                                if i == 0:
                                    if k != len(word) - 1:
                                        logger.debug("i first and k mid")
                                        # iFirstKMid(i, j, k, l)
                                        firstMid(i, j, k, l)
                                elif i == len(word) - 1:
                                    if k != 0:
                                        logger.debug("i end and k mid")
                                        # iEndKMid(i, j, k, l)
                                        endMid(i, j, k, l)
                                elif k == 0:
                                    if i != len(word) - 1:
                                        logger.debug("k first and i mid")
                                        # kFirstIMid(i, j, k, l)
                                        firstMid(k, j, i, l)
                                elif k == len(word) - 1:
                                    if i != 0:
                                        logger.debug("k end and i mid")
                                        # kEndIMid(i, j, k, l)
                                        endMid(k, j, i, l)
                                else:
                                    if i > k:
                                        # logger.debug("i mid before k mid")
                                        # iMidKMid(i, j, k, l)
                                        midMid(i, j, k, l)
                                    else:
                                        # logger.debug("k mid before i mid")
                                        # kMidIMid(i, j, k, l)
                                        midMid(k, j, i, l)

    def firstMid(i, j, k, l):
        # logger.debug("firstMid")
        # if i is the beginning of the word and k is somewhere in the middle...
        tempWord = j + word[1:k] + l + word[k + 1 :]
        # the tempword should be the alphabet letter plus the given word minus first letter with the middle letter switched out
        possibleWords.append(tempWord)
        ##~~and do it again with j and l switched
        # add to possible words list
        tempWord = l + word[1:k] + j + word[k + 1 :]
        # the tempword should be the alphabet letter plus the given word minus first letter
        possibleWords.append(tempWord)
        # add to possible words list

    def endMid(i, j, k, l):
        # logger.debug("endMid")
        # if i is the end of the word and k is not in the beginning...
        tempWord = word[:k] + j + word[k + 1 : -1] + l
        # the temp word should be the while given word minue the last letter which is replaced by the given alphabet letter with middle letter switched out
        possibleWords.append(tempWord)
        # add to possible words list
        ##~~and do it again with j and l switched
        tempWord = word[:k] + l + word[k + 1 : -1] + j
        # the temp word should be the while given word minue the last letter which is replaced by the given alphabet letter with middle letter switched out
        possibleWords.append(tempWord)
        # add to possible words list

    def midMid(i, j, k, l):
        if i + 1 == k or k + 1 == i:
            # print("side by side")
            # if working through the middle of the word and i is less than k...
            tempWord = word[:i] + j + l + word[k + 1 :]
            # the temp word should be the given word up till given letter, exchanged with given alphabet letter, then the rest of the given word two times
            possibleWords.append(tempWord)
            # add to possible words list
            ##~~and again with j and l switched
            # if working through the middle of the word...
            tempWord = word[:i] + l + j + word[k + 1 :]
            # the temp word should be the given word up till given letter, exchanged with given alphabet letter, then the rest of the given word two times
            possibleWords.append(tempWord)
            # add to possible words list
        else:
            # print("not side by side")
            # if working through the middle of the word and i is less than k...
            tempWord = word[:i] + j + word[i + 1 : k] + l + word[k + 1 :]
            # the temp word should be the given word up till given letter, exchanged with given alphabet letter, then the rest of the given word two times
            possibleWords.append(tempWord)
            # add to possible words list
            ##~~and again with j and l switched
            # if working through the middle of the word...
            tempWord = word[:i] + l + word[i + 1 : k] + j + word[k + 1 :]
            # the temp word should be the given word up till given letter, exchanged with given alphabet letter, then the rest of the given word two times
            possibleWords.append(tempWord)
            # add to possible words list

    """
    OLD DOUBLE LETTER SWITCH FUNCTIONS 
    def iFirstKMid(i, j, k, l):
        logger.debug("iFirstKMid")
        # if i is the beginning of the word and k is somewhere in the middle...
        tempWord = j + word[1:k] + l + word[k + 1 :]
        # the tempword should be the alphabet letter plus the given word minus first letter with the middle letter switched out
        possibleWords.append(tempWord)
        ##~~and do it again with j and l switched
        # add to possible words list
        tempWord = l + word[1:k] + j + word[k + 1 :]
        # the tempword should be the alphabet letter plus the given word minus first letter
        possibleWords.append(tempWord)
        # add to possible words list

    def iEndKMid(i, j, k, l):
        logger.debug("iEndKMid")
        # if i is the end of the word and k is not in the beginning...
        tempWord = word[:k] + j + word[k + 1 : -1] + l
        # the temp word should be the while given word minue the last letter which is replaced by the given alphabet letter with middle letter switched out
        possibleWords.append(tempWord)
        # add to possible words list
        ##~~and do it again with j and l switched
        tempWord = word[:k] + l + word[k + 1 : -1] + j
        # the temp word should be the while given word minue the last letter which is replaced by the given alphabet letter with middle letter switched out
        possibleWords.append(tempWord)
        # add to possible words list

    def kFirstIMid(i, j, k, l):
        logger.debug("kFirstIMid")
        i, j, k, l
        # if i is the beginning of the word and k is somewhere in the middle...
        tempWord = j + word[1:i] + l + word[i + 1 :]
        # the tempword should be the alphabet letter plus the given word minus first letter with the middle letter switched out
        possibleWords.append(tempWord)
        ##~~and do it again with j and l switched
        # add to possible words list
        tempWord = l + word[1:i] + j + word[i + 1 :]
        # the tempword should be the alphabet letter plus the given word minus first letter
        possibleWords.append(tempWord)
        # add to possible words list

    def kEndIMid(i, j, k, l):
        logger.debug("kEndIMid")
        # if i is the end of the word and k is not in the beginning...
        tempWord = word[:i] + j + word[i + 1 : -1] + l
        # the temp word should be the while given word minue the last letter which is replaced by the given alphabet letter with middle letter switched out
        possibleWords.append(tempWord)
        # add to possible words list
        ##~~and do it again with j and l switched
        tempWord = word[:i] + l + word[i + 1 : -1] + j
        # the temp word should be the while given word minue the last letter which is replaced by the given alphabet letter with middle letter switched out
        possibleWords.append(tempWord)
        # add to possible words list

    def iMidKMid(i, j, k, l):
        logger.debug("iMidKMid")
        # if working through the middle of the word and i is less than k...
        tempWord = word[:i] + j + word[i + 1 : k] + l + word[k + 1 :]
        # the temp word should be the given word up till given letter, exchanged with given alphabet letter, then the rest of the given word two times
        possibleWords.append(tempWord)
        # add to possible words list
        ##~~and again with j and l switched
        # if working through the middle of the word...
        tempWord = word[:i] + l + word[i + 1 : k] + j + word[k + 1 :]
        # the temp word should be the given word up till given letter, exchanged with given alphabet letter, then the rest of the given word two times
        possibleWords.append(tempWord)
        # add to possible words list

    def kMidIMid(i, j, k, l):
        logger.debug("kMidIMid")
        # if working through the middle of the word and k is less than i...
        tempWord = word[:k] + j + word[k + 1 : i] + l + word[i + 1 :]
        # the temp word should be the given word up till given letter, exchanged with given alphabet letter, then the rest of the given word two times
        possibleWords.append(tempWord)
        # add to possible words list
        ##~~and again with j and l switched
        # if working through the middle of the word...
        tempWord = word[:k] + l + word[k + 1 : i] + j + word[i + 1 :]
        # the temp word should be the given word up till given letter, exchanged with given alphabet letter, then the rest of the given word two times
        possibleWords.append(tempWord)
        # add to possible words list
    """

    # load alphabet
    ALPHABET = createAlpha()
    possibleWords = []

    if singeOrDouble == "single":
        singleLetterSwitch()  # first create single letter switches
    else:
        doubleLetterSwitch()  # then create double letter switches

    # delete repeats
    possibleWords = set(possibleWords)

    return possibleWords


# FIND THE FINAL GLOSS
def findGloss(keys):
    gloss = []
    logger.debug(keys)
    for i in keys:
        if type(i) == int:
            if GLOSSARY[i][GLOSS] != "":
                gloss.append(GLOSSARY[i][GLOSS])
            else:
                gloss.append("?")
        elif i == None:
            gloss.append("NEG")
        else:
            gloss.append("?")

    return gloss


# FIND THE FINAL LATEX GLOSS
def findLGloss(keys):
    latexgloss = []
    for i in keys:
        if type(i) == int:
            if GLOSSARY[i][LATEXGLOSS] != "":
                latexgloss.append(GLOSSARY[i][LATEXGLOSS])
            else:
                latexgloss.append("?")
        elif i == None:
            latexgloss.append("\\neg{}")
        else:
            latexgloss.append("?")

    return latexgloss


# FIND LATEX SPELLING
def findLSpl(keys):
    latexSpl = []
    for i in keys:
        if type(i) == int:
            if GLOSSARY[i][LATEXSPL] != "":
                latexSpl.append(GLOSSARY[i][LATEXSPL])
            else:
                latexSpl.append("?")
        else:
            latexSpl.append("?")

    return latexSpl


# DO THE FINAL PRINTOUT
def resultsDict(
    givenWords, keys, givenCat, givenLang, gloss, latexGloss, latexSpl
):

    for i in range(len(givenWords)):
        logger.info(
            "["
            + str(givenWords[i])
            + ", "
            + str(gloss[i])
            + ", "
            + str(latexGloss[i])
            + "]"
        )

    givenWords = " ".join(givenWords)
    gloss = " ".join(gloss)
    latexSpl = " ".join(latexSpl)
    latexGloss = " ".join(latexGloss)

    results = {}
    results["moore"] = givenWords
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


def main(args):

    keys = []  # index of row in GLOSSARY for each given word
    givenCat = []  # to be list of which colomn for each given word
    givenLang = []  # given langauge
    altSplChck = (
        []
    )  # num of alt translations per given word that has gone through spell check
    for i in moore:
        try:
            returns = wordToKey(i)
            if type(returns) == list:
                for j in returns:
                    keys.append(j[0])
                    givenCat.append(j[1])
                    givenLang.append(j[2])
                    altSplChck.append(0)
            else:
                keys.append(returns[0])
                givenCat.append(returns[1])
                givenLang.append(returns[2])
                altSplChck.append(0)
        except TypeError:
            logger.info(
                " "
                + str(datetime.now().time())
                + " ~~> No results found for '"
                + str(i)
                + "'. Checking for possible word misspells."
            )
            possibleWords = possibleWordGen(i, "single")
            results = []
            altSplChckCount = 0
            for j in possibleWords:
                returns = wordToKey(j)
                if returns != None:
                    if type(returns) == list:
                        for k in returns:
                            altSplChckCount += 1
                            keys.append(k[0])
                            givenCat.append(k[1])
                            givenLang.append(k[2])
                            logger.debug(
                                " "
                                + str(datetime.now().time())
                                + " ~~> Possible match found. Input word: '"
                                + str(i)
                                + "'. Detected match: '"
                                + str(j + "'.")
                            )
                            results.append(k)
                    else:
                        altSplChckCount += 1
                        keys.append(returns[0])
                        givenCat.append(returns[1])
                        givenLang.append(returns[2])
                        logger.debug(
                            " "
                            + str(datetime.now().time())
                            + " ~~> Possible match found. Input word: '"
                            + str(i)
                            + "'. Detected match: '"
                            + str(j + "'.")
                        )
                        results.append(returns)
            altSplChck.append(altSplChckCount)

            if len(results) == 0:
                keys.append("?")
                givenCat.append("?")
                givenLang.append("?")
                altSplChck.append("0")

    ## this is where question determaining and cell-word parsing should happen ## change to do this when loading csv?
    for i in keys:

        if type(i) == int:
            if "," in GLOSSARY[i][ENGMEAN]:
                GLOSSARY[i][ENGMEAN] = commaParse(GLOSSARY[i][ENGMEAN])
            if "p." in GLOSSARY[i][ENGMEAN]:
                # if ends in something like "Peterson 1971 p. 139"
                pass

    # see if there is a ká...yé
    print(keys)
    keys = checkForKaYe(keys)
    print(keys)

    # check the respective langauges detected are the same within the input words
    if len(givenLang) > 0:
        for i in givenLang:
            for j in givenLang:
                if i != "?" and j != "?":
                    if i != j:
                        logger.critical(
                            " "
                            + str(datetime.now().time())
                            + " ~~> Inconsistant language inputs detected!"
                        )
                        sys.exit(
                            "Error: inconsistant language inputs detected"
                        )
        givenLang = givenLang[0]

    logger.debug("keys --> " + str(keys))
    logger.debug("givenCat --> " + str(givenCat))
    logger.debug("givenLang --> " + str(givenLang))

    gloss = findGloss(keys)

    latexGloss = findLGloss(keys)

    latexSpl = findLSpl(keys)

    # finalPrintout(moore, keys, givenCat, givenLang, gloss, latexGloss)
    rd = resultsDict(
        moore, keys, givenCat, givenLang, gloss, latexGloss, latexSpl
    )

    ###
    ## PUT COMMAND LINE PRINT STATEMENTS HERE
    ##
    ###

    # Start JSON block
    if "GATEWAY_INTERFACE" in os.environ:
        print("Content-type: application/json")
        print("")

    print(json.JSONEncoder().encode(rd))
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
