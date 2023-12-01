from simhash import Simhash, SimhashIndex 
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import json
import os
import math
import ast

LETTERS = {"", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}

# set of unique tokens
uniqueWords = set()
# list of indexed docs
docs = []
# uses simhash to detect duplicate files
hashed = SimhashIndex([], k=1)
# inverted index dictonary
invertedIndex = {}


# runs processDevFolder()
# write indexed docs into docs.txt
def indexer():
    processDevFolder()
    os.chdir('../..')
    with open("docs.txt", "w") as f:
        f.write(str(docs))


# processes all DEV subfolders given to us
# os.chdir("./developer/DEV"): path to DEV
# os.listdir(os.getcwd()) gives us a list of all subfolder inside DEV
# processes each folder by calling processDevJsons
# write partial index to a file as a record to make sure not overflow the memeory in case DEV is too large
# if invertedIndex exceeds 100000 elements, write the element to a new partial index file
def processDevFolder():
    os.chdir("./developer/DEV")

    count = 1
    for file in os.listdir(os.getcwd()):
        if os.path.isdir(file):
            processDevJsons(file)

        if len(invertedIndex) > 100000:
            loadPartialIndex(count)
            count += 1

    if len(invertedIndex) > 0: 
        loadPartialIndex(count)


# writes current invertedIndex to partial_index file and clears the current invertedIndex
# this is to make sure that we don't overflow memory with large invertedIndex
# encoding 'utf-8' : handle Unicode characters
def loadPartialIndex(partialIndexNumber: int):
    with open("../../indexes/partial_index" + str(partialIndexNumber) + ".txt", "w", encoding='utf-8') as file:
        file.write(str(invertedIndex))
    invertedIndex.clear()


# processes all json files in DEV subfolder
# changes directory to go into current sub folder of DEV
# os.listdir(os.getcwd()) gives us all the files inside the current directory
# adds json file to docs
# each docs element is a dict containing 2 keys: json url and content
# uses simhash to detect exact and near duplicate files, if file is duplicate skip the file
# gets tfs of text from processText()
# adds tokens into invertedIndex
    # if token is already in invertedIndex -> update its tf value
        # otherwise create it
# each word in invertedIndex holds: word, tf, docID
# returns to the previous directory
def processDevJsons(str):
    os.chdir(os.getcwd() + "/" + str)
    print("\nPROCESSING: " + str)

    for jsonFile in os.listdir(os.getcwd()):
        id = len(docs)
        docs.append({'id': id, 'url': str + '/' + jsonFile})
        text = parseJson(jsonFile)
        hashedText = Simhash(text)

        if len(hashed.get_near_dups(hashedText)) == 0:
            hashed.add(jsonFile, hashedText)
            tfDict = processText(text)

            for word in tfDict:
                uniqueWords.add(word)
                if word in invertedIndex: 
                    invertedIndex[word][id] = tfDict[word]
                else: 
                    invertedIndex[word] = {id: tfDict[word]}
    os.chdir('..')


# gets file from json
# file content is a json obj with key 'content' holding HTML data
# uses beautiful soup to parse the HTML content 
# removes script and style tags
# sets an identifier for text within important tags
# returns docContent string including text from file
def parseJson(path):
    print("\tPROCESSING: " + path)
    docContent = ""

    try:
        with open(path, "r") as f: 
            file = json.load(f)
        soup = BeautifulSoup(file["content"], "html.parser")
        for tag in soup.find_all(['script', 'style']):
            tag.extract()

        importantTags = ['b', 'strong', 'h1', 'h2', 'h3']
        for tag in soup.find_all():
            tagName = tag.name.lower()

            if tagName in importantTags:
                docContent += 'STRONGTAG' + tag.get_text()
            else:
                docContent += tag.get_text()

        # docContent = soup.get_text()  # this is basic get_text(), take all words with equal weight

    except:
        print(f"Error reading file {path}")

    return docContent 


# returns a dict, KEYS are the TOKENS from the doc and VALUES are their TF VALUES
# tokenizes the given string(doc content) using NLTK word_tokenize
# stems all the tokens using NLTK PorterStemmer
# calculates the tf values for each stemmed word
# words marked as 'strongtag' are important words that will be assigned a higher weight
# 'strongtag' is removed from the word to not affect indexing
# use math.log to smooth out high frequency word counts, +1 so there are only non-zero values
# math.log is done so that common words are not dominant
def processText(text):
    text = word_tokenize(text.lower())
    porter = PorterStemmer()
    stemmedWords = [porter.stem(word) for word in text]

    tf = {}
    for word in stemmedWords:
        if word in tf:
            if "strongtag" in word:
                word = word.replace("strongtag", "")
                tf[word] += 2
            else:
                tf[word] += 1
        else: 
            if "strongtag" in word:
                word = word.replace("strongtag", "")
                tf[word] = 2
            else:
                tf[word] = 1

    for word in tf: 
        tf[word] = math.log(tf[word]) + 1
    return tf


# spilts the partial_index files into 27 inverted_index files: 26 for letters and 1 for special characters
# this helps organize the index so it's more efficient for retrieval and reduces the memory during the search
# create a list of paths to all partial_index files
# create a dict for tokens that start with the current relevant letter and another dict for special chars
# read the file and eval the content (in string format) using 'ast.literal_eval() to safely eval dicts stored in partial index
# check first char and add to 'indexDict' or 'special_indexDict'
# when token is written to inverted_index file it's also written to 'uniqueWords.txt'
# after processing each letter, 'indexDict' is cleared to free up memory before processing next letter
def splitIndexes():
    partialIndexList = []
    indexDict = {}
    special_indexDict = {}

    temp_partialIndexNumber = 1
    while(os.path.exists("indexes/partial_index" + str(temp_partialIndexNumber) + ".txt")):
        partialIndexList.append("indexes/partial_index" + str(temp_partialIndexNumber) + ".txt")
        temp_partialIndexNumber += 1

    for letter in LETTERS:
        for partialIndex in partialIndexList:
            print("READING " + letter + " from: " + partialIndex)
            with open(partialIndex, "r", encoding='utf-8') as file:
                docContent = ast.literal_eval(file.read())
                for key in docContent.keys():
                    if len(key) > 0:
                        if key[0] not in LETTERS:
                            special_indexDict[key] = docContent[key]
                        elif key[0] == letter:
                            indexDict[key] = docContent[key]

        with open("indexes/inverted_index" + letter + ".txt", "w", encoding='utf-8') as open_file:
            if letter == "":
                count = 1
                for word in special_indexDict:
                    print("{\"" + word + "\": " + str(special_indexDict[word]) + "}", file=open_file)

                    with open("uniqueWords.txt", "a", encoding='utf-8') as f:
                        print(word + " " + str(count), file=f)
                    count += 1
            else:
                count = 1
                for word in indexDict:
                    print("{\"" + word + "\": " + str(indexDict[word]) + "}", file=open_file)

                    with open("uniqueWords.txt", "a", encoding='utf-8') as f:
                        print(word + " " + str(count), file=f)
                    count += 1
        indexDict.clear()


# MAIN
indexer()
splitIndexes()

totalSize = 0
for dirpath, dirnames, filenames in os.walk('indexes'):
    for f in filenames:
        fpath = os.path.join(dirpath, f)
        if os.path.exists(fpath):
            totalSize += os.path.getsize(fpath)

print(f"Total index size on disk: {totalSize / 1024} KB")
