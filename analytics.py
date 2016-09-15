#!/usr/bin/env python
#--------------------------------------------------------------------------------------------------------------------------
#@Author: Brandon Radosevich
#@Date: September 3, 2016
#@Class: New Mexico State University EE565/490
#@Project: Project 2
#Description: Analytics For The EmailParser, Classifier and Compute Performance
#--------------------------------------------------------------------------------------------------------------------------
#import statements
from __future__ import division
import re # for regular expression handling.
import argparse # for command line arguments
import json # for creating a json file.
import os # for texting after training is done.
import sys # for progress bar
from collections import Counter, defaultdict # for counting words
from timeit import default_timer as timer # for timing total execution speed.
import numpy as np # for the maths...
import matplotlib.pyplot as plt
#Libraries For This Assignment
from emailParser import EmailParser
from classify import classifyEmail
from computer_performance import ComputerPerformance as cp

'''
Description: This Class Performs Analytics on the Naive Bayesian Spam Filter Class
'''
class Analytics(object):
    def __init__ (self,filePath, keyFile,testFile1,testFile2):
        parser = EmailParser(filePath,keyFile,None,None,None)
        training = 'training_probs.txt'
        evals1 = classifyEmail(testFile1,None,training)
        evals2 = classifyEmail(testFile2,None,training)
        hDict = parser.hamDict
        sDict = parser.spamDict
        #print sDict.most_common(100)
        self.getAverage(evals1.analytics)
        self.getAverage(evals2.analytics)
        self.graphMostCommonWords(sDict.most_common(50),hDict.most_common(50))

    '''
    function: getAverage
    date: 9-14-2016
    Description: Gets the Mean of total number of words in each test email
    '''
    def getAverage(self,dataset):
        values = []
        for v in dataset:
            values.append(v[1])
        mean = np.mean(values)
        print 'Mean Value: ',mean

    '''
    function: graphMostCommonWords
    date: 9-15-2016
    Description: Graphs 50 most common words in both dictionaries.
    '''
    def graphMostCommonWords(self, sDict, hDict):
        values_h = []
        values_s = []
        words_s = []
        words_h = []
        for t in sDict:
            values_s.append(t[1])
            words_s.append(t[0])
        for t in hDict:
            values_h.append(t[1])
            words_h.append(t[0])
        width = 0.3
        indexes1 = np.arange(len(words_h))
        indexes2 = np.arange(len(words_s))
        plt.bar(indexes1,values_h)
        plt.bar(indexes2,values_s)
        plt.xticks(indexes1-0.2, words_h, rotation='vertical')
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Bayesian Spam Filter Analytics")
    parser.add_argument("-f","--file", dest="filename", help="The file to read data from", metavar="FILE",required=True)
    parser.add_argument("-k","--key",dest="keyFile",help="The Key file for training", metavar="FILE",required=True)
    parser.add_argument("-test1","--test1",dest="testFile1",help="The Test file for training", metavar="FILE",required=True)
    parser.add_argument("-test2","--test2",dest="testFile2",help="The Test file for training", metavar="FILE",required=True)
    parser.add_argument("-o","--outputFile",dest="GraphName",help="The filename to save the training to to",metavar="Graph",required=False)
    parser.add_argument("-p","--phoneNumber",dest="phoneNumber",help="The phone Number to text when training is complete.", metavar="Phone",required=False)
    args = parser.parse_args()
    analyze = Analytics(args.filename,args.keyFile,args.testFile1,args.testFile2)
