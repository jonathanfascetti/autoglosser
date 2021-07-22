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

"""
No matter whether ambiguity exists or not, the program will find the glosses of each given word and add their key values and all other needed indicatiors to paralell lists. If a certain given word has more than one corrisponding gloss (maybe from another colomn) (this indicated ambiguity), all possible glosses will be added to the lists. 
Ambiguity is kept track of in var amb which is a list. len(amb) = len(givenWords). Each index of amb indicated the number of possible glosses for the respective given word. 
Later on (in resultsDict()), var amb is used to organize the generated possible glosses into single elements of the paralell lists.
"""

import cgi
import cgitb
import os
import json
import subprocess
from csv import reader
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
    if "," in word:
        word = word[:-1]
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
                # if there are multiple phrases within the cell
                GLOSSARY[j][i] = commaParse(GLOSSARY[j][i])
                # parse them into a list
                for k in GLOSSARY[j][i]:
                    # check each sub element for a match
                    if word == k:
                        keys.append(matchFound(word, j, i, "moore"))
            elif type(GLOSSARY[j][i]) == list:
                for k in GLOSSARY[j][i]:
                    # check each sub element for a match
                    if word == k:
                        keys.append(matchFound(word, j, i, "moore"))
            else:
                # if only one word in cell, check for match
                if word == GLOSSARY[j][i]:  # if 1:1 match
                    keys.append(matchFound(word, j, i, "moore"))

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
    def append(i):
        if type(i[0]) == int:
            if GLOSSARY[i[0]][GLOSS] != "":
                gloss.append(GLOSSARY[i[0]][GLOSS])
            else:
                gloss.append("?")
        elif i[0] == None:
            gloss.append("NEG")
        else:
            gloss.append("?")
        return gloss

    gloss = []
    for i in keys:
        if type(i) == list and i[0] != "?":
            for j in i:
                append(j)
        else:
            append(i)

    return gloss


# FIND THE FINAL LATEX GLOSS
def findLGloss(keys):
    def append(i):
        if type(i[0]) == int:
            if GLOSSARY[i[0]][LATEXGLOSS] != "":
                latexgloss.append(GLOSSARY[i[0]][LATEXGLOSS])
            else:
                latexgloss.append("?")
        elif i[0] == None:
            latexgloss.append("?")
        else:
            latexgloss.append("?")
        return latexgloss

    latexgloss = []
    for i in keys:
        if type(i) == list and i[0] != "?":
            for j in i:
                append(j)
        else:
            append(i)

    return latexgloss


# FIND LATEX SPELLING
def findLSpl(keys):
    def append(i):
        if type(i[0]) == int:
            if GLOSSARY[i[0]][LATEXSPL] != "":
                latexSpl.append(GLOSSARY[i[0]][LATEXSPL])
            else:
                latexSpl.append("?")
        elif i[0] == None:
            latexSpl.append("?")
        else:
            latexSpl.append("?")
        return latexSpl

    latexSpl = []
    for i in keys:
        if type(i) == list and i[0] != "?":
            for j in i:
                append(j)
        else:
            append(i)

    return latexSpl


# FIND NORMSPL
def findNormspl(keys):
    def append(i):
        if type(i[0]) == int:
            if GLOSSARY[i[0]][MOOREWORD] != "":
                normSpl.append(GLOSSARY[i[0]][MOOREWORD])
            else:
                normSpl.append("?")
        elif i[0] == None:
            normSpl.append("?")
        else:
            normSpl.append("?")
        return normSpl

    normSpl = []
    for i in keys:
        if type(i) == list and i[0] != "?":
            for j in i:
                append(j)
        else:
            append(i)
    return normSpl


