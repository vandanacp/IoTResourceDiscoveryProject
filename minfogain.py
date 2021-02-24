import pandas as pd
import numpy as np
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2,mutual_info_classif
import json
import csv

def derive(svc_type, rem_attr_list):
    f = open("./Unified_Data.json")
    out = open("%s.csv" %(svc_type), 'w')
    csv_file = csv.writer(out)
    data = json.load(f)
    attr_list = []
    for s in data:
        for e in s:
            if e == 'servicetype':
                continue
            attr_list.append(str(e))
        break
    attr_list.append('servicetype')
    print(attr_list)
    csv_file.writerow(attr_list)

    for s in data:
        stype = s['servicetype'].split(",")
        attr_value = []
        tattrs = 0
        if True:
            for e in s:
                if e in rem_attr_list and s[e] != 'Nil':
                    attr_value.append("true")
                else:
                    attr_value.append("false")
                tattrs = tattrs + 1
        if svc_type in stype:
            # last one service type
            attr_value.append("1")
        else:
            # last one service type
            attr_value.append("0")
        csv_file.writerow(attr_value)

    data=pd.read_csv("%s.csv" %(svc_type))
    print(data)
    X = data.iloc[:,0:tattrs - 1]  #independent columns
    y = data.iloc[:,-1]    #target column - service type
    mut_info_score = mutual_info_classif(X,y, random_state=0)
    dfscores = pd.DataFrame(mut_info_score)      
    dfcolumns = pd.DataFrame(X.columns)
    #concat two dataframes for better visualization
    featureScores = pd.concat([dfcolumns,dfscores],axis=1)
    featureScores.columns = ['Specs','Score']  #naming the dataframe columns
    count = 0
    for score in featureScores['Score']:
        if float(score) > 0:
            count = count + 1
    print(featureScores.nlargest(count,'Score'))
