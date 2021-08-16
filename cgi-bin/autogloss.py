#!/usr/bin/env python3
# coding: utf-8


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

# setting up logger info
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
    # convert to lower case to avoid errors
    word = word.lower()

    # if the word ends in a comma, delete it
    if "," in word:
        word = word[:-1]

    keys = []
    # work through each of the given rows (all possible positive outcomees)
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


# helper function for finding final gloss, latex gloss, latex spelling, and normalized spelling
def append(glossaryRow, row, i):
    if type(i[0]) == int:
        if GLOSSARY[i[0]][glossaryRow] != "":
            row.append(GLOSSARY[i[0]][glossaryRow])
        else:
            row.append("?")
    elif i[0] == None:
        row.append("NEG")
    else:
        row.append("?")
    return row


# FIND THE FINAL GLOSS
def findGloss(keys):
    gloss = []
    for i in keys:
        # check if there is an unknown
        if type(i) == list and i[0] != "?":
            for j in i:
                gloss = append(GLOSS, gloss, j)
        else:
            gloss = append(GLOSS, gloss, i)

    return gloss


# FIND THE FINAL LATEX GLOSS
def findLGloss(keys):
    latexgloss = []
    for i in keys:
        if type(i) == list and i[0] != "?":
            for j in i:
                latexgloss = append(LATEXGLOSS, latexgloss, j)
        else:
            latexgloss = append(LATEXGLOSS, latexgloss, i)

    return latexgloss


# FIND LATEX SPELLING
def findLSpl(keys):
    latexSpl = []
    for i in keys:
        if type(i) == list and i[0] != "?":
            for j in i:
                latexSpl = append(LATEXSPL, latexSpl, j)
        else:
            latexSpl = append(LATEXSPL, latexSpl, i)

    return latexSpl


