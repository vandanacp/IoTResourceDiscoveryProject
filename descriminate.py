# excel file is converted to json using excel2json
import json
import nltk
import calc_score
import pdb
import rdfsearch

devices = {}
slist = []
kv_dict = {}


def  init():
    f = open("./Unified_Data.json")
    data = json.load(f)
    for e in data:
        stype = e['servicetype'].split(",")
        for s in stype:
            if s in devices:
                devices[s].append(e)
            else:
                devices[s] = []
                devices[s].append(e)
                slist.append(s)
    print(slist)
    for s in slist:
        print("%s : %u" %(s, len(devices[s])))
        for d in devices[s]:
            for kv in d.items():
                if kv[0] in kv_dict:
                    kv_dict[kv[0]].append(kv[1])
                else:
                    kv_dict[kv[0]] = []
                    kv_dict[kv[0]].append(kv[1])
        process = {}
        score_ = {}
        for k in kv_dict:
            process[k] = False
            print("k %s lenght %u" %(str(k), len(kv_dict[k])))
            for l in range(len(kv_dict[k])):
                if kv_dict[k][l] != "Nil":
                    process[k] = True
                    break
        for k in kv_dict:
            if process[k] == False or k == 'servicetype':
                continue
            print("%s : %s : type %s" %(k, kv_dict[k], str(type(kv_dict[k][0]))))
            if isinstance(kv_dict[k][0], float) or isinstance(kv_dict[k][0], int):
                score = calc_score.score(kv_dict[k], "int", 1)   
            elif isinstance(kv_dict[k][0], str):
                score = calc_score.score(kv_dict[k], "str", 1)   
            else:
                assert(0)
            score_[k] = score

        score_sorted = dict(reversed(sorted(score_.items(), key=lambda item: item[1])))
        attr_prio_list = []
        for p, q in score_sorted.items():
            print("%s : %s" %(str(p), str(q)))
            attr_prio_list = attr_prio_list  + [p]

        # call dfss with priority list
        rdfsearch.dfss(attr_prio_list)
        break

def main():
    init();

if __name__ == '__main__':
    exit(main())


