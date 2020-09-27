import numpy as np
import json
import specsparser as specs
import utils as utils
import ontology as ontology

# Category -> words
data = {}
embeddings_index = {}
data_embeddings = {}
categories = {}

def parse_categories():
    json_data = {}
    global data, categories

    with open("./attributebin.json") as f:
        json_data = json.load(f)

    data["device"] = []
    for d in json_data['device']['words'].split(','):
        data["device"].append(d.strip())

    data["application"] = []
    for d in json_data['application']['words'].split(','):
        data["application"].append(d.strip())

    data["qos"] = []
    for d in json_data['qos']['words'].split(','):
        data["qos"].append(d.strip())

    # Words -> category
    categories = {word: key for key, words in data.items() for word in words}
    print(categories)

def gen_embed_indexes():
    global embeddings_index, data_embeddings, categories

    # Load the whole embedding matrix
    with open('../../glove/glove.6B.100d.txt') as f:
        for line in f:
            values = line.split()
            word = values[0]
            embed = np.array(values[1:], dtype=np.float32)
            embeddings_index[word] = embed
        print('Loaded %s word vectors.' % len(embeddings_index))
        # Embeddings for available words
        data_embeddings = {key: value for key, value in embeddings_index.items() if key in categories.keys()}

# Processing the query
def process(query):
  global embeddings_index, data_embeddings, categories
  print("scores for query : %s" %query)
  query_embed = embeddings_index[query]
  scores = {}
  for word, embed in data_embeddings.items():
    category = categories[word]
    dist = query_embed.dot(embed)
    dist /= len(data[category])
    scores[category] = scores.get(category, 0) + dist
  return scores


def create_excel_sheet(filename, result):
    ontology.init()
    with open("service_out.json") as f:
        service_out = json.load(f)

    for s in service_out:
        for match in s['match']:
            if match['filename'] == filename:
                print(s["service_type"])
                for k, v in result['device']:
                    ontology.add_device(1, k, v)
                for k, v in result['qos']:
                    ontology.add_qos(1, s["service_type"], k, v)
                for k, v in result['application']:
                    ontology.add_application(1, k, v)
    ontology.workbook_final()
# Testing
def main():
    i = 0
    result = {}
    try:
        parse_categories()
        gen_embed_indexes()
        kv_array = specs.parse_files()
        while i < len(kv_array):
            print("----------------------------------------------")
            filename=kv_array[i]['filename'] #.lower().replace('.', '_')
            print("extracting key values from  %s" %(kv_array[i]['filename']))
            result[filename] = {}
            result[filename]['application'] = []
            result[filename]['qos'] = []
            result[filename]['device'] = []

            for k,v in kv_array[i]['kv']:
                print("%s : %s" %(k, v))
                if v == "":
                    continue
                l = len(k.split());
                korig = k
                if l > 1:
                    #k = k.split()[l - 1]
                    k = utils.k_get(k.strip(), l)
                try:
                    scores = process(k.strip())
                    print(scores)
                    max = 'device' if  scores['device'] > scores['application'] else 'application'
                    max = max if scores['qos'] < scores[max] else 'qos'
                    print(max)
                    k = utils.k_strip(korig.strip(), k.strip())
                    if k == None:
                        continue
                    print("--------")
                    result[filename][max].append([k, v])
                except Exception as e:
                    print("Exception")
                    print(e)
                    pass
            i = i + 1
            break

    except Exception as e:
        print("Exception")
        print(e)

    print("-------------")
    for f in result:
        print(f)
        for s in result[f]:
            out = s + "    :"
            for k, v in result[f][s]:
                out = out + k + ":"
            #print(result[f][s])
            utils.dump(out)
        print("---")
        create_excel_sheet(f, result[f])


if __name__ == '__main__':
    exit(main())