# PREPARE DICT FOR THE FINAL PRINTOUT
def resultsDict(
    givenWords,
    keys,
    gloss,
    latexGloss,
    latexSpl,
    normSpl,
    is_amb,
    amb,
    rules,
):

    if is_amb == True:
        print(givenWords)
        i = 0
        while i < len(givenWords):
            for j in range(len(amb)):
                if amb[j] != 0:
                    for certainList in [
                        gloss,
                        latexGloss,
                        latexSpl,
                        normSpl,
                    ]:

                        certainList[i] = "/".join(
                            certainList[i : i + amb[j]]
                        )
                        for k in range(amb[j] - 1):
                            certainList.pop(i + 1)
                i += 1

    if len(rules) > 1:
        # some rules exist
        for i in range(len(rules)):
            if i != 0:
                if rules[i][0] in givenWords:
                    if rules[i][1] == "preceding":
                        if (
                            GLOSSARY[
                                keys[givenWords.index(rules[i][0]) + 1][0][0]
                            ][POS]
                            == rules[i][3]
                        ):
                            toSwitch = []
                            for j in range(len(givenWords)):
                                if givenWords[j] == rules[i][0]:
                                    toSwitch.append(j)
                            for certainList in [
                                gloss,
                                latexGloss,
                                latexSpl,
                                normSpl,
                            ]:
                                for j in toSwitch:
                                    certainList[j] = rules[i][4]

                    elif rules[i][1] == "succeeding":
                        if (
                            GLOSSARY[
                                keys[givenWords.index(rules[i][0]) - 1][0][0]
                            ][POS]
                            == rules[i][3]
                        ):
                            toSwitch = []
                            for j in range(len(givenWords)):
                                if givenWords[j] == rules[i][0]:
                                    toSwitch.append(j)
                            for certainList in [
                                gloss,
                                latexGloss,
                                latexSpl,
                                normSpl,
                            ]:
                                for j in toSwitch:
                                    certainList[j] = rules[i][4]
        for i in gloss:
            if "/" in i:
                is_amb = True
                break
            else:
                is_amb = False

    for i in range(len(givenWords)):
        logger.info(
            " Per word output: ["
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

    return results, is_amb


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


def ambig(lofkeys, ambOptions):

    for i in ambOptions:
        if i[0] + 1 > len(lofkeys):
            logger.critical(
                " Ambiguity input value error. %s is greater than number of possible words.",
                i,
            )
            sys.exit(
                "\n\nExiting with error...\n\tAmbiguity input value error. "
                + str(i)
                + " is greater than number of possible words.\n\n"
            )
        try:
            lofkeys[i[0]][i[1]]
        except IndexError:
            logger.critical(
                " Ambiguity input value error. %s is greater than number of possible options.",
                i,
            )
            sys.exit(
                "\n\nExiting with error...\n\tAmbiguity input value error. "
                + str(i)
                + " is greater than number of possible options.\n\n"
            )

    # set values
    for i in ambOptions:
        lofkeys[i[0]] = lofkeys[i[0]][i[1]]

    # make sure there are no more tuples
    for i in lofkeys:
        if len(i) > 1 and type(i) != tuple:

            is_amb = True
            logger.warning(" Ambiguity still exists after user input.")
        else:
            is_amb = False

    return lofkeys, is_amb


def updateGlossary():
    subprocess.run(
        [
            "wget",
            "--no-check-certificate",
            "--output-document=mooreglossary.csv",
            "https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw/export?gid=260382663&format=csv",
        ]
    )
    subprocess.run(
        [
            "wget",
            "--no-check-certificate",
            "--output-document=mooreglossaryrules.csv",
            "https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw/export?gid=210327120&format=csv",
        ]
    )


def analyzeGlossaryRules():
    with open("mooreglossaryrules.csv") as file:
        csv_reader = reader(file)
        # Pass reader object to list() to get a list of lists
        list_of_rows = list(csv_reader)

    return list_of_rows


def main(args, ambOptions, glossaryUpdate):
    if glossaryUpdate == True:
        updateGlossary()

    # if the user indicated theyt want to designate an ambiguity option
    if ambOptions:
        logger.info(" ambOptions argument input found: %s", ambOptions)
        # convert to list
        ambOptionsStr = ambOptions.strip()

        ambOptions = []
        for i in range(len(ambOptionsStr)):
            if ambOptionsStr[i] == ":":
                try:
                    ambOptions.append(
                        [
                            int(ambOptionsStr[i - 1]),
                            int(ambOptionsStr[i + 1]),
                        ]
                    )
                except ValueError:
                    logger.critical(
                        " "
                        + str(datetime.now().time())
                        + " ~~> Invalid ambiguity option found. Expected int, recieved "
                        + str(ambOptionsStr[i - 1])
                        + " and "
                        + ambOptionsStr[i + 1]
                    )

    lofkeys = []
    ## list where each element is a list where each element is a tuple of a match found
    # list where each element is the number of ambigous options found per given word
    amb = []

    for i in moore:
        lofkeys.append(wordToKey(i))
        if len(lofkeys[-1]) > 1:  # ambiguity is true
            amb.append(len(lofkeys[-1]))
        else:
            amb.append(0)

    is_amb = None
    # if there are values of ambiguity found
    if set(amb) != {0}:
        is_amb = True
        logger.info(
            " "
            + str(datetime.now().time())
            + " ~~> Ambiguity found: "
            + str(amb)
        )
        if ambOptions:
            lofkeys, is_amb = ambig(lofkeys, ambOptions)
    else:
        is_amb = False
        logger.info(
            " " + str(datetime.now().time()) + " ~~> No ambiguity found"
        )

    for i in range(len(lofkeys)):
        if lofkeys[i] == []:
            lofkeys[i] = ["?", "?", "?"]

    gloss = findGloss(lofkeys)

    latexGloss = findLGloss(lofkeys)

    latexSpl = findLSpl(lofkeys)

    normSpl = findNormspl(lofkeys)

    rules = analyzeGlossaryRules()

    rd, is_amb = resultsDict(
        moore,
        lofkeys,
        gloss,
        latexGloss,
        latexSpl,
        normSpl,
        is_amb,
        amb,
        rules,
    )

    # Start JSON block
    if "GATEWAY_INTERFACE" in os.environ:
        print("Content-type: application/json")
        print("")
        print(json.JSONEncoder().encode(rd))
    else:
        percent = "%"
        if is_amb != True:
            print(
                "\nFinal output. \n Original: \n \t %s \n\n Normalized Spelling + Gloss: \n \t %s \n \t %s \n\n LaTex Spelling + Gloss: \n \t \\exg. %s\\\\ \n \t %s\\\\ \n \t %sOriginal spelling: %s \n\n"
                % (
                    rd["moore"],
                    rd["normSpl"],
                    rd["gloss"],
                    rd["latexSpelling"],
                    rd["latexGloss"],
                    percent,
                    rd["moore"],
                )
            )
        else:
            print(
                '\n\t\t\t~~\n\t\tAmbiguity was found.\n\t\t\t~~ \n Original: \n \t %s \n Gloss: \n \t %s \n\n Please run the program again with the same sentence and append the argument -a with the given syntax. \n\n \t\t -a "input-word-num:ambiguity-option/input-word-num:ambiguity-option/…" \n\n \t For example: -a 0:1/2:0 would mean the zeroth input word is assigned the  \n\t   first ambiguity option and the second input word is assigned the \n\t   zeroth ambiguity option. \n'
                % (
                    rd["moore"],
                    rd["gloss"],
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
            with open("out.txt") as file:
                file.write("form-->" + str(form))
                file.write("moore-->" + str(moore))

    else:  # COMMAND LINE EXECUTION
        # split arguments given at start into words in a list under variable moore
        parser = argparse.ArgumentParser(
            description="Translate from Mòoré to English"
        )

        parser.add_argument(
            "-a",
            "--ambOptions",
            type=str,
            help='Only use this argument when the ambiguity is known. Use syntax: -a "input-word-num:ambiguity-option/input-word-num:ambiguity-option/…".',
        )

        parser.add_argument(
            "-u",
            "--glossaryUpdate",
            action="store_true",
            help="Update glossary? True for update and False/no call for no update.",
        )

        parser.add_argument(
            type=str, nargs="+", help="Input text.", dest="moore"
        )

        ##Add preferences arg!!##

        args = parser.parse_args()
        logger.info(
            " "
            + str(datetime.now().time())
            + " ~~> Arguments: "
            + str(vars(args))
        )

        moore = args.moore

        try:
            logger.info(
                " "
                + str(datetime.now().time())
                + " ~~> Ambiguity: "
                + str(args.ambOptions)
            )
        except ValueError:
            pass

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
                or moore[-1][-1] == "?"
            ):
                moore[-1] = moore[-1][:-1]
            logger.debug(
                " " + str(datetime.now().time()) + ": Trimmed the input."
            )

    logger.info(" " + str(datetime.now().time()) + " ~~> Moore: ")
    logger.info(moore)

    main(moore, args.ambOptions, args.glossaryUpdate)

    logger.info(
        " " + str(datetime.now().time()) + " ~~> Sucessfully executed."
    )
