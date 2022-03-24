#!/usr/bin/env python3
# coding: utf-8


import os
import subprocess
import argparse, logging, sys
import pandas as pd
import numpy as np
from datetime import datetime
from assets.glossary.glossaryGlobals import (
    commaParse,
    GLOSSARY,
    ORIGWORD,
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
        ORIGWORD,
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
                        keys.append(matchFound(word, j, i, "inputword"))
            elif type(GLOSSARY[j][i]) == list:
                for k in GLOSSARY[j][i]:
                    # check each sub element for a match
                    if word == k:
                        keys.append(matchFound(word, j, i, "inputword"))
            else:
                # if only one word in cell, check for match
                if word == GLOSSARY[j][i]:  # if 1:1 match
                    keys.append(matchFound(word, j, i, "inputword"))

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
        + " ~~> inputword: '"
        + str(GLOSSARY[row][ORIGWORD])
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
                normSpl = append(ORIGWORD, normSpl, j)
        else:
            normSpl = append(ORIGWORD, normSpl, i)
    return normSpl


# PREPARE DICT FOR THE FINAL PRINTOUT
def standardResults(
    theInput,
    gloss,
    latexGloss,
    latexSpl,
    normSpl,
    amb,
    rules,
    glossary
):
    # apply rules
    if max(amb) > 0:
        # Temp fix for website to read
        if (rules.empty):
            rules = pd.read_csv("../assets/glossary/glossaryrules.csv")
            glossary = pd.read_csv("../assets/glossary/glossary.csv")
        
        ambiguousWords = rules['ambiguous wordform'].values
        possibleWords = glossary['Wordform in Mòoré (high tones marked)'].values

        # Lowercase the names
        nameIndexes = np.where(glossary['POS'] == 'name')[0]
        for i in nameIndexes:
            possibleWords[i] = possibleWords[i].lower()

        for wordIndex in range(len(amb)):
            # check if there is a rule to apply
            rulesIndex = np.where(ambiguousWords == theInput[wordIndex])[0]

            if amb[wordIndex] != 0 and len(rulesIndex) > 0:
                rule = rules.loc[rulesIndex[0], :]

                if rule['in position ("preceding" or "succeeding")'] == "preceding":
                    # check if rule applies
                    if wordIndex == len(amb) - 1:
                        continue
                    
                    # Find row of next word
                    nextWord = theInput[wordIndex + 1]
                    nextWordIndex = np.where(possibleWords == nextWord)[0]
                    if (len(nextWordIndex) == 0):
                        continue
                    nextWordIndex = nextWordIndex[0]

                    # check if next word's feature column match value
                    feature = rule['feature']
                    value = rule['value']

                    if (glossary[feature].values[nextWordIndex] != value):
                        continue

                    # replace ambigious word with row that has use value in Gloss column
                    for amb_option in range(amb[wordIndex]):
                        if (gloss[amb_option + wordIndex] == rule['use value']):
                            for certainList in [
                                gloss,
                                latexGloss,
                                latexSpl,
                                normSpl,
                            ]:
                                # choose the correct option
                                certainList[wordIndex] = certainList[wordIndex + amb_option]
                                
                                # remove old options
                                for k in range(amb[wordIndex] - 1):
                                    certainList.pop(wordIndex + 1)

                            amb[wordIndex] = 0
                            break
            

                if rule['in position ("preceding" or "succeeding")'] == "succeeding":
                    # Find row of next word
                    nextWord = theInput[wordIndex - 1]
                    nextWordIndex = np.where(possibleWords == nextWord)[0]
                    if (len(nextWordIndex) == 0):
                        continue
                    nextWordIndex = nextWordIndex[0]

                    # check if next word's feature column match value
                    feature = rule['feature']
                    value = rule['value']

                    if (glossary[feature].values[nextWordIndex] != value):
                        continue

                    # replace ambigious word with row that has use value in Gloss column
                    for amb_option in range(amb[wordIndex]):
                        if (gloss[amb_option + wordIndex] == rule['use value']):
                            for certainList in [
                                gloss,
                                latexGloss,
                                latexSpl,
                                normSpl,
                            ]:
                                # choose the correct option
                                certainList[wordIndex] = certainList[wordIndex + amb_option]
                                
                                # remove old options
                                for k in range(amb[wordIndex] - 1):
                                    certainList.pop(wordIndex + 1)

                            amb[wordIndex] = 0
                            break

            # apply generic values
            if amb[wordIndex] != 0:
                logger.info(
                    " "
                    + str(datetime.now().time())
                    + " ~~> Found " + str(amb[wordIndex]) + " ambiguity at : "
                    + str(wordIndex)
                )

                # make changes to each of the certainLists
                for certainList in [
                    gloss,
                    latexGloss,
                    latexSpl,
                    normSpl,
                ]:
                    # combine all possible options into one
                    certainList[wordIndex] = "/".join(
                        np.unique(certainList[wordIndex : wordIndex + amb[wordIndex]])
                    )
                    
                    # remove old options
                    for k in range(amb[wordIndex] - 1):
                        certainList.pop(wordIndex + 1)                  

    # Log all matches to word
    for i in range(len(theInput)):
        logger.info(
            " Per word output: ["
            + str(theInput[i])
            + ", "
            + str(gloss[i])
            + ", "
            + str(latexGloss[i])
            + ", "
            + str(normSpl[i])
            + "]"
        )

    # put the lists in the dictionary with respective keys
    results = {}
    results["inputword"] = " ".join(theInput)
    results["normSpl"] = " ".join(normSpl)
    results["gloss"] = " ".join(gloss)
    results["latexSpelling"] = " ".join(latexSpl)
    results["latexGloss"] = " ".join(latexGloss)

    return results

# this function will only be called if the -a flag is used
def ambig(lofkeys, ambOptions, amb):
    # check to make sure whatever ambiguity preferences there are are valid
    for ambOption in ambOptions:
        input_index, ambiguity_option = ambOption[0], ambOption[1]

        if input_index < 0 or input_index >= len(lofkeys) or ambiguity_option < 0 or ambiguity_option >= len(lofkeys[input_index]):
            ambOptionStr = "[" + ", ".join([str(elem) for elem in ambOption]) + "]"
            logger.critical(
                " Ambiguity input index error. %s is out of bounds.",
                ambOptionStr,
            )
            sys.exit(
                "\n\nExiting with error...\n\tAmbiguity input index error. "
                + ambOptionStr
                + " is out of bounds.\n\n"
            )

    # set values
    for ambOption in ambOptions:
        input_index, ambiguity_option = ambOption[0], ambOption[1]

        # Set key to amb word
        lofkeys[input_index] = [lofkeys[input_index][ambiguity_option]]
        # Set number of amb to 0
        amb[input_index] = 0

    # Select default values if no ambiguity option selected for those words
    is_amb = False
    for input_index in range(len(lofkeys)):
        key = lofkeys[input_index]

        # set ambiguious term to default
        if type(key) != tuple:
            # lofkeys[input_index] = key[0]

            # set ambiguious term to default
            if len(key) > 1:
                logger.warning(" Ambiguity still exists after user input.")
                is_amb = True

    is_amb = False
    return lofkeys, is_amb, amb


# code to update glossary (should only run when -u flag is included in program call)
def updateGlossary():
    logger.info("Running updateGlossary()")
    subprocess.run(
        [
            "wget",
            "--no-check-certificate",
            "--output-document=assets/glossary/glossary.csv",
            "https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw/export?gid=260382663&format=csv",
        ]
    )
    subprocess.run(
        [
            "wget",
            "--no-check-certificate",
            "--output-document=assets/glossary/glossaryrules.csv",
            "https://docs.google.com/spreadsheets/d/1hht0h0BP-TeO_RHx07RF0UjK2VX-tcRU47bQ9FKS8Cw/export?gid=210327120&format=csv",
        ]
    )


# Convert Glossary Rules to DateFrame
def readGlossaryRules():
    try:
        with open("assets/glossary/glossaryrules.csv") as file:
            return pd.read_csv("assets/glossary/glossaryrules.csv")
    except FileNotFoundError:
        logger.debug(
            "assets/glossary/glossaryrules.csv not found."
        )

    return pd.DataFrame()

# Convert Glossary to DateFrame
def readGlossary():
    try:
        with open("assets/glossary/glossary.csv") as file:
            return pd.read_csv("assets/glossary/glossary.csv")
    except FileNotFoundError:
        logger.debug(
            "assets/glossary/glossary.csv not found."
        )

    return pd.DataFrame()

# DO THE FINAL PRINTOUT
def finalPrintout(givenLang, givenWords, normalSpelling, gloss, latexSpelling, latexGloss):
    print("\n~~~\n")
    print(
        "Original (in "
        + str(givenLang)
        + "):\n\n"
        + " ".join(givenWords)
    )

    print("\n~~~\n")
    print("Normalized spelling + Gloss:\n")
    print(" ".join(normalSpelling))
    print(" ".join(gloss))
    print("\n~~~\n")
    print("LaTeX Gloss: \n\n\exg. " + " ".join(latexSpelling)   + "\\\\\n" + " ".join(latexGloss) + "\\\\")
    print("%Original spelling: " + " ".join(givenWords) + "\n")
    print("\n~~~\n")

    # logging
    for i in range(len(givenWords)):
        logging.info(
            "["
            + str(givenWords[i])
            + ", "
            + str(gloss[i])
            + ", "
            + str(latexSpelling[i])
            + ", "
            + str(latexGloss[i])
            + "]"
        )

# DO THE STANDARD PRINTOUT
def standardPrintout(givenWords, normalSpelling, gloss, latexSpelling, latexGloss):
    percent = "%"
    print(
        "\nFinal output. \n Original: \n \t %s \n\n Normalized Spelling + Gloss: \n \t %s \n \t %s \n\n LaTex Spelling + Gloss: \n \t \\exg. %s\\\\ \n \t %s\\\\ \n \t %sOriginal spelling: %s \n\n"
        % (
            givenWords,
            normalSpelling,
            gloss,
            latexSpelling,
            latexGloss,
            percent,
            givenWords,
        )
    )

def main(args, ambOptions, glossaryUpdate):
    logger.info("Main")

    # if glossaryUpdate is True, update the files
    if glossaryUpdate == True:
        updateGlossary()
        logger.info("Updated glossary and rules")
        logger.debug(args)

    # if the user indicated they want to designate an ambiguity option
    if ambOptions:
        logger.info("AmbOptions argument input found: %s", ambOptions)
        # convert to list
        ambOptionsStr = ambOptions.strip()

        # organize list to be grouped in [[#:#], [#:#] ...]
        ambOptions = [[int(elem.split(":")[0]), int(elem.split(":")[1])] for elem in ambOptionsStr.split("/")]

    # list where each element is a list where each element is a tuple of a match found
    lofkeys = []
    # list where each element is the number of ambigous options found per given word
    amb = []

    theInput = args

    # Match the input
    for i in theInput:
        # find the row number for each of the given rows
        lofkeys.append(wordToKey(i))
        # if more than one possible row is found, make ambiguity True
        if len(lofkeys[-1]) > 1:  # ambiguity is true
            amb.append(len(lofkeys[-1]))
        else:
            amb.append(0)

    # Match anything that was unmatched
    for i in range(len(lofkeys)):
        if lofkeys[i] == []:
            lofkeys[i] = ["?", "?", "?"]

    is_amb = None
    # if there are values of ambiguity found
    if max(amb) > 0:
        is_amb = True
        logger.info(
            " "
            + str(datetime.now().time())
            + " ~~> Ambiguity found: "
            + str(amb)
        )

        # Apply Ambiguity Options Handler
        if ambOptions:
            lofkeys, is_amb, amb = ambig(lofkeys, ambOptions, amb)

    else:
        is_amb = False
        logger.info(
            " " + str(datetime.now().time()) + " ~~> No ambiguity found"
        )

    # find the final lists for all of the different outputs
    gloss = findGloss(lofkeys)

    latexGloss = findLGloss(lofkeys)

    latexSpl = findLSpl(lofkeys)

    normSpl = findNormspl(lofkeys)

    rules = readGlossaryRules()

    glossary = readGlossary()


    # orangize lists and put into a dictionary
    rd = standardResults(
        theInput,
        gloss,
        latexGloss,
        latexSpl,
        normSpl,
        amb,
        rules,
        glossary
    )

    # Print to terminal - command line
    # finalPrintout("moore", rd["inputword"], rd["normSpl"], rd["gloss"], rd["latexSpelling"], rd["latexGloss"])
    print(amb) # For website to know where abiguity is
    standardPrintout(rd["inputword"], rd["normSpl"], rd["gloss"], rd["latexSpelling"], rd["latexGloss"])


if __name__ == "__main__":

    inputword = None  # declare

    # Handle arguments
    # split arguments given at start into words in a list under variable inputword
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

    # List of punctuations to remove
    punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~ '''

    theInput = theInput[0].split(" ")

    # Removing punctuations in string
    for word_index in range(len(theInput)):
        word = theInput[word_index]

        for char in word:
            if char in punc:
                word = word.replace(char, "")
        
        theInput[word_index] = word.lower()

    # Remove empty strings
    theInput = [i for i in theInput if i]

    logger.info("Refined input")
    logger.info(theInput)

    # run main()
    main(theInput, args.ambOptions, args.glossaryUpdate)

    logger.info(
        " " + str(datetime.now().time()) + " ~~> Sucessfully executed."
    )