import os
import re
import sys
import json
import gensim.downloader as api
from gensim import corpora
from gensim.matutils import softcossim
import pdb
import nltk
from gensim.models import Word2Vec, WordEmbeddingSimilarityIndex
from gensim.similarities import SoftCosineSimilarity, SparseTermSimilarityMatrix
import specsparser as specs
from gensim.models.phrases import Phrases, Phraser
import tfidf as tfidf

#model =  api.load('fasttext-wiki-news-subwords-300')

from gensim.test.utils import common_texts
from gensim.models import Word2Vec
model = Word2Vec(common_texts, size=100, window=5, min_count=1, workers=4)
output = []


def dump_result():
    result = {}
    with open("service_out.json") as f:
        service_out = json.load(f)

    for s in service_out:
        for match in s['match']:
            result[match['filename']] = []
    for s in service_out:
        for match in s['match']:
            result[match['filename']].append(s["service_type"])
    for f in result:
        print("%s result %s" %(f, str(result[f])))

def find_similarity(search_w, corpus_w):
    rv = {}
    rv['result'] = []
    bmatch = False
    #Tokenize the sentence into words
    #search_tokens = [word for word in search_w.split()] 
    #corpus_tokens = [word for word in corpus_w.split()]
    search_tokens = search_w
    corpus_tokens = corpus_w

    #print(search_tokens)
    #print(corpus_tokens)
    #print("-----")
    #cp = []
    #for c in corpus_tokens:
    #    cp.append([c])
    
    #corpus_tokens = cp
    search_tokens = [search_w]
    print(corpus_tokens)
    print(search_tokens)
    # Prepare a dictionary and a corpus.
    #documents = [svc_tokens, specs_tokens]
    dictionary = corpora.Dictionary(corpus_tokens)

    termsim_index = WordEmbeddingSimilarityIndex(model.wv)
    bow_corpus = [dictionary.doc2bow(doc) for doc in corpus_tokens]
    similarity_matrix = SparseTermSimilarityMatrix(termsim_index, dictionary)  # construct similarity matrix
    docsim_index = SoftCosineSimilarity(bow_corpus, similarity_matrix, num_best=10)

    # Compute soft cosine similarity
    for t in search_tokens:
        #print("looking for %s" %(t.split()))
        for e in t.split(','):
            match = {}
            e = e.strip()
            lkup = [e]
            try:
                result = docsim_index[dictionary.doc2bow(lkup)]
            except:
                result = [(0, 0)]
            print(f"looking for {lkup}, result {result}")
            if len(result) and result[0][1] > 0.5:
                match['word'] = e.split()
                match['value'] = str(result)
                rv['result'].append(match)
                bmatch = True
    #print(docsim_index[dictionary.doc2bow(search_tokens)])
    return rv if bmatch else None

def parse_service_identify():
    data = []
    with open("./service_identify.txt") as finp:
        for l in finp:
            if l.startswith("#"):
                continue
            out = {}
            l = l.rstrip("\n\r")
            l = re.sub(' +', ' ', l)
            l = l.rstrip()
            m = l.split(':')
            if len(m) < 3:
                print("ignoring service type %s" %(m[0]))
                continue
            out['service type'] = m[0].strip()
            out['representative terms'] = m[1].strip()
            if len(m) >= 3:
                out['indirect terms'] = m[2].strip()
            data.append(out)
    with open("./service_identify.json", "w+") as fout:
        json.dump(data, fout, indent=4)
    return data

def main():
    i = 0
    global output
    try:
        data = parse_service_identify()
        kv_array = specs.parse_files()
        while i < len(data):
            j = 0
            out = {}
            out['match'] = []
            out['service_type'] = data[i]['service type'] 
            print("looking for service %s" %(data[i]['service type']))
            while j < len(kv_array):
                print("----------------------------------------------")
                print("finding similarity in %s" %(kv_array[j]['filename']))
                spec = []
                for k,v in kv_array[j]['kv']:
                    spec.append([k])
                    tokens = nltk.word_tokenize(v)
                    spec.append(tokens)
                #print(spec)
                #print(data[i]['representative terms'])
                rv = find_similarity(data[i]['representative terms'], spec)
                if rv != None:
                    rv['filename'] = kv_array[j]['filename']
                    rv['representative'] = True
                    out['match'].append(rv)
                if 'indirect terms' in data[i]:
                    rv = find_similarity(data[i]['indirect terms'], spec)
                    if rv != None:
                        rv['filename'] = kv_array[j]['filename']
                        rv['representative'] = False
                        out['match'].append(rv)
                j = j + 1
            output.append(out)
            i = i + 1

        print("-------------------matching---------------------")
        i = 0
        while i < len(output):
            print(output[i])
            i = i + 1
            print("\n")
        with open("service_out.json", "w") as f:
            json.dump(output, f, indent=4)
        dump_result()
        return 0
    except Exception as e:
        print("Error in opening the service identify file ")
        print(e)
        return -1

if __name__ == '__main__':
    exit(main())

