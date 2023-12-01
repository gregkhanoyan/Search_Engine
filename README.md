# 121_Assignment3  
# SEARCH ENGINE  
Wrote a search engine from the ground up that is capable of handling tens of thousands of documents or Web pages, under harsh operational constraints and having a query response time under 300ms.  
  
# Indexer.py  
 - To run indexer.py, navigate to the "IR23F-A3-G24" folder using the cd command in the terminal  
 - Type "python3 indexer.py" to execute indexer and build the index  
 - Indexer.py will create a folder called indexes. Inside this folder, you will find the partial_index.txt files, which contain all the indexes from all the documents (JSON files), document IDs, and TF values  
 - The indexes folder includes 27 inverted_index.txt files, which separate all the indexes from the partial_index.txt files based on their first letter (26 letters and 1 special characters)  
 - Indexer.py also creates two files: docs.txt and uniqueWords.txt  
 - Docs.txt is a list of dictionaries, each dict contains the JSON file, document ID, and URL path to look for that document  
 - uniqueWords.txt contains all the unique tokens obtained from the documents as well as the line number to find the tokens (indexes) in the inverted_index.txt files  
  
# Search.py  
- To run search.py, navigate to the "IR23F-A3-G24" folder using the cd command in the terminal  
- Type "python3 search.py" to execute search engine. A GUI window will appear  
- Inside the GUI window, enter your search query into the search box, and then click the “Enter” button to search  
- The ranked pages will be outputted at the bottom of the window  
- The search time will also be outputted at the bottom of the window  
  
# Deliverables for indexer.py:  
Number of Unique Tokens: 738,246  
Number of Documents: 55,397  
Total size of Index on Disk: 266817.866 KB  
  
