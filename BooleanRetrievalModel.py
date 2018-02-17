# -*- coding: utf-8 -*-
"""
Created on Sat Sep 30 23:47:33 2017
@author: hammadkhan
"""
import re
from nltk import word_tokenize
from collections import defaultdict
import json
import time
start_time = time.time()

#==============================================================================
# Declaring Variables
#==============================================================================
number_of_documents = 15 #default value
stopwords_list = []
lexicon = []
hadeeth = []
verse = []
did = 0
doc_id = []

#==============================================================================
#  Reading Documents from file
#==============================================================================
for i in range(number_of_documents):
    f = open("Dataset/"+str(i+1), 'r')
    for li in f:
        if(li[0]!='['):
            li =  re.sub(r'[^\w\s]','',li)
            hadeeth += li
        if(li[0]=='['):
            did = str(li)
            doc_id.append(did)
            lexicon.append(hadeeth)
            hadeeth=""
            continue
        
f = open("Dataset/Quran Translation.txt")
for li in f:
    if(li[0]!='['):
        li =  re.sub(r'[^\w\s]','',li)
        hadeeth += li
    if(li[0]=='['):
            did = str(li)
            doc_id.append(did)
            lexicon.append(hadeeth)
            hadeeth=""
            continue

#==============================================================================
# Creating Stopword corpus
#==============================================================================
f = open("Dataset/Stopword-List.txt")
stopwords_list = f.readlines()
stopwords_list = [x.rstrip() for x in stopwords_list]

#==============================================================================
# Creating Tokens(Tokenization)
#==============================================================================
def Tokenizer(lexicon):
    token= []
    for i in lexicon[1:]:
        t = word_tokenize(i)
        t = [l for l in t if l not in stopwords_list]
        t = [l for l in t if len(l)>1 ]
        t = [l for l in t if not l.isdigit()]
        token.append(t) 
    return token

tokens = Tokenizer(lexicon)
#==============================================================================
# Creating Inverted Index
#==============================================================================
def create_Inverted_index (terms):
    index = defaultdict(list)
    for i, tokens in enumerate(terms):
        for token in set(tokens):
            index[token.lower()].append(i)
    return index    

inverted_index = create_Inverted_index(tokens)  

#==============================================================================
# Creating Positional Index
#==============================================================================
def positional_index(tokens):
    pos_index = defaultdict(lambda:[])
    for docID, sb in enumerate(tokens):
        for term in set(sb):
            pos_index[term.lower()].append([docID,[index for index, element in enumerate(sb) if element == term]])
    return pos_index

p_index = positional_index(tokens)

#==============================================================================
# Dumping Positional and Inverted Index on to Disk
#==============================================================================
with open('InvertedIndex.json', 'w') as ij:
    json.dump(inverted_index,ij)
with open("PositionalIndex.json", 'w') as pj:
    json.dump(p_index, pj)

ij.close();
pj.close();

#==============================================================================
# loading positional and inverted index from Disk
#==============================================================================
with open("InvertedIndex.json", 'r') as ii:
    Inverted_index = json.load(ii)

with open("PositionalIndex.json", 'r') as pi:
    Positional_index = json.load(pi)    

ii.close();
pi.close();

#==============================================================================
# Getting Term PostingList
#==============================================================================
def get_posting_list(word) :
    given_value = word
    for key, val in Inverted_index.items() :
        if key == given_value :
            p1 = val      
            return p1

#==============================================================================
# PostingList Intersection
#==============================================================================
def intersection(p1,p2):
    if p1 is not None and p2 is not None:
        intersection = list(set(p1) & set(p2)) 
        return intersection
    else:
        return []

#==============================================================================
# PostingList Union
#==============================================================================
def union(p1,p2):
    if p1 is not None and p2 is not None: 
        return list(set().union(p1,p2))
    else:
        return []
    
#==============================================================================
# PostingList Negation
#==============================================================================
def NOT(p1,p2):
    if p1 is not None and p2 is not None:
        return list(set(p1) - set(p2))
    else:
        return []

#==============================================================================
# Getting positional postinglist of terms
#==============================================================================
def get_pos_posting_list(word) :
    given_value = word
    for key, val in p_index.items() :
        if key == given_value :
            p1 = val      
            return p1

