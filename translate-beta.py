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


import argparse, logging, csv, sys
from datetime import datetime

# createAlpha is another script that has a function to split the known alphamet -- needed for spell check system
import os
sys.path.append(os.path.abspath(os.path.join('assets', 'alphabet')))
import createAlpha

# set up logging info
logging.basicConfig(
    filename="test.log",
    filemode="w",
    level=logging.DEBUG,  # debug, info, warning, error, critical
    format=f"%(lineno)d --> %(levelname)s --> %(name)s:%(message)s",
)


def main():
    def addPmatches():
        if results != []:
            if len(results) == 1:
                keys.append(results[0][0])
                givenCat.append(results[0][1])
                givenLang.append(results[0][2])
            else:
                logging.info(
                    " "
                    + str(datetime.now().time())
                    + " ~~> "
                    + str(len(results))
                    + " results detected for '"
                    + str(i)
                    + "': "
                )
                for j in results:
                    logging.info(
                        " "
                        + str(datetime.now().time())
                        + " ~~> '"
                        + str(GLOSSARY[j[0]][0])
                        + "' -> "
                        + str(j)
                    )

    keys = []  # index of row in GLOSSARY for each given word
    givenCat = []  # to be list of which colomn for each given word
    givenLang = []  # given langauge
    altSplChck = (
        []
    )  # num of alt translations per given word that has gone through spell check
    for i in args.moore:
        try:
            returns = wordToKey(i)
            keys.append(returns[0])
            givenCat.append(returns[1])
            givenLang.append(returns[2])
            altSplChck.append(0)
        except TypeError:
            logging.info(
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
                    altSplChckCount += 1
                    keys.append(returns[0])
                    givenCat.append(returns[1])
                    givenLang.append(returns[2])
                    logging.debug(
                        " "
                        + str(datetime.now().time())
                        + " ~~> Possible match found. Input word: '"
                        + str(i)
                        + "'. Detected match: '"
                        + str(j + "'.")
                    )
                    results.append(returns)
            altSplChck.append(altSplChckCount)
            """ is checking for two letter switches too much?
            if len(results) == 0:
                # if no matches found for single letter switches
                logging.info(
                    " "
                    + str(datetime.now().time())
                    + " ~~> No spelling corrections found for single letter switches, checking for two. "
                )
                for i in args.moore:  ## huh -- is this right?
                    possibleWords = possibleWordGen(i, "double")
                    results = []
                    for j in possibleWords:
                        returns = wordToKey(j)
                        if returns != None:
                            logging.debug(
                                " "
                                + str(datetime.now().time())
                                + " ~~> Possible match found. Input word: '"
                                + str(i)
                                + "'. Detected match: '"
                                + str(j + "'.")
                            )
                            results.append(returns)
            """
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

    # check the respective langauges detected are the same within the input words
    if len(givenLang) > 0:
        for i in givenLang:
            for j in givenLang:
                if i != "?" and j != "?":
                    if i != j:
                        logging.critical(
                            " "
                            + str(datetime.now().time())
                            + " ~~> Inconsistant language inputs detected!"
                        )
                        sys.exit(
                            "Error: inconsistant language inputs detected"
                        )
        givenLang = givenLang[0]

    logging.debug("keys --> " + str(keys))
    logging.debug("givenCat --> " + str(givenCat))
    logging.debug("givenLang --> " + str(givenLang))

    normalSpelling = findNormalSpelling(keys)
    
    gloss = findGloss(keys)

    latexGloss = findLGloss(keys)

    latexSpelling = findLSpelling(keys)

    finalPrintout(args.moore, keys, givenCat, givenLang, normalSpelling, gloss, latexSpelling, latexGloss)


# TO FIND WHICH ROW IN GLOSSARY INPUT WORD IS
def wordToKey(word):
    word = word.lower()
    for i in [
        MOOREWORD,
        SPLVAR,
        MORPH,
        FLEXSPL,
        SILSPL,
    ]:
        for j in range(len(GLOSSARY)):  # run through each row
            if "," in GLOSSARY[j][i]:
                logging.info("Found ',' in " + str(GLOSSARY[j][i]))
                # if there are multiple phrases within the cell
                GLOSSARY[j][i] = commaParse(GLOSSARY[j][i])
                # parse them into a list
                for k in GLOSSARY[j][i]:
                    # check each sub element for a match
                    if word == k:
                        return matchFound(word, j, i, "moore")
            elif type(GLOSSARY[j][i]) == list:
                for k in GLOSSARY[j][i]:
                    # check each sub element for a match
                    if word == k:
                        return matchFound(word, j, i, "moore")
            else:
                # if only one word in cell, check for match
                if word == GLOSSARY[j][i]:  # if 1:1 match
                    return matchFound(word, j, i, "moore")


# TO PARSE CELLS THAT HAVE COMMAS INTO LISTS
def commaParse(inputPhrase):
    if "," in inputPhrase:
        parsedPhrase = inputPhrase.split(", ")
    return parsedPhrase


# LOGGING STUFF FOR WHEN MATCHES ARE FOUND
def matchFound(word, row, col, givenLang):
    key = row
    givenCat = col
    logging.info(
        " "
        + str(datetime.now().time())
        + " ~~> Match found: "
        + str(word)
        + " -> row #"
        + str(row)
    )
    logging.info(
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
            logging.debug(
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
            logging.debug(
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
                                        logging.debug("i first and k mid")
                                        # iFirstKMid(i, j, k, l)
                                        firstMid(i, j, k, l)
                                elif i == len(word) - 1:
                                    if k != 0:
                                        logging.debug("i end and k mid")
                                        # iEndKMid(i, j, k, l)
                                        endMid(i, j, k, l)
                                elif k == 0:
                                    if i != len(word) - 1:
                                        logging.debug("k first and i mid")
                                        # kFirstIMid(i, j, k, l)
                                        firstMid(k, j, i, l)
                                elif k == len(word) - 1:
                                    if i != 0:
                                        logging.debug("k end and i mid")
                                        # kEndIMid(i, j, k, l)
                                        endMid(k, j, i, l)
                                else:
                                    if i > k:
                                        # logging.debug("i mid before k mid")
                                        # iMidKMid(i, j, k, l)
                                        midMid(i, j, k, l)
                                    else:
                                        # logging.debug("k mid before i mid")
                                        # kMidIMid(i, j, k, l)
                                        midMid(k, j, i, l)

    def firstMid(i, j, k, l):
        # logging.debug("firstMid")
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
        # logging.debug("endMid")
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
        logging.debug("iFirstKMid")
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
        logging.debug("iEndKMid")
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
        logging.debug("kFirstIMid")
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
        logging.debug("kEndIMid")
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
        logging.debug("iMidKMid")
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
        logging.debug("kMidIMid")
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
    ALPHABET = createAlpha.main()
    possibleWords = []

    if singeOrDouble == "single":
        singleLetterSwitch()  # first create single letter switches
    else:
        doubleLetterSwitch()  # then create double letter switches

    # delete repeats
    possibleWords = set(possibleWords)

    return possibleWords


""" WORKING FOR ONE LETTER SWITCH
def possibleWordGen(word):
    # load alphabet
    ALPHABET = createAlpha.main()
    possibleWords = []

    if len(word) > 1: # only if the word is longer than one letter
        for i in range(len(word)):  # through each letter in given word
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
    return possibleWords
"""


# FIND THE FINAL GLOSS
def findGloss(keys):
    gloss = []
    print(keys)
    for i in keys:
        if type(i) == int:
            if GLOSSARY[i][GLOSS] != "":
                gloss.append(GLOSSARY[i][GLOSS])
            else:
                gloss.append("?")
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
        else:
            latexgloss.append("?")

    return latexgloss



# FIND THE LATEX SPELLING
def findLSpelling(keys):
    latexspelling = []
    for i in keys:
        if type(i) == int:
            if GLOSSARY[i][LATEXSPL] != "":
                latexspelling.append(GLOSSARY[i][LATEXSPL])
            else:
                latexspelling.append("?")
        else:
            latexspelling.append("?")

    return latexspelling

# FIND THE NORMAL SPELLING
def findNormalSpelling(keys):
    normalspelling = []
    for i in keys:
        if type(i) == int:
            if GLOSSARY[i][MOOREWORD] != "":
                normalspelling.append(GLOSSARY[i][MOOREWORD])
            else:
                normalspelling.append("?")
        else:
            normalspelling.append("?")

    return normalspelling


# DO THE FINAL PRINTOUT
def finalPrintout(givenWords, keys, givenCat, givenLang, normalSpelling, gloss, latexSpelling, latexGloss):
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
    """
    print(len(givenWords))
    print(len(gloss))
    print(len(latexGloss))
    """
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


if __name__ == "__main__":

    # split arguments given at start into words in a list under variable args.moore
    raw_args = None
    parser = argparse.ArgumentParser(
        description="Translate from Mòore to English"
    )
    parser.add_argument(
        "-m", "--moore", type=str, nargs="+", help="Input text."
    )
    args = parser.parse_args(raw_args)
    logging.info(
        " "
        + str(datetime.now().time())
        + " ~~> Arguments: "
        + str(vars(args))
    )

    """
    ## attempt at not needing to double \\ in arguments ... might just need to be fixed when calling function
    for i in range(len(args.moore)):
        if "\\" in args.moore[i]:
            print("check")
            args.moore[i] == args.moore[
                : args.moore[i].index("\\")
            ] + "\\" + args.moore[: args.moore[i].index("\\") + 1]
            print(args.moore[i])
    """

    # get glossary info and store in list of tuples (described at the top)
    with open("glossary.csv") as f:
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
    ###

    # parse cells in SPLVAR, ENGMEAN, GLOSS that have commas into sub-lists
    for i in GLOSSARY:  # by row
        for j in [SPLVAR, ENGMEAN, GLOSS]:
            if "," in i[j]:
                i[j] = commaParse(i[j])
    logging.info(
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
    for i in questions:
        i[1] = HEADDERLIST[
            i[1]
        ]  # get second element and replace from int to str

    main()

    logging.info(
        " " + str(datetime.now().time()) + " ~~> Sucessfully executed."
    )
