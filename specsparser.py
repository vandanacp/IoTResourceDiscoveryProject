import nltk
import os
import re
from nltk.corpus import stopwords

def cleaner(s):
    cl = re.compile('[\//(),]')
    cltxt = re.sub(cl, ' ', s)
    cltxt = cltxt.lower()
    #print(cltxt)
    return cltxt

def split_key_value(l):
    fl = []
    l = re.sub(' +', ' ', l) 
    l = re.sub('\t+', ' ', l) 
    stop_words = set(stopwords.words("english"))
    l = l.split(":")
    #print(l)
    for w in l:
        if w not in stop_words:
            fl.append(w)
    #print(fl)
    fl_k = cleaner(fl[0])
    fl_v = cleaner(fl[1])
    #print("%s : %s" %(fl_k, fl_v))
    return [fl_k, fl_v]

def parse_files():
    data = []
    files =  [f for f in os.listdir('./specs') if re.match(r'[a-zA-Z0-9]*\.spec', f)]
    for f in files:
        #print("\n\n")
        #print(f)
        kv=[]
        with open(f"./specs/{f}") as finp:
            out = {}
            cl=""
            for l in finp:
                if not l.rstrip():
                    continue
                l = l.rstrip("\n")
                if re.search(':', l):
                    if len(cl):
                        kv.append(split_key_value(cl))
                    cl = l
                else:
                    cl = cl + "." + l
            if len(cl):
                kv.append(split_key_value(cl))

            out['filename'] = f;
            out['kv'] = kv
            data.append(out)
    return data
