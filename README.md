# 121_Assignment3
SEARCH ENGINE  
Wrote a search engine from the ground up that is capable of handling tens of thousands of documents or Web pages, under harsh operational constraints and having a query response time under 300ms.  

Indexer.py  
 - To run indexer.py, type "python3 indexer.py" to run to the file to build the index  
 - Indexer.py will create a folder called indexes. Inside this folder, you will find the partial_index.txt files, which contain all the indexes from all the documents (JSON files).  
 - Inside the indexes folder, you also have 27 inverted_index.txt files, which separate all the indexes from the partial_index.txt files based on their first letter (26 letters and 1 special characters)  
 - Indexer.py also creates two files docs.txt and uniqueWords.txt  
 - Docs.txt is a list of dictionaries, each dict contains the JSON file, document ID, and URL path to look for that document  
 - uniqueWords.txt contains all the unique tokens obtained from the documents as well as the line number to find the tokens (indexes) in the inverted_index.txt files  
  
  
Current numbers for indexer.py:  
Number of Unique Tokens: 2,057,195
Number of Documents: 55396
Total size of Index on Disk: 353,825.375 KB
