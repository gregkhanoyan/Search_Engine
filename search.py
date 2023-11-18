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
# spliting with tuple because each line in uniqueWords.txt will have "Word ID"
words = {}
with open("uniqueWords.txt", encoding="utf8", errors='ignore') as writeLines:
    for line in writeLines.readlines():
        word, line = tuple(line.split())
        words[word] = int(line)


# gets total number of docs(json pages)
# eval transforms the entire docs.txt into a list
with open("docs.txt") as doc_id_txt:
    line = doc_id_txt.readline()
    doc_ids = eval(line)
totalDocs = len(doc_ids)


LETTERS = {"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}


# check if stemmed words are in uniqueWords
# letter is set to the first letter of each word in stemmed
# words[stemmed] = line number of word in inverted_index
# linecache.getline gets the line from the respective inverted_index file
# retrieves the index from its respective inverted_index file
def retrieveIndex(stemmed):
    if stemmed not in words: 
        raise ValueError

    if stemmed[0] not in LETTERS:
        letter = ""
    else: 
        letter = stemmed[0]

    dictOfStemmed = linecache.getline("indexes/inverted_index" + letter + ".txt", words[stemmed])
    return eval(dictOfStemmed)


# converts query to vector 
# returns
#   query_list: list of all unique tokens from the query
#   vect_q: frequecy of each token
def queryToVector(query):
    query_list = list(set(query))
    vect_q = [0 for _ in query_list]
    for term in query:
        if term in query: 
            vect_q[query_list.index(term)] += 1
        else: 
            vect_q[query_list.index(term)] = 1
    return query_list, vect_q


# calculates tf-idf value
# TFIDF = term frequency * log(total docs / docs containing term)
def calculate_TFIDF(tf, df):
    return tf * math.log(totalDocs/ df)


# caculate the mean
def mean(vector):
    mean = 0
    for i in range(0,len(vector)):
        mean += vector[i]
    return mean/len(vector)


# vector stores doc ID and list of TFIDF scores for each term in document
# df is the number of docs that contain the current term
# creates a table for each document that is being considered for the results 
# ex: 50111 : [1.12312, 1.4322], where 50111 is the doc ID, 1.12312 is the TFIDF value of the first token, 1.4322 is the TFIDF value of the second token
# df is document frequency : number of docs that contatin the term
# if doc contains term, calculate_TFIDF
# if doc doesn't contain term, TFIDF is 0
# best stores doc ID and average TFIDF score of all the terms
# best is sorted in decending order from highest to lowest avg TFIDF score
# if the total of docs is more than roughly 40 docs, considers only 1/4 of the docs in tokens
# if total of docs more than 500, considers only 500
def tfidf_matrix(terms, tokens):
    vector = {}
    for i in range(len(terms)):
        df = len(tokens[i][terms[i]])
        for document in tokens[i][terms[i]]:
            if document in vector and document in tokens[i][terms[i]]:
                vector[document][i] = calculate_TFIDF(tokens[i][terms[i]][document], df)
            else: 
                vector[document] = [0 for _ in terms]   
                if document in tokens[i][terms[i]]:
                    vector[document][i] = calculate_TFIDF(tokens[i][terms[i]][document], df)

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


# normilizes a vector
# iterate over vector
# every vector element squared and added to normed
def normalize(vector):
    normed = 0
    for i in range(0,len(vector)):
        normed += vector[i] ** 2
    return normed


# tokenizes query
# stems query
# converts query to a vector
# retrieves docs that relevant to the query
# caculates the TFIDF value for each docs and store all that in dict of list, table(matrix)-like format
# uses cosine similarity to rank those docs
def getQueryAndSearch(query):
    tokenized_query = word_tokenize(query.lower())

    porter = PorterStemmer()
    stemmed_list = [porter.stem(token) for token in tokenized_query]

    terms, vect_q = queryToVector(stemmed_list)

    tokens = [retrieveIndex(term) for term in terms]

    vectors = tfidf_matrix(terms, tokens)

    ranked = {page: dot(vect_q, vectors[page])/normalize(vect_q)*normalize(vectors[page]) for page in vectors}

    ranked = dict(sorted(ranked.items(), key=lambda item: item[1], reverse = True)) 

    return ranked


# calls getQueryAndSearch function to search the result
# the timer is started before getQueryAndSearch and ends after getQuerySearch because that is where we do our main search
# based on the doc IDs returned, we get their respective JSON names in docs.txt, then get their URLs in DEV 
# we wrap everything in a try/except to make sure a query exist in indexes
# returns the resulting 10 urls or NO RESULTS FOUND
def printURLs_gui(query):
    os.system('cls')
    output_str = ''
    try:
        start = time.time()
        ranked = getQueryAndSearch(query)
        stop = time.time()
        count = 0
        topTen = []
        output_str += "Results: \n"

        with open("docs.txt") as printPage:
            file_content = eval(printPage.read())
            for key in ranked:
                if count == 10:
                    break
                topTen.append(file_content[key].get('url'))
                count += 1

        for i in range(0, 10):
            with open("developer/DEV/" + topTen[i], "r") as file:
                output_str += json.load(file)["url"] + '\n'

        output_str += str(stop - start) + " seconds\n"        
    except:
        output_str += "NO RESULTS FOUND\n"

    print(output_str)
    return output_str


# builds a gui by using tkiner library
# displays top 10 URLs along with the time it takes to process the query 
def gui():
    root = tkinter.Tk()
    root.title("Assignment 3")
    
    label = tkinter.Label(root, text = 'Enter Query')
    label.grid(pady = 10, row =0)

    label2 = tkinter.Label(root, text = "")
    label2.grid(pady = 10, row =3)

    query = tkinter.Entry(root, width = 40, borderwidth = 3)
    query.grid(pady = 10, row =1)

    def output():
        label2.config(text = "")
        input_string = query.get()
        out_string = printURLs_gui(input_string)
        label2.config(text = out_string)

    tkinter.Button(root, text = 'Enter', command = output).grid(pady = 10, row =2)

    root.mainloop()

gui()