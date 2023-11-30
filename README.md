# 121_Assignment3  
# SEARCH ENGINE  
Wrote a search engine from the ground up that is capable of handling tens of thousands of documents or Web pages, under harsh operational constraints and having a query response time under 300ms.  
  
# Indexer.py  
 - To run indexer.py, use the cd command in the terminal to get into the "CS121_AS3" folder  
 - Type "python3 indexer.py" to run to the file to build the index  
 - Indexer.py will create a folder called indexes. Inside this folder, you will find the partial_index.txt files, which contain all the indexes from all the documents (JSON files), document IDs, and TF values  
 - Inside the indexes folder, you also have 27 inverted_index.txt files, which separate all the indexes from the partial_index.txt files based on their first letter (26 letters and 1 special characters)  
 - Indexer.py also creates two files docs.txt and uniqueWords.txt  
 - Docs.txt is a list of dictionaries, each dict contains the JSON file, document ID, and URL path to look for that document  
 - uniqueWords.txt contains all the unique tokens obtained from the documents as well as the line number to find the tokens (indexes) in the inverted_index.txt files  
  
# Search.py  
- To run search.py, use the cd command in the terminal to get to the location of the "CS121_AS3" folder  
- Type "python3 search.py" to run to the file. A GUI window will appear  
- Inside the GUI window, enter the words you want to search for in the search box, and then click the “Enter” button  
- The result will be outputted at the bottom of the window  
- The search time will also be outputted at the bottom of the window  
  
# Deliverables for indexer.py:  
Number of Unique Tokens: 738,246  
Number of Documents: 55,397  
Total size of Index on Disk: 266817.866 KB  
