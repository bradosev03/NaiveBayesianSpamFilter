#!/usr/bin/env python
#--------------------------------------------------------------------------------------------------------------------------
#@Author: Brandon Radosevich
#@Date: September 5, 2016
#@Class: New Mexico State University EE565/490
#@Project: Project 2
#Description:
# Evaluating Overall Training Of Naive Bayesian Spam Filter
#--------------------------------------------------------------------------------------------------------------------------
#import statements
from __future__ import division # for printing out progress
import argparse # for arguments
from collections import Counter # magic
import sys # for printing out progress bar
import csv #for reading in file
import numpy as np # For finding probability
from email.parser import Parser # for parsin email
import string # for regex
'''
class: classifyEmail
Description: This class is used for evaluating the overall training of the code
'''
class classifyEmail(object):

    def __init__(self,inputFile,trainingFile,probs,verbose):
        print "[+] Beginning Testing:"
        print '------------------------------------------'
        self.verbose = verbose
        self.analytics = []
        self.loadEmails(inputFile,trainingFile,probs)

    '''
    function: createProbabilities
    Date: 9-14-2016
    Description: This Function Creates the Likelihoods, given a text file with word,hCount,sCount
    '''
    def createProbabilities(self,trainingFile):
        reader = csv.reader(open(trainingFile,'r'))
        spamSum = 0
        hamSum = 0
        nDict = {}
        d = {}
        for row in reader:
            k,h,s = row
            d[k] = (int(h),int(s))
        for key,value in d.items():
            hamSum = value[0] + hamSum
            spamSum = value[1] + spamSum
        if self.verbose:
            print 'Ham Sum: ',hamSum
            print 'Spam Sum: ', spamSum

        for key, value in d.items():
            hamProb = np.float()
            spamProb = np.float()
            if value[0] == 0:
               hamProb = np.divide(np.exp(1*1.2),hamSum)
               spamProb = np.divide(value[1],spamSum)
            if value[1] == 0:
               hamProb = np.divide(np.float(value[0]),hamSum)
               spamProb =  np.divide(np.exp(1*1.2),spamSum)
            else:
                hamProb = np.divide(np.float(value[0]),hamSum)
                spamProb = np.divide(np.float(value[1]),spamSum)
                nDict[key] = (hamProb, spamProb)
        return nDict

    '''
    @function: loadTrainingFile
    @Date: 9-12-2016
    @Description: This Function loads the training from the likelihoods
    '''
    def loadTrainingFile(self,probs):
        reader = csv.reader(open(probs,'r'))
        d = {} # dictionary for trainingFile
        for row in reader:
            k,h,s = row
            d[k] = (h,s)
        return d
    '''
    @function: loadEmails
    @Date: 9-12-2016
    @Description: This functions loads the evaluation emails from the provided file
    '''
    def loadEmails(self,inputFile, trainingFile, probs):
        training = {}
        if trainingFile is None:
            training = self.loadTrainingFile(probs)
        elif probs is None:
            training = self.createProbabilities(trainingFile)
        folder = "trec05p-1/"
        emails = [line.strip("\r\n") for line in open(inputFile)]
        total = len(emails)
        count = 0
        results = []
        for e in emails:
            counter = self.countOccurrence(folder + str(e))
            ham, spam = self.lookupTraining(counter,training)
            val = self.findProbability(ham,spam)
            results.append(val)
            count = count + 1
            sys.stdout.write('\r')
            sys.stdout.write('%.2f%% Complete' % ( count / total * 100,))
            sys.stdout.flush()
        #TODO: add flag for name of outputFile
        print '\n------------------------------------------'
        self.saveToTextfile(results,'results.txt')

    '''
    @function: countOccurrence
    @Date: 9-12-2016
    @Description:
    '''
    def countOccurrence(self,filePath):
        counter = Counter()
        with open(filePath, 'r') as fp:
            words = self.parseEmail(fp)
            counter.update(words)
        fp.close()
        return counter
    '''
    function: parseEmail
    date: 9-14-2016
    Description: Parses Emails based on the predetermined characterists of emails.
    '''
    def parseEmail(self,data):
        parser = Parser()
        email = parser.parse(data)
        word = email.as_string().strip('"').strip('"').split()
        s_word = set(word)
        c_word = []
        for w in s_word:
            if len(w) < 15 and len (w) >= 1:
                w = w.translate(None, string.punctuation)
                w = w.translate(None,string.digits)
                c_word.append(w)
        s_word = c_word#set(c_word)
        return s_word
    '''
    @function: countOccurrence
    @Date: 9-12-2016
    @Description: This function gets the training results from a given text file
    '''
    def lookupTraining(self,dictionary,training):
        dic = dict(dictionary)
        spam = [] # array for spam Probability
        ham = [] # array for ham Probability
        count = 0
        for key,value in dic.items():
            if key in training:
                ham.append(training[key][0])
                spam.append(training[key][1])
                count= count + 1
        if self.verbose:
            print '\tMatched %d Words'% (count,)
        self.analytics.append((key, count))
        return (ham,spam)
    '''
    @function: findProbability
    @Date: 9-12-2016
    @Description:
                                likelihood             posterior       prior
        Bayes Theorem: p(X = 'cash' | Y = ham) = p(X=cash | Y = ham) p( Y = ham)
                                                 --------------------------------
                                                            P(X = cash)
                                                           normalization
    '''
    def findProbability(self,ham, spam):
        pSpam = -1000
        pHam = -1000
        sPrior = 0.50
        hPrior = 0.50
        for h,s in zip(ham,spam):
            #norm = np.add(np.multiply(np.float(s),np.float(sPrior)),np.multiply(np.float(h),np.float(hPrior)))
            s_temp = np.add(np.log(np.float(s)),np.log(np.float(sPrior)))
            h_temp = np.add(np.log(np.float(h)),np.log(np.float(hPrior)))
            pSpam = pSpam + s_temp
            pHam = pHam + h_temp

        if pSpam > pHam:
            return "spam"
        else:
            return "ham"

    '''
    function: saveToTextfile
    date: 9-8-2016
    description: Writes output to text file
    '''
    def saveToTextfile(self,data,filename):
        with open(filename,'wb') as f:
            for d in data:
                f.write(d+"\n")
        print "Testing Completed, Please Review %s For results."% (filename,)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Spam Filter Classification System")
    parser.add_argument("-f","--file", dest="filename", help="The file to read data from", metavar="FILE",required=True)
    parser.add_argument("-t","--training", dest="trainingFile", help="The file to read data from", metavar="FILE",required=False)
    parser.add_argument("-p","--probabilities",dest='probs',help="The Training File as Probabilities",metavar="FILE",required=False)
    parser.add_argument("-v","--verbose",dest="verbose",help="Verbose Mode For Evaluation.",action="store_true")
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    if (args.trainingFile is None and args.probs is None):
        print 'Must Provide A Training File Using -t or -p\n'
        exit(0)
    elif args.trainingFile is None:
        ce = classifyEmail(args.filename,None,args.probs,args.verbose)
    elif args.probs is None:
        ce = classifyEmail(args.filename,args.trainingFile,None,args.verbose)
