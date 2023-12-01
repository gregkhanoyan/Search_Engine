from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
import linecache   
import math
from numpy import dot
import json
import time
import tkinter
import os


# processes all the words inside uniqueWords.txt and get their IDs(its position in its respective inverted_index.txt)
# spliting with tuple because each line in uniqueWords.txt will have "Word, Line # in inverted_index"
# store tuples in word dict, convert line # from string to int
words = {}
with open("uniqueWords.txt", encoding="utf8", errors='ignore') as writeLines:
    for line in writeLines.readlines():
        word, line = tuple(line.split())
        words[word] = int(line)


# read entire docs.txt
# eval transforms the entire docs.txt into a list of dicts
# gets total number of docs(json pages)
with open("docs.txt") as docTxt:
    line = docTxt.readline()
    docList = eval(line)
docsTotal = len(docList)


LETTERS = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}


# creat a GUI for search engine using tkiner library
# displays top 10 URLs along with the time it takes to process the query 
def gui():
    root = tkinter.Tk()
    root.title("Search Engine")
    
    label = tkinter.Label(root, text = 'Enter Query')
    label.grid(pady = 10, row =0)

    results = tkinter.Label(root, text = "")
    results.grid(pady = 10, row =3)

    searchBox = tkinter.Entry(root, width = 40, borderwidth = 3)
    searchBox.grid(pady = 10, row =1)

    def output():
        results.config(text = "")
        input = searchBox.get()
        output = printURLs(input)
        results.config(text = output)

    tkinter.Button(root, text = 'Enter', command = output).grid(pady = 10, row =2)

    root.mainloop()


# calls search function to search the result
# the timer is started before search and ends after getQuerySearch because that is where we do our main search
# ranked gives us the doc IDs from docs.txt and topTen gives us the json URLs of those doc IDs from docs.txt
# find the json URLs in DEV folder and add their web URLs to the outputStr
# we wrap everything in a try/except to make sure a query exist in indexes
# returns the resulting 10 urls or NO RESULTS FOUND
def printURLs(query):
    os.system('cls')
    outputStr = ''
    try:
        start = time.time()
        ranked = search(query)
        stop = time.time()
        count = 0
        topTen = []
        outputStr += "Results: \n"

        with open("docs.txt") as printPage:
            fileContent = eval(printPage.read())
            for key in ranked:
                if count == 10:
                    break
                topTen.append(fileContent[key].get('url'))
                count += 1

        for i in range(0, 10):
            with open("developer/DEV/" + topTen[i], "r") as file:
                outputStr += json.load(file)["url"] + '\n'

        outputStr += str(stop - start) + " seconds\n"        
    except:
        outputStr += "NO RESULTS FOUND\n"

    print(outputStr)
    return outputStr


# retrieve relevant documents and rank them based in query 
# tokenize and stem query using NLTK
# queryVector splits stemmed words and its frequency within search query
# retrieves docs that terms appear in and the term freq in those docs
# caculates the TF-IDF value for term in each doc and store all that in dict of lists, table(matrix)-like format
# uses cosine similarity to rank those docs, calculated bewtween query vector (freq) and each doc's TF-IDF vector
# ranked results stored in dict, KEY: doc ID and Value: similarity score
# sorted in decending order, highest similarity to lowest similarity
# Cited Source: GeeksForGeeks, used for cosine similarity and sort for rankings
def search(query):
    tokenizedQ = word_tokenize(query.lower())

    porter = PorterStemmer()
    stemmedQ = [porter.stem(token) for token in tokenizedQ]

    terms, freq = queryVector(stemmedQ)

    tokens = [getIndex(term) for term in terms]

    vectors = tfidf_matrix(terms, tokens)

    ranked = {page: dot(freq, vectors[page])/norm(freq)*norm(vectors[page]) for page in vectors}

    ranked = dict(sorted(ranked.items(), key=lambda item: item[1], reverse = True)) 

    return ranked


# converts query to vector based on term freq
# convert query into set to remove duplicates terms then back into a list
# wordFreq counts the frequency of a word in the query, non-stemmed
# returns
#   queryList: list of all unique tokens from the query
#   wordFreq: frequecy of each token in query
def queryVector(query):
    queryList = list(set(query))
    wordFreq = [0 for _ in queryList]
    for term in query:
        if term in query: 
            wordFreq[queryList.index(term)] += 1
        else: 
            wordFreq[queryList.index(term)] = 1
    return queryList, wordFreq


# check if stemmed words are in words dict
# raise valueError, make sure only indexed words are processed
# letter is set to the first letter of each stemmed word, empty = special chars  letter = cooresponding inverted_index
# linecache.getline gets the line from the respective inverted_index file
# words[stemmed] = line number of word in inverted_index
# retrieved line is a string, use eval() to eval back to dictionary
# stemmedDict maps doc ID to their term frequencies
# retrieves the index from its respective inverted_index file
def getIndex(stemmed):
    if stemmed not in words: 
        raise ValueError

    if stemmed[0] not in LETTERS:
        letter = ""
    else: 
        letter = stemmed[0]

    stemmedDict = linecache.getline("indexes/inverted_index" + letter + ".txt", words[stemmed])
    return eval(stemmedDict)


# vector stores doc ID and list of TFIDF scores for each term in each document
# df is the number of docs that contain the current term
# creates a table for each document that is being considered for the results 
# ex: 50111 : [1.12312, 1.4322], where 50111 is the doc ID, 1.12312 is the TFIDF value of the first token, 1.4322 is the TFIDF value of the second token
# df is document frequency : number of docs that contatin the term
# if doc contains term, calcTFIDF
# if doc doesn't contain term, TFIDF is 0
# best stores doc ID and mean TFIDF score of all the terms
# best is sorted in decending order from highest to lowest mean TFIDF score
# if the total of docs is more than 40 docs, considers only 1/4 of the docs in tokens, else consider them all
# max docs we will consider is 500
# return dict with KEY: doc ID VALUE: TFIDF value
def tfidf_matrix(terms, tokens):
    vector = {}
    for i in range(len(terms)):
        df = len(tokens[i][terms[i]])
        for document in tokens[i][terms[i]]:
            if document in vector and document in tokens[i][terms[i]]:
                vector[document][i] = calcTFIDF(tokens[i][terms[i]][document], df)
            else: 
                vector[document] = [0 for _ in terms]   
                if document in tokens[i][terms[i]]:
                    vector[document][i] = calcTFIDF(tokens[i][terms[i]][document], df)

    best = {doc: mean((vector[doc])) for doc in vector}
    best = sorted(best, key=lambda x: -best[x])

    if math.floor(len(best) / 4) >= 10: 
        extract = math.floor(len(best) / 4) 
        if extract > 500:
            extract = 500 
    else: 
        extract = len(best)

    best = best[0:extract + 1]
    return {doc: vector[doc] for doc in best} 


# normalizes a vector
# every vector element squared and added to normed
# used for cosine similarity
def norm(vector):
    normed = 0
    for i in range(0,len(vector)):
        normed += vector[i] ** 2
    return normed


# calculates tf-idf value
# TF-IDF = term frequency * log(total docs / docs containing term)
# used for TFIDF matrix
def calcTFIDF(tf, df):
    return tf * math.log(docsTotal/ df)


# caculate the mean
# used for TFIDF matrix
def mean(vector):
    mean = 0
    for i in range(0,len(vector)):
        mean += vector[i]
    return mean/len(vector)


# MAIN
gui()
