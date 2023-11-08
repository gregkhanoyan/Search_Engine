from simhash import Simhash, SimhashIndex 
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import json
import os
import math
import ast

LETTERS = {"", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"}

# keep track of unique tokens
unique_tokens = set()
# default index size on disk
index_size_on_disk = 0
# keep track of number of docs being indexed
docs = []
# uses simhash to keep track of duplicate files
hashed = SimhashIndex([], k=1)
# inverted index dict
inverted_index = {}

# returns a dict, keys are the tokens from the docs and values are their tf values
# tokenizes the given string
# stems all the words
# calculates the tf values for each word after stemming
# use math.log to smooth out high frequency numbers, +1 so there are only non-zero values
def process_text(text):
    text = word_tokenize(text.lower())
    # text = re.findall(r'\bw+\b', text.lower())

    porter = PorterStemmer()
    stemmed_list = [porter.stem(word) for word in text]

    tf = {}
    for word in stemmed_list:
        if word in tf: 
            tf[word] += 1 
        else: 
            tf[word] = 1
    for word in tf: 
        tf[word] = math.log(tf[word]) + 1
    return tf


# assign higher weight to important text
# def get_weighted_tf(soup):
#     important_tags = {'strong': 2, 'b': 2, 'h1': 3, 'h2': 2.5, 'h3': 2}
#     text = soup.get_text()
#     tf = process_text(text)
#     for tag, weight in important_tags.items():
#         for element in soup.find_all(tag):
#             important_text = element.get_text()
#             important_tf = process_text(important_text)
#             for word in important_tf:
#                 if word in tf:
#                     tf[word] += important_tf[word] * (weight - 1)  # Weighted increment
#                 else:
#                     tf[word] = important_tf[word] * weight  # New entry with weight
#     return tf

# gets file from json
# uses beautiful soup to parse the content 
# removes script and style tags
# returns the text from the file
def parse_json(path):
    print("\tPROCESSING: " + path)
    file_content = ""

    try:
        with open(path, "r") as f: 
            file = json.load(f)
        soup = BeautifulSoup(file["content"], "html.parser")
        for tag in soup.find_all(['script', 'style']):
            tag.extract()
        file_content = soup.get_text()
    except:
        print(f"Error reading file {path}")

    return file_content 

# changes directory to go into each sub folder of DEV
# os.listdir(os.getcwd()) gives us all the files inside the current directory
# each file is a dict containing 3 keys: url, content, encoding
# saves links of json files in docs
# uses simhash to detect duplicate files
# gets tfs from text
# adds tokens into inverted_index
    # if token is already in inverted_index -> update its tf value
        # otherwise save it in
# returns to the previous directory
def process_single_directory(str):
    os.chdir(os.getcwd() + "/" + str)
    print("Current directory:", os.getcwd())
    print("\nPROCESSING: " + str)

    for json_file in os.listdir(os.getcwd()):
        id = len(docs)
        docs.append({'id': id, 'url': str + '/' + json_file})

        text = parse_json(json_file)
        simhashed_words = Simhash(text)

        if len(hashed.get_near_dups(simhashed_words)) == 0:
            hashed.add(json_file, simhashed_words)
            tf_dict = process_text(text)

            for word in tf_dict:
                unique_tokens.add(word)
                if word in inverted_index: 
                    inverted_index[word][id] = tf_dict[word]
                else: 
                    inverted_index[word] = {id: tf_dict[word]}
    os.chdir('..')
    print("Current directory:", os.getcwd())

# writes partial index to a file and clears the inverted_index
# this is to make sure that we don't overflow memory with file that is too large
# makedirs : check if directory exits else create it
# encoding 'utf-8' : handle Unicode characters
def write_partial_index(partial_index_count: int):
    with open("../../indexes/partial_index" + str(partial_index_count) + ".txt", "w", encoding='utf-8') as file:
        file.write(str(inverted_index))
    inverted_index.clear()

# processes the entire DEV file given to us
# os.chdir("./developer/DEV"): path to DEV
# os.listdir(os.getcwd()) gives us a list of all subfolder inside DEV
# processes each folder by calling process_single_directory
# write partial index to a file as a record to make sure not overflow the memeory in case DEV is too large
# if inverted_index exceeds 100000 elements, write the element to a new file
def process_dev_folder():
    os.chdir("./developer/DEV")
    print("Current directory:", os.getcwd())
    count = 1
    for file in os.listdir(os.getcwd()):
        if os.path.isdir(file):
            process_single_directory(file)
        
        if len(inverted_index) > 100000:
            write_partial_index(count)
            count += 1
    if len(inverted_index) > 0: 
        write_partial_index(count)

# runs process_dev_folder()
# go back to previous directory
# write docs into docs.txt
def indexer():
    process_dev_folder()
    os.chdir('..')
    print("Current directory:", os.getcwd())

    with open("docs.txt", "w") as f:
        f.write(str(docs))

# gets all the partial_index files
# for each file check all the character in LETTERS 
# creates 27 inverted_index files: 26 for 26 letters, 1 for special characters
# saves all the unique words into uniqueWords
def split_indexes():
    partial_index_list = []
    index_dict = {}
    special_index_dict = {}

    temp_partial_index_count = 1
    while(os.path.exists("indexes/partial_index" + str(temp_partial_index_count) + ".txt")):
        partial_index_list.append("indexes/partial_index" + str(temp_partial_index_count) + ".txt")
        temp_partial_index_count += 1

    for letter in LETTERS:
        for partial_index in partial_index_list:
            print("READING " + letter + "from: " + partial_index)
            with open(partial_index, "r", encoding='utf-8') as file:
                file_content = ast.literal_eval(file.read())
                for key in file_content.keys():
                    if key[0] not in LETTERS:
                        special_index_dict[key] = file_content[key]
                    elif key[0] == letter:
                        index_dict[key] = file_content[key]
            
        with open("indexes/inverted_index" + letter + ".txt", "w", encoding='utf-8') as open_file:
            if letter == "":
                count = 1
                for word in special_index_dict:
                    print("{\"" + word + "\": " + str(special_index_dict[word]) + "}", file=open_file)

                    with open("uniqueWords.txt", "a", encoding='utf-8') as f:
                        print(word + " " + str(count), file=f)
                    count += 1
            
            else:
                count = 1
                for word in index_dict:
                    print("{\"" + word + "\": " + str(index_dict[word]) + "}", file=open_file)

                    with open("uniqueWords.txt", "a", encoding='utf-8') as f:
                        print(word + " " + str(count), file=f)
                    count += 1
        index_dict.clear()

indexer()
split_indexes()

index_size_on_disk = sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))
print(f"Total index size on disk (in KB): {index_size_on_disk / 1024}")