def docID(plist):
        return plist[0]

def position(plist):
        return plist[1]

#==============================================================================
# Positional Intersection Book Implementation
#==============================================================================
def pos_intersect(p1,p2,k):
        answer = []   
        if p1 is not None and p2 is not None:                                                                  
            len1 = len(p1)
            len2 = len(p2)
            i = j = 0 
            while i != len1 and j != len2:                                                  
                    if docID(p1[i]) == docID(p2[j]):
                            l = []
                            pp1 = position(p1[i])
                            pp2 = position(p2[j])                                           
        
                            plen1 = len(pp1)
                            plen2 = len(pp2)
                            ii = jj = 0 
                            while ii != plen1:                                              
                                    while jj != plen2:                                      
                                            if abs(pp1[ii] - pp2[jj]) <= k:                 
                                                    l.append(pp2[jj])                       
                                            elif pp2[jj] > pp1[ii]:                         
                                                    break    
                                            jj+=1                                           
                                    l.sort()                                               
                                    while l != [] and abs(l[0] - pp1[ii]) > k :             
                                            l.remove(l[0])                                  
                                    for ps in l:                                            
                                            answer.append([ docID(p1[i])])
                                    ii+=1
                            i+=1                                                            
                            j+=1                                                            
                    elif docID(p1[i]) < docID(p2[j]):
                            i+=1                                                                                                      
                    else:
                            j+=1                                                            
        return answer 

#==============================================================================
# Handling Normal Query
#==============================================================================

def query_handler(query,inverted_index):
    query = query.split(" ")
    term = query[0]
    posting = get_posting_list(term)
    documents = posting
    
    for index in range(1,len(query)):
        if(query[index] == "AND"):
            op = '&'
        elif(query[index]== "OR"):
            op = '||'
        elif(query[index]== "NOT"):
            op = '!'
        else:
            if(op == '&'):
                term = query[index]
                term = get_posting_list(term)
                documents = intersection(documents,term)
    
            elif(op == '||'):
                term = query[index]
                term = get_posting_list(term)
                documents = union(documents,term)
         
            elif(op == '!'):
                term = query[index]
                term = get_posting_list(term)
                documents = list(set(documents) - set(term))
    return documents
#==============================================================================
# Handling Proximity Query
#==============================================================================
def ProximityQueryHandler(query, positional_index):
    proximity = re.findall(r'\d+' , query)
    query = query.split(" ")
    token = []
    term = query[0]
    token.append(term)
    
    for i in range(1,len(query)):
        if(query[i] == "AND"):
            operator = "&"
        
        elif(query[i] == "NOT"):
            operator = "!"
            
        elif("/" in query[i]):
            k = int(proximity[0])
            p1 = get_pos_posting_list(token[0])
            p2 = get_pos_posting_list(token[1])
            documents = pos_intersect(p1,p2,k)
            token.remove(token[0])
            proximity.remove(proximity[0])
        else:
            if(operator == '&'):
                term = query[i]
                token.append(term)
                
            elif(operator == '!'):
                term = query[i]
                token.append(term)
        if(len(token) == 3):
                token.remove(token[0])
    return documents
    
#==============================================================================
# Running Query    
#==============================================================================
query = ""    
while(query != "@"):
    print("~~~~~~Enter @ in the query to Exit.~~~~~~")
    query = input("Enter your query: ")
    if '/' in query:
        results = ProximityQueryHandler(query,Positional_index)
        k=0
        for i in results:
            for j in i:
                results[k] = doc_id[j]
                k+=1
        results = [x.rstrip() for x in results] 
        print (results)
        total_docs = str(len(results))
        print ("Total Documents:" + total_docs)
        
    else:
        if(query != "@"):
            results = query_handler(query,Inverted_index)
            for k in range(len(results)):
                j=0
                for i in results:
                        if(not isinstance(results[j],str)):
                            results[j] = doc_id[i] 
                            j+=1    
            results = [x.rstrip() for x in results] 
            print (results)
            total_docs = str(len(results))
            print ("Total Documents:" + total_docs)        
        else:
            break    
    
print("Total Time: %s seconds" % (time.time() - start_time))
