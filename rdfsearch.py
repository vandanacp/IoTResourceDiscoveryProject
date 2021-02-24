from rdflib import Graph, plugin
from rdflib.serializer import Serializer
import json
import time
import minfogain

devices = {}
slist = []
g = Graph()
g.parse("Unified_Data_LD.rdf", format="n3")
#print(g.serialize(format='json-ld', indent=4))
#print(len(g))

#for stmt in g:
#    pprint.pprint(stmt)

def add_service_type(e):
    stype = e['servicetype'].split(",")
    for s in stype:
        if s in devices:
            devices[s].append(e)
        else:
            devices[s] = []
            devices[s].append(e)
            slist.append(s)

def search(attr_list, service_type):
    print("attr %s" %attr_list)
    count = 0
    for d in devices[service_type]:
        lkup = ""
        for a in attr_list:
            lkup = lkup + "?x <info:discovery/iot_resource/%s> \"%s\" . " %(a.lower(), d[a]) 

        qres = g.query("""SELECT ?s WHERE {
                        %s
                        ?x <info:discovery/iot_resource/device_id> ?s }"""%lkup)
        #print("lkup %s qres %s" %(lkup, len(qres)))
        for row in qres:
            #print("%s" % row)
            count = count + 1
    return float(count) / len(devices[service_type])


f = open("./Unified_Data.json")
data = json.load(f)

def sfs():
    # SFS
    # add one by one to the list and check
    for s in data:
        add_service_type(s)
    for s in data:
        d = ""
        selected = []
        min_score = 0xffffffff
        stype = s['servicetype'].split(",")
        for e in s:
            t0 = time.process_time()
            if e == "Device_ID" or e == "servicetype":
                continue
            if s[e] == 'Nil':
                continue
            score = search(selected + [e], stype[0])
            print("Score for attr %s for stype %s is %s" %(selected + [e], stype[0], str(score)))
            t1 = time.process_time() - t0
            print("Time elapsed: ", t1) # CPU seconds elapsed (floating point)
            if score < min_score:
                min_score = score
                selected = selected + [e]
        break
    print("SFS selected %s" %selected)

def sbs():
    # SBS
    # add to the list first and remove one by one and check
    for s in data:
        add_service_type(s)
    for s in data:
        selected = []
        min_score = 0xffffffff
        stype = s['servicetype'].split(",")
        for e in s:
            if e == "Device_ID" or e == "servicetype":
                continue
            if s[e] == 'Nil':
                continue
            selected = selected + [e]
        score = search(selected + [e], stype[0])
        print("Score for attr %s for stype %s is %s" %(selected, stype[0], str(score)))
        min_score = score
        for e in s:
            t0 = time.process_time()
            if e == "Device_ID" or e == "servicetype":
                continue
            if s[e] == 'Nil':
                continue
            print("%s : %s" %(selected, e))
            nlist = selected[:]
            nlist.remove(e)
            score = search(nlist, stype[0])
            print("Score for attr %s for stype %s is %s" %(nlist, stype[0], str(score)))
            if score <= min_score:
                min_score = score
                print("selected %s , remove %s" %(selected, e))
                selected.remove(e)
            t1 = time.process_time() - t0
            print("Time elapsed: ", t1) # CPU seconds elapsed (floating point)
        break
    print("SBS selected %s" %selected)

def dfss(priolist):
    # DFFS
    # add one by one to the list and check
    for s in data:
        add_service_type(s)
    for s in data:
        d = ""
        selected = []
        prev_score = 0
        min_score = 0xffffffff
        prev_match = None
        stype = s['servicetype'].split(",")
        for e in priolist:
            print("%s : %s" %(str(e), str(s[e])))
            t0 = time.process_time()
            if e == "Device_ID" or e == "servicetype":
                continue
            if s[e] == 'Nil':
                continue
            score = search(selected + [e], stype[0])
            print("Score for attr %s for stype %s is %s" %(selected + [e], stype[0], str(score)))
            t1 = time.process_time() - t0
            print("Time elapsed: ", t1) # CPU seconds elapsed (floating point)
            print("Matches found %u" %score)
            if score < min_score:
                selected = selected + [e]
                min_score = score
                prev_match = e
            elif score == min_score:
                nlist = selected + [e]
                nlist.remove(prev_match)
                score = search(nlist, stype[0])
                if score == min_score:
                    selected.remove(prev_match)
            else:
                assert(0)

        rem_features = []
        for e in s:
            if e == "Device_ID" or e == "servicetype":
                continue
            if s[e] == 'Nil':
                continue
            if e in selected:
                continue
            rem_features = rem_features + [e]
        print("DFFS selected %s" %str(selected))
        print("Remaining features %s" %rem_features)
        minfogain.derive(stype[0], rem_features)
        break

sfs()
#sbs()
#dfss()