# FIND NORMSPL
def findNormspl(keys):
    normSpl = []
    for i in keys:
        if type(i) == list and i[0] != "?":
            for j in i:
                normSpl = append(MOOREWORD, normSpl, j)
        else:
            normSpl = append(MOOREWORD, normSpl, i)
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
    # if any ambiguity is establised by user
    if is_amb == True:
        i = 0
        # iterate through the length of givenWords
        while i < len(givenWords):
            # work through list of ambiguity preferences
            for j in range(len(amb)):
                if amb[j] != 0:
                    # make changes to each of the certainLists
                    for certainList in [
                        gloss,
                        latexGloss,
                        latexSpl,
                        normSpl,
                    ]:
                        # combine all possible options
                        certainList[i] = "/".join(
                            certainList[i : i + amb[j]]
                        )
                        # remove junk to keep list clean
                        for k in range(amb[j] - 1):
                            certainList.pop(i + 1)
                i += 1

    # if there are rules set in the CSV file (in addition to headder)
    if len(rules) > 1:
        # iterate through all rule rows...
        for i in range(len(rules)):
            # ... except headder row
            if i != 0:
                # if the first item in the row is one of the givenWords (because if not, don't bother with the rest of the rule)
                if rules[i][0] in givenWords:
                    # check to see if the second item is either "preceding" or "succeeding"
                    if rules[i][1] == "preceding":
                        # check to see if the rule applies to this situation...
                        try:
                            if (
                                GLOSSARY[
                                    keys[givenWords.index(rules[i][0]) + 1][
                                        0
                                    ][0]
                                ][POS]
                                == rules[i][3]
                            ):
                                # find which word needs to be switched
                                toSwitch = []
                                for j in range(len(givenWords)):
                                    if givenWords[j] == rules[i][0]:
                                        toSwitch.append(j)
                                # make the change in all of the lists
                                for certainList in [
                                    gloss,
                                    latexGloss,
                                    latexSpl,
                                    normSpl,
                                ]:
                                    for j in toSwitch:
                                        certainList[j] = rules[i][4]
                        except TypeError:
                            pass
                    # this is the same as the condition above, but it checks for "succeeding"...
                    elif rules[i][1] == "succeeding":
                        # ...in this condition...
                        try:
                            if (
                                GLOSSARY[
                                    keys[givenWords.index(rules[i][0]) - 1][
                                        0
                                    ][0]
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
                        except TypeError:
                            pass
        for i in gloss:
            # after rules are applied, if there is still a slash in the gloss (meaning there is ambiguity) make is_amb True
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

    old_results = {}
    old_results["moore"] = givenWords
    old_results["normSpl"] = normSpl
    old_results["gloss"] = gloss
    old_results["latexSpelling"] = latexSpl
    old_results["latexGloss"] = latexGloss
    if is_amb == True:
        old_results["ambiguity"] = "True"
    else:
        old_results["ambiguity"] = "False"

    # join all of lists into a more readable form.
    givenWords = " ".join(givenWords)
    normSpl = " ".join(normSpl)
    gloss = " ".join(gloss)
    latexSpl = " ".join(latexSpl)
    latexGloss = " ".join(latexGloss)

    # put the lists in the dictionary with respective keys
    results = {}
    results["moore"] = givenWords
    results["normSpl"] = normSpl
    results["gloss"] = gloss
    results["latexSpelling"] = latexSpl
    results["latexGloss"] = latexGloss
    if is_amb == True:
        results["ambiguity"] = "True"
    else:
        results["ambiguity"] = "False"

    return results, is_amb, old_results


# this function will only be called if the -a flag is used
def ambig(lofkeys, ambOptions):
    # check to make sure whatever ambiguity preferences there are are valid
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


# code to update glossary (should only run when -u flag is included in program call)
def updateGlossary():
    subprocess.run(
        [
            "wget",
            "--no-check-certificate",
            "--output-document=glossary.csv",
            "https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw/export?gid=260382663&format=csv",
        ]
    )
    subprocess.run(
        [
            "wget",
            "--no-check-certificate",
            "--output-document=glossaryrules.csv",
            "https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw/export?gid=210327120&format=csv",
        ]
    )


# digest the glossary rules CSV (seperate into parallel lists by row)
def analyzeGlossaryRules():
    try:
        with open("cgi-bin/glossaryrules.csv") as file:
            csv_reader = reader(file)
            # Pass reader object to list() to get a list of lists
            list_of_rows = list(csv_reader)
    except FileNotFoundError:
        with open("glossaryrules.csv") as file:
            csv_reader = reader(file)
            # Pass reader object to list() to get a list of lists
            list_of_rows = list(csv_reader)

    return list_of_rows


def main(args, ambOptions, glossaryUpdate):
    logger.info("Main")

    # if glossaryUpdate is True, update the files
    if glossaryUpdate == True:
        updateGlossary()
        logger.info("Updated glossary and rules")

    # if the user indicated they want to designate an ambiguity option
    if ambOptions:
        logger.info("AmbOptions argument input found: %s", ambOptions)
        # convert to list
        ambOptionsStr = ambOptions.strip()

        # organize list to be grouped in [[#:#], [#:#] ...]
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

    # list where each element is a list where each element is a tuple of a match found
    lofkeys = []
    # list where each element is the number of ambigous options found per given word
    amb = []

    theInput = args
    # trim periods and commas off of given words and lower case everynthing
    for i in range(len(theInput)):
        if theInput[i][-1] == "," or theInput[i][-1] == ".":
            theInput[i] = theInput[i][:-1]
        theInput[i] = theInput[i].lower()

    for i in theInput:
        # find the row number for each of the given rows
        lofkeys.append(wordToKey(i))
        # if more than one possible row is found, make ambiguity True
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

    # find the final lists for all of the different outputs
    gloss = findGloss(lofkeys)

    latexGloss = findLGloss(lofkeys)

    latexSpl = findLSpl(lofkeys)

    normSpl = findNormspl(lofkeys)

    # analyze the rules
    rules = analyzeGlossaryRules()

    # orangize lists and put into a dictionary
    rd, is_amb, old_rd = resultsDict(
        theInput,
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
        if rd["ambiguity"] == "False":
            print("Content-type: application/json")
            print("")
            print(json.JSONEncoder().encode(rd))
        else:
            print("Content-type: application/json")
            print("")
            print(json.JSONEncoder().encode(old_rd))
    # if terminal call
    else:
        percent = "%"
        # if there is no ambiguity, do this output...
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
        # ...but if there is ambiguity do this one
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

            logger.info("Refined input")

            # run main() without ambOptions or updateGlossary
            main(moore, None, None)

    else:  # COMMAND LINE EXECUTION
        # split arguments given at start into words in a list under variable moore
        parser = argparse.ArgumentParser(
            description="Translate from Mòoré to English"
        )

        # use -a then the 0:0 type syntax to set ambiguity preferences
        parser.add_argument(
            "-a",
            "--ambOptions",
            type=str,
            help='Only use this argument when the ambiguity is known. Use syntax: -a "input-word-num:ambiguity-option/input-word-num:ambiguity-option/…".',
        )

        # just include the -u flag to update the glossary and rules files before processing input
        parser.add_argument(
            "-u",
            "--glossaryUpdate",
            action="store_true",
            help="Update glossary? True for update and False/no call for no update.",
        )

        # all other text (even without a flag) will be classified under the variable args.theInput
        parser.add_argument(
            type=str, nargs="+", help="Input text.", dest="theInput"
        )

        args = parser.parse_args()

        logger.info(
            " "
            + str(datetime.now().time())
            + " ~~> Arguments: "
            + str(vars(args))
        )

        # rename variable to make a bit easier to work with
        theInput = args.theInput

        try:
            logger.info(
                " "
                + str(datetime.now().time())
                + " ~~> Ambiguity: "
                + str(args.ambOptions)
            )
        except ValueError:
            pass

        # if the input is clumped together in one element
        if " " in theInput[0]:
            theInput = theInput[0].split()

        # get rid of period and quotes to make processing easier
        if theInput[0][0] == "'" or theInput[0][0] == '"':
            theInput[0] = theInput[0][1:]
        for i in range(2):
            if (
                theInput[-1][-1] == "."
                or theInput[-1][-1] == "'"
                or theInput[-1][-1] == '"'
                or theInput[-1][-1] == "?"
            ):
                theInput[-1] = theInput[-1][:-1]
            logger.debug(
                " " + str(datetime.now().time()) + ": Trimmed the input."
            )

        logger.info("Refined input")
        logger.info(theInput)

        # run main()
        main(theInput, args.ambOptions, args.glossaryUpdate)

    logger.info(
        " " + str(datetime.now().time()) + " ~~> Sucessfully executed."
    )
