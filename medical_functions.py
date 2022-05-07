#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  5 00:08:32 2022

@author: roy
"""
from pprint import pprint
import nltk
import sys
from stat_parser import Parser
import pandas as pd
import os
os.environ['R_HOME'] = '/Library/Frameworks/R.framework/Resources' # set R_HOME
import rpy2.robjects as robjects
robjects.r.setwd("/Users/roy/coding/PGT/DIA") # set R working directory


def getKeyWord_NN(reply):
    tokens = nltk.word_tokenize(reply)
    tagged = nltk.pos_tag(tokens)
    properNouns = [ word for (word, pos) in tagged if pos=="NNP" ]
    if not properNouns:
        properNouns = [ word for (word, pos) in tagged if pos=="NN" ]
    if not properNouns:
        properNouns = [ word for (word, pos) in tagged if pos=="NNS" ]
    return properNouns

def getKeyWord_num(reply):
    tokens = nltk.word_tokenize(reply)
    tagged = nltk.pos_tag(tokens)
    properNouns = [word for (word,pos) in tagged if pos == "CD"]
    if not properNouns :
        properNouns = [word for (word,pos) in tagged if pos == "LS"]
    return properNouns



# users can exit bye saying bye in every question
def ask(question,knowledge):
    reply = input(question)
    properNouns = getKeyWord_NN(reply)
    for word in properNouns :
        if word == "bye" or word == "goodbye" \
            or word == "Bye" or word == "Goodbye" :
            print()
            print("Patient information: ")
            pprint(knowledge)
    
            fw = open("patientInfo",'w+')
            fw.write(str(knowledge))
            fw.close()
            sys.exit()
    return reply


# different file
def ask2(question,knowledge):
    reply = input(question)
    properNouns = getKeyWord_NN(reply)
    for word in properNouns :
        if word == "bye" or word == "goodbye" \
            or word == "Bye" or word == "Goodbye" :
            print()
            print("Diagnosis records: ")
            pprint(knowledge)
    
            fw = open("record",'w+')
            fw.write(str(knowledge))
            fw.close()
            sys.exit()
    return reply



def show_record():
    fr = open("record",'r+')
    knowledge = eval(fr.read())
    fr.close
    print()
    print("Diagnosis records: ")
    pprint(knowledge)



def main():
    print("Hello, I am a medical advice agent.",end="")
    
    while True :
        question = "Do you want to get medical advice or see diagnosis records?\n"
        reply = input(question)
        tokens = nltk.word_tokenize(reply)
        tagged = nltk.pos_tag(tokens)
        properNouns = [ word for (word, pos) in tagged if pos=="NNP" or pos=="NN" or pos=="NNS" ]
            
        for word in properNouns:
            if word == "bye" or word == "goodbye" \
                or word == "Bye" or word == "Goodbye" :
                print("Bye! ")
                sys.exit()
            elif word == "records" or word == "record" or \
                word == "Records" or word == "Record" :
                show_record()
                sys.exit()
                
        for word in tokens :
            if word == "advice" or word == "Advice" or \
                word == "bad" or word == "uncomfortable" :
                patientName,age = patient()
                if age < 10:
                    question_young(patientName)
                else:
                    diagnosis_old(patientName)
        
        print("I cannot help you with that. ")



def patient():
    fr = open("patientInfo",'r+')
    knowledge = eval(fr.read())
    fr.close
    
    
    question = "What is your name?\n"
    reply = ask(question,knowledge)
    # check if the name is recorded in the system
    check = {(person,fact,value) for (person, fact,value) \
              in knowledge if fact=="name" and value == getKeyWord_NN(reply)[0] }
    # print(check)
    patientName = reply
    if not check :
        count = 0
        for (person, fact, value) in knowledge :
            if int(person) > count :
                count = int(person)
        count += 1
        currentPatient = str(count) # mark the new patient
        knowledge.add((currentPatient,"name",reply))
        knowledge.add((currentPatient,"age","?"))
    else :
        currentPatient = list(check)[0][0]
    
    unknownAge = { (person,fact,value) for (person,fact,value) \
                in knowledge if person==currentPatient and \
                    fact=="age" and value=="?" }
    
    if unknownAge:
        question = "What is your age?\n"
        reply = ask(question,knowledge)
        age = getKeyWord_num(reply)[0]
        knowledge.add((currentPatient,"age",age))
        knowledge.remove((currentPatient,"age","?"))
    else:
        findAge = { (person,fact,value) for (person,fact,value) \
                    in knowledge if person==currentPatient and \
                        fact=="age"}
        age = list(findAge)[0][2]
    
    fw = open("patientInfo",'w+')
    fw.write(str(knowledge))
    fw.close()
        
    return patientName, int(age)




def diagnosis_old(patientName):
    
    fr = open("record",'r+')
    knowledge = eval(fr.read())
    fr.close
    
    # assign a new id for the latest diagnosis record
    count = 0
    for (record, person, fact, value) in knowledge :
        if int(record) > count :
            count = int(record)
    count += 1
    record = str(count)
    
    while True :
        question = "What is your temperature now?\n"
        reply = ask2(question,knowledge)
        try :
            temperature = getKeyWord_num(reply)[0]
        except IndexError:
            print("Please tell me your temperature in numbers.")
            continue
        knowledge.add((record,patientName,"temperature",temperature))
        break
    
    while True :
        question = "From 0 to 10, how would you rate your headache?\n"
        reply = ask2(question,knowledge)
        try :
            headache = getKeyWord_num(reply)[0]
        except IndexError :
            print("Please tell me the degree of your headache in numbers.")
            continue
        knowledge.add((record,patientName,"headache",headache))
        break
    
    data = [float(temperature),float(headache)]
    # output the data to a csv file
    dataframe = pd.DataFrame({'A':data})
    dataframe.to_csv("data.csv",index=False,sep=',')
    
    # evaluate the urgency with the FIS model in R
    robjects.r.source("medicalFIS.r")
    urgency = int(robjects.r('urgency')[0])
    knowledge.add((record,patientName,"urgency",urgency))
    print("Your urgency is",urgency,"%")
    
    if urgency >= 80 :
        advice = "I suggest you call 999 immediately. "
    elif urgency >= 60 :
        advice = "I suggest you go to the hospital right now. "
    elif urgency >= 35 :
        advice = "If you keep feeling bad, please go to the hospital. "
    else :
        advice = "I suggest you take some medicine and rest for now. "
    print(advice)
    
    # pprint(knowledge)
    fw = open("record",'w+')
    fw.write(str(knowledge))
    fw.close()
    print()
    print("Your record for this diagnosis: ")
    thisRecord = { (record_,patientName_,symptom_,symptomName_) for \
                  (record_,patientName_,symptom_,symptomName_) \
                 in knowledge if record_ == record and patientName_ == patientName }
    pprint(thisRecord)
    sys.exit()



def diagnosis_young(patientName):
    
    fr = open("record",'r+')
    knowledge = eval(fr.read())
    fr.close
    
    # assign a new id for the latest diagnosis record
    count = 0
    for (record, person, fact, value) in knowledge :
        if int(record) > count :
            count = int(record)
    count += 1
    record = str(count)
    
    symptom = 0
    
    active = True
    while active :
        question = "Do you have a headache now?\n"
        reply = ask2(question,knowledge)
        tokens = nltk.word_tokenize(reply)
        for word in tokens :
            if word == "No" or word == "no" or word == "not" :
                active = False
                break
        for word in tokens :
            if word == "Yes" or word == "yes" :
                symptom += 1
                knowledge.add((record,patientName,"symptom"+str(symptom),"headache"))
                active = False
                break
         
        if active == True :
             print("Sorry, I cannot understand.")
    
    active = True
    while active :
        question = "Do you have any other symptoms make you uncomfortable?\n"
        reply = ask2(question,knowledge)
        tokens = nltk.word_tokenize(reply)
        
        for word in tokens :
            if word == "No" or word == "no" :
                if symptom >= 3 :
                    print("You better go to the hospital or call 999 right now. ")
                elif symptom >=1 :
                    print("I suggest you tell your parents. ")
                else :
                    print("Maybe you just need some rest. ")
                fw = open("record",'w+')
                fw.write(str(knowledge))
                fw.close()

                print()
                print("Your record for this diagnosis: ")
                thisRecord = { (record_,patientName_,symptom_,symptomName_) for \
                              (record_,patientName_,symptom_,symptomName_) \
                             in knowledge if record_ == record and patientName_ == patientName }
                pprint(thisRecord)
                sys.exit()
        
        try :
            symptomName = get_symptom(reply)
        except NameError :
            print("I cannot understand. ")
            continue
        
        symptom += 1
        knowledge.add((record,patientName,"symptom"+str(symptom),symptomName))
        print("I have recorded your symptom")



def question_young(patientName):
    
    while True :
        question = "Can you measure your body temperature?\n"
        reply = input(question)
        tokens = nltk.word_tokenize(reply)
        for word in tokens :
            if word == "bye" or word == "goodbye" \
                or word == "Bye" or word == "Goodbye" :
                    print("Bye! ")
                    sys.exit()      
                    
        for word in tokens :
            if word == "No" or word == "no" or word == "not" :
                diagnosis_young(patientName)
        for word in tokens :
            if word == "Yes" or word == "yes" or word == "can" :
                diagnosis_old(patientName)
        
        print("Sorry, I cannot understand.")
        print("You may just simply answer yes or no.")
    
            
            
def get_symptom(sentence):
    parser = Parser()
    t = parser.parse(sentence)
    for st in t.subtrees():
        if st.label()=="VP":
            vpTree = st
    for st in vpTree.subtrees():
        if st.label()=="NP":
            npTree = st
    return " ".join(npTree.leaves())
            
    
    
    
    
    
    
    
    
    
    
    
    
