#!/usr/bin/env python
#--------------------------------------------------------------------------------------------------------------------------
#@Author: Brandon Radosevich
#@Date: September 3, 2016
#@Class: New Mexico State University EE565/490
#@Project: Project 2
#Description:
#Creating a SPAM | HAM Filter using test data.
#--------------------------------------------------------------------------------------------------------------------------
#import statements
from __future__ import division # for printing progress
import time # time for timing operations
import re # for regular expression handling.
import threading # for threading
import argparse # for command line arguments
import json # for creating a json file.
import os # for texting after training is done.
import sys # for progress bar
from collections import Counter, defaultdict # for counting words
from timeit import default_timer as timer # for timing total execution speed.
import csv # for writing to text file
import numpy as np # for the maths...
from email.parser import Parser # for parsin email
import string # for parsing
from multiprocessing import Process as Task, Queue
'''
class: EmailParser
Date: 9-9-2016
Description: This Class contains all of the functions needed to train a Naive Bayesian Spam Filter.
In order to use this Class, you must provide a Training File with the names of folders to read emails,
as well as a Key File with the classification of each file, i.e. SPAM OR HAM.
'''
class EmailParser(object):
    def __init__ (self, inputFile, keyFile, phoneNumber,wordMin, wordMax):
        self.wordMin = wordMin
        self.wordMax = wordMax
        self.spamDict = Counter()
        self.hamDict = Counter()
        print '[+] Beginning Email Parsing'
        print '-----------------------------------------------------------------------------------------'
        spamEmails, hamEmails, total = self.splitEmails(inputFile,keyFile)
        self.parseEmails(spamEmails,hamEmails, total)
        if phoneNumber is not None:
            self.notify(number=phoneNumber,message='Training Complete')
        print '[.] Training Completed'
    '''
    function: splitEmails
    Date: 9-9-2016
    Description: Reads in Training & Key File and filters the emails into two lists, SPAM & HAM.
    Returns a tuple with spamEmails, hamEmails, and total Number of Emails.
    '''
    def splitEmails(self,inputFile, keyFile):
        hamEmails = []
        spamEmails = []
        folder = "trec05p-1/"
        fData = [line.strip("\r\n") for line in open(inputFile)]
        kData = [line.strip("\r\n") for line in open(keyFile)]
        emails = []
        keys = []
        total = len(fData)
        for i in range(0,len(fData)):
            emails.append(folder + str(fData[i]).strip("[").strip("'").strip("'").strip("]"))
            keys.append(str(kData[i]))
        for key,email in zip(keys,emails):
            if key == 'ham':
                hamEmails.append(email)
            elif key == 'spam':
                spamEmails.append(email)
        return (spamEmails,hamEmails,total)
    '''
    function: parseEmails
    Date: 9-9-2016
    Description: Takes the two lists from splitEmail and total from splitEmail function and
    begins parsing Emails. The emails are parsed by key. Spam Emails are parsed first, and Ham emails.
    '''
    def parseEmails(self,spamEmails,hamEmails,total):
        start = timer()
        print 'Total Number of Emails: ',total
        print '-----------------------------------------------------------------------------------------'
        sTotal = len(spamEmails)
        hTotal = len(hamEmails)
        status = Queue()
        lock1 = threading.Lock()
        lock2 = threading.Lock()
        print 'Total # Of Ham Emails: %d | Total # Of Spam Emails: %d' % (len(hamEmails), len(spamEmails))
        print '-----------------------------------------------------------------------------------------'
        child1 = threading.Thread(target=self.parseSpamEmails,args=(spamEmails,total,status,lock1))
        child2 = threading.Thread(target=self.parseHamEmails,args=(hamEmails,total,status,lock2))
        workers = [child1,child2]
        child1.daemon = True
        child2.daemon = True
        child1.start()
        child2.start()
        progress = {}
        progress['Spam'] = 0
        progress['Ham'] = 0
        while any(i.is_alive() for i in workers):
            time.sleep(0.006)
            while not status.empty():
                filename, percent = status.get()
                progress[filename] = percent
                self.progressBar(progress,sTotal,hTotal)
        child2.join()
        child1.join()
        end = timer()
        print '\n-----------------------------------------------------------------------------------------'
        print 'Total Elapsed Time: %.2f '% (end - start,)
        self.combineDictionaries(self.hamDict,self.spamDict,'training.txt','training_probs.txt')
        self.getMostCommonWords(self.hamDict.most_common(5000),self.spamDict.most_common(5000))

    '''
    function: parseSpamEmails
    Date: 9-14-2016
    Description: Parse Spam Emails, using multithreading, locking thread down while in use.
    '''
    def parseSpamEmails(self,spamEmails,total,status,lock):
        lock.acquire()
        try:
            sCount = 0
            for spam in spamEmails:
                self.readSpamEmail(spam)
                sCount = sCount + 1
                status.put(["Spam",sCount])
        finally:
            lock.release()

    '''
    function: parseHamEmails
    Date: 9-14-2016
    Description: Parses Ham Emails, using  multithreading, locking thread down while in use.
    '''
    def parseHamEmails(self,hamEmails,total,status,lock):
        lock.acquire()
        try:
            dCount = 0
            for ham in hamEmails:
                self.readHamEmail(ham)
                dCount = dCount + 1
                status.put(['Ham',dCount])
        finally:
            lock.release()

    '''
    function: progressBar
    Date: 9-14-2016
    Description: Prints out the Progress Of The Training.
    '''
    def progressBar(self,progress,sTotal,hTotal):
        sys.stdout.write('\r')
        for f,p in progress.items():
            if f == "Ham":
                sys.stdout.write('%s: %.2f%% Complete | ' % (f,p / hTotal * 100))
            elif f == 'Spam':
                sys.stdout.write(' %s: %.2f%% Complete ' % (f,p / sTotal * 100))
        sys.stdout.flush()

    '''
    function: readSpamEmail
    Date: 9-9-2016
    Description: For each SPAM Email, the email is read into a list and then the set() function is called to
    see all unique words which exist in the email. Then the global SPAM Dictionary Counter is updated for each
    value in the email.
    '''
    def readSpamEmail(self, filePath):
        with open(filePath, 'r') as fp:
            words = self.parseEmail(fp)
            self.spamDict.update(words)
        fp.close()
    '''
    function: readHamEmail
    Date: 9-9-2016
    Description: For each HAM Email, the email is read into a list and then the set() function is called to
    see all unique words which exist in the email. Then the global HAM Dictionary Counter is updated for each
    value in the email.
    '''
    def readHamEmail(self,filePath):
        with open(filePath, 'r') as fp:
            words = self.parseEmail(fp)
            self.hamDict.update(words)
        fp.close()
    '''
    function: parseEmail
    Date: 9-11-2016
    Description: This is where all of the magic happens as far as parsing goes.
    '''
    def parseEmail(self,data):
        parser = Parser()
        email = parser.parse(data)
        word = email.as_string().strip('"').strip('"').split()
        s_word = set(word)
        c_word = []
        if self.wordMax is None or self.wordMin is None:
            self.wordMax = 15
            self.wordMin = 1
        for w in s_word:
            if len(w) <=self.wordMax and len(w) >= self.wordMin:
                printable = set(string.printable)
                w = w.strip("\n")
                w = filter(lambda x: x in printable, w)
                w = w.translate(None, string.punctuation)
                w = w.translate(None,string.digits)
                c_word.append(w)
            #removed set(c_word)
        s_word = c_word
        return s_word
    '''
    function: combineDictionaries
    Date: 9-9-2016
    Description: The Spam & Ham Counters are cast as dictionaries. Then the union of both dictionaries is iterated
    through and both values for each word are added to the dictionary. Then the intersection of both dictionaries
    is then added to the master dictionary.
    '''
    def combineDictionaries(self,sDict, hDict,filename1, filename2):
        nCounter = Counter()
        nCounter = sDict + hDict
        self.saveCounter('counter.txt',nCounter,hDict,sDict)
        spDict = dict(self.spamDict)
        haDict = dict(self.hamDict)
        master = {}
        keys = set(spDict.keys()) & set(haDict.keys())
        total = len(keys)
        count = 0
        print '-----------------------------------------------------------------------------------------'
        print 'Adding Emails To Dictionary: '
        for k in keys:
            master[str(k)] = ('ham',haDict[k],'spam',spDict[k])
            count = count + 1
            sys.stdout.write('\r')
            sys.stdout.write('%.2f%% Complete' % ( count / total * 100,))
            sys.stdout.flush()
        hKeys = set(keys).difference(hDict.keys())
        sKeys = set(keys).difference(sDict.keys())
        total = len(hKeys)
        count = 0
        for k in hKeys:
            master[str(k)] = ('ham',haDict[k],'spam',0)
            count = count + 1
            sys.stdout.write('\r')
            sys.stdout.write('%.2f%% Complete' % ( count / total * 100,))
            sys.stdout.flush()
        total = len(sKeys)
        count = 0
        for k in sKeys:
            master[str(k)] = ('ham',0,'spam',spDict[k])
            count = count + 1
            sys.stdout.write('\r')
            sys.stdout.write('%.2f%% Complete ' % ( count / total * 100,))
            sys.stdout.flush()
        print '\n-----------------------------------------------------------------------------------------'
        self.saveToTextfile(master,filename1,1,3)
        nDict = self.getProbabilities(master,1,3)
        self.saveToTextfile(nDict,filename2,0,1)

    '''
    function: getMostCommonWords
    Date: 9-14-2016
    Description: Get a List of N Most Common Words in both Spam & Ham Dictionary and write them to a file for use in training.
    '''
    def getMostCommonWords(self, spamDict, hamDict):
        filename1 = 'most_common.txt'
        filename2 = 'most_common_probs.txt'
        sDict = dict(spamDict)
        hDict = dict(hamDict)
        master = {}
        mCommonKeys = list(set(hDict.keys()) & set(sDict.keys()))
        for k in mCommonKeys:
            master[k] = (hDict[k], sDict[k])
        self.saveToTextfile(master,filename1,0,1)
        nDict = self.getProbabilities(master,0,1)
        self.saveToTextfile(nDict,filename2,0,1)
    '''
    function: getProbabilities
    Date: 9-11-2016
    Description: Converts the Count of Spam And Ham to Probabilities using P('word')/ SUM(SPAM) & P('word') /  SUM(HAM)
    or the Likelihoods of each word that its SPAM | HAM.
    '''
    def getProbabilities(self,data,val1,val2):
        dictionary = dict(data)
        spamSum = 0
        hamSum = 0
        nDict = {}
        for key, value in dictionary.items():
            hamSum = value[val1] + hamSum
            spamSum = value[val2] + spamSum
        for key, value in dictionary.items():
            hamProb = np.float()
            spamProb = np.float()
            if int(value[val1]) == 0:
                hamProb = np.divide(1,np.power(2,hamSum))
                spamProb = np.divide(np.float(value[val2]),spamSum)
                print 'Ham 0'
            elif int(value[val2]) == 0:
                hamProb = np.divide(np.float(value[val1]),hamSum)
                spamProb =  np.divide(1,np.power(2,spamSum))
                print 'Spam 0'
            else:
                hamProb = np.divide(np.float(value[val1]),hamSum)
                spamProb = np.divide(np.float(value[val2]),spamSum)
            nDict[key] = (hamProb, spamProb)
        return nDict

    '''
    function: saveToJSON
    Date: 9-9-2016
    Description: A File is saved to a JSON Text File after the training is completed.
    '''
    def saveToJSON(self,data,filename):
        dictionary = dict(data)
        filename = filename + ".json"
        with open(filename, 'w') as fp:
            json.dump(dictionary, fp, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
            print 'Training Completed! Please Review %s to see training data' % filename
    '''
    function: saveToTextfile
    Date: 9-12-2016
    Description: A File is saved to a JSON Text File after the training is completed.
    '''
    def saveToTextfile(self,data,filename,val1, val2):
        dictionary = dict(data)
        with open(filename,'wb') as f:
            w = csv.writer(f)
            for key,value in dictionary.items():
                w.writerow([key,value[val1],value[val2]])
        f.close()

    def saveCounter(self,filename,master, sDict, hDict):
        with open(filename,'wb') as f:
            w = csv.writer(f)
            for key in master.keys():
                w.writerow([key,hDict[key],sDict[key]])
        f.close()
    '''
    function: notify
    Date: 9-12-2016
    Description: Texts provided phone number when training is completed. Can be useful when training is longer than 5 minutes.
    '''
    def notify(self, number, message):
        command = "curl http://textbelt.com/text -d number=" + str(number) + ' -d message="' + str(message)+'"'
        print command
        os.system(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Spam Filter Training")
    parser.add_argument("-f","--file", dest="filename", help="The file to read data from", metavar="FILE",required=True)
    parser.add_argument("-k","--key",dest="keyFile",help="The Key file for training", metavar="FILE",required=True)
    parser.add_argument("-s","--save",dest="sFilename",help="The filename to save trainig to",metavar="FILE",required=False)
    parser.add_argument("-p","--phoneNumber",dest="phoneNumber",help="The phone Number to text when training is complete.", metavar="Phone",required=False)
    parser.add_argument("-o","--outputFile",dest="outFilename",help="The Name of the File For Outputting Taining To.")
    parser.add_argument("-min","--wordMin",dest="wordMin",help="Minimum Word Length For Training",metavar='INT',required=False)
    parser.add_argument("-max","--wordMax",dest="wordMax",help="Maximum Word Length For Training",metavar='INT',required=False)
    args = parser.parse_args()
    if args.wordMax != None and args.wordMin != None:
        ep = EmailParser(args.filename,args.keyFile,None,args.wordMin, args.wordMax)
    elif args.wordMax != None and args.wordMin != None and args.phoneNumber != None:
        ep = EmailParser(args.filename,args.keyFile,args.phoneNumber,args.wordMin,args.wordMax)
    elif args.phoneNumber != None:
        ep = EmailParser(args.filename,args.keyFile,args.phoneNumber,None,None)
    else:
        ep = EmailParser(args.filename,args.keyFile,None,None,None)
