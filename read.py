#-----------------------------------------------------
# Code to read from fixed length records (random access file)
# Modified by: Karuna Bhaila
#-----------------------------------------------------
import sys
import os

from lex_tokenize import HTMLLexer

# Define record sizes
HASHTABLE_SIZE = 5000*15*3
TOKEN_SIZE = 15
FREQ_SIZE = 10
START_SIZE = 15
DICT_SIZE = TOKEN_SIZE + FREQ_SIZE + START_SIZE + 3
DOC_INDX_SIZE = 10
TF_IDF_SIZE = 10
POST_SIZE = DOC_INDX_SIZE + TF_IDF_SIZE + 2
DOC_NAME_SIZE = 15
MAP_SIZE = DOC_INDX_SIZE + DOC_NAME_SIZE + 2

# Get record number n from file f (Records numbered from 0 to NUM_RECORDS-1) 
def get_line(f, recordNum, record_size):
    record = ""
    assert recordNum >= 0
    f.seek(0,0)
    f.seek(record_size * recordNum) #offset from the beginning of the file
    record = f.readline()

    return record.split()


# Displays top 10 documents containind input token with weights
def get_files(token, docs, weights, matches):
    # Get hashed index
    sum = 0
    recordNum = -1

    for i in range(len(token)):
        sum = (sum * 19) + ord(token[i])  

    recordNum = sum % HASHTABLE_SIZE
    search_flag = True
    found = False
    f = open('output/dictionary.txt', 'r')

    # Linear probing until _empty_ is found
    while search_flag:
        # Find in dict file
        record = get_line(f, recordNum, DICT_SIZE)     
                
        if record[0] == token:
            doc_freq = int(record[1])
            start_index = int(record[2])
            search_flag = False
            found = True
        elif record[0] == '_empty_':
            search_flag = False
        else:
            recordNum = (recordNum + 1) % HASHTABLE_SIZE

    # Close files
    f.close()
    
    # Find in postings and mapping file
    if found and doc_freq > 0:
        assert record[0] == token

        p = open('output/postings.txt', 'r')
        m = open('output/mappings.txt', 'r')

        for i in range(doc_freq):
            post = get_line(p, start_index + i, POST_SIZE)
            
            if len(post) > 0:
                doc_map = get_line(m, int(post[0]), MAP_SIZE)

                # insert into accumulator
                # add new key if not already in accumulator
                # otherwise add term weight
                if doc_map[1] not in weights.keys():
                    weights[doc_map[1]] = float(post[1])
                    docs[doc_map[1]] = doc_map[0]
                    matches[doc_map[1]] = [token]
                else:
                    weights[doc_map[1]] += float(post[1])
                    matches[doc_map[1]].append(token)

        # close files
        p.close()
        m.close()

    return docs, weights, matches


def get_documents(words):
    filepath = 'temp.txt'

    # write input to file
    with open(filepath, 'w') as f:
        for word in words:
            f.write(word + '\n')
        f.close()

    # tokenize input
    tokenizer = HTMLLexer()
    tokenizer.build()
    tokens = tokenizer.tokenizeFile(inputFile=filepath, getTokens=True)

    # search token in dict, post, and map files
    matches = {}
    docs = {}
    weights = {}

    for token in tokens:
        token = token.strip()
        docs, weights, matches = get_files(token, docs, weights, matches)   

        # for key, value in temp_docs.items():
        #     if key not in matches.keys():
        #         matches[key] = [token]
        #     else:
        #         matches[key].append(token)
        
    # sort accumulator by term weights
    weights = sorted(weights.items(), key=lambda x:x[1], reverse=True)
    weights = dict(weights)

    sorted_docs = []
    sorted_matches = []
    sorted_weights = []

    if docs:
        for i, (key, value) in enumerate(weights.items()):
            if i < 10:
                sorted_docs.append(key)
                sorted_matches.append(matches[key])
                sorted_weights.append(round(value,3))

    # remove temp file
    os.remove('temp.txt')

    # for i, j in zip(sorted_docs, sorted_matches):
    #     print(i, j)

    return sorted_docs, sorted_matches, sorted_weights

if __name__ == '__main__':
    docs, matches = get_documents(['robot', 'launch', 'vaccum', 'gauch', 'susan'])
 