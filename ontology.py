from nltk.corpus import wordnet
import xlsxwriter
import json
import utils as utils


# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('output.xlsx')
worksheet = workbook.add_worksheet()
history={}
history['device'] = {}
history['app'] = {}
history['qos'] = {}
data = {}

def create_xlssheet(data):
    global history
    col = 0
    for k in data['thing']['iot_resource']['device_entity'] :
        worksheet.write(0, col, k)
        history['device'][k] = {}
        history['device'][k]['col'] = col
        history['device'][k]['type'] = data['thing']['iot_resource']['device_entity'][k]
        col = col + 1

    for k in data['thing']['iot_resource']['application_entity'] :
        worksheet.write(0, col, k)
        history['app'][k] = {}
        history['app'][k]['col'] = col
        history['app'][k]['type'] = data['thing']['iot_resource']['application_entity'][k]
        col = col + 1

    for s in data['thing']['iot_resource']['service_entity']['services'] :
        val = ""
        for k in s:
            if k == "name":
                val = s[k]
                continue
            if k == "qos":
                history['qos'][val] = {}
                for q in s["qos"]:
                    history['qos'][val][q] = {}
                    history['qos'][val][q]['col'] = col
                    history['qos'][val][q]['type'] = s['qos'][q]
                    k = val + "_" + q
                    worksheet.write(0, col, k)
                    col = col + 1


def find_in_synonyms(name, history):
    for syn in wordnet.synsets(name):
        for l in syn.lemmas():
            for k in history:
                if k == l.name():
                    return k
    return None

def workbook_final():
    workbook.close()

def add_device(row, name, value):
    matched = False
    for k in history['device']:
        name = name.strip()
        #print("comparing %s vs %s" %(name, k))
        if k == name:
            #print("  match found")
            matched = True
            worksheet.write(row, history['device'][k]['col'], value)
            break
        if k.find(name) >= 0:
            #print("  match found")
            matched = True
            worksheet.write(row, history['device'][k]['col'], value)
            break
        if name.find(k) >= 0:
            #print("  match found")
            matched = True
            worksheet.write(row, history['device'][k]['col'], value)
            break
    if matched != True:
        syn = find_in_synonyms(name, history['device'])
        if syn != None:
            matched = True
            worksheet.write(row, history['device'][syn]['col'], value)

    if matched != True:
        matched, k = utils.sdevice_match(name, history['device'])
        if matched == True:
            worksheet.write(row, history['device'][k]['col'], value)
        else:
            print("%s not found in device list" %(name))

def add_application(row, name, value):
    matched = False
    for k in history['app']:
        if k == name:
            matched = True
            worksheet.write(row, history['app'][k]['col'], value)
            break
        if k.find(name) >= 0:
            matched = True
            worksheet.write(row, history['app'][k]['col'], value)
            break
        if name.find(k) >= 0:
            matched = True
            worksheet.write(row, history['app'][k]['col'], value)
            break
    if matched != True:
            print("%s not found in app list" %(name))

def add_qos(row, qos_type, name, value):
    matched = False
    for k in history['qos'][qos_type]:
        #print("qos check k %s name  %s" %(k, name))
        if k == name:
            matched = True
            worksheet.write(row, history['qos'][qos_type][k]['col'], value)
            break
        if k.find(name) >= 0:
            #print("  match found")
            matched = True
            worksheet.write(row, history['qos'][qos_type][k]['col'], value)
            break

    if matched != True:
            print("%s not found in qos list of %s" %(name, qos_type))

def init():
    global data
    with open("./ontology.json") as f:
        data = json.load(f)

    create_xlssheet(data)
