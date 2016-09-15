#!/usr/bin/env python
#--------------------------------------------------------------------------------------------------------------------------
#@Author: Brandon Radosevich
#@Date: September 3, 2016
#@Class: New Mexico State University EE565/490
#@Project: Project 2
#Description:
#Finds Overall Accuracy of Training File from Evaluation Stage
#--------------------------------------------------------------------------------------------------------------------------
#import statements
import argparse
import numpy as np # for math and stuff
from collections import Counter #magic
'''
Class: ComputerPerformance
Description: Finds Overall Accuracy of Bayesian Spam Filter
'''
class ComputerPerformance(object):

    def __init__(self,key,training,verbose):
        self.computeResults(key,training,verbose)

    '''
    function: computeResults
    date: 9-12-2016
    Description: This function Computes the Overall Accuracy of the Training.
    '''
    def computeResults(self,key,training,verbose):
        kData = [line.strip("\r\n") for line in open(key)]
        rData = [line.strip("\r\n") for line in open(training)]
        sKey = 0
        hKey = 0
        for l in kData:
            if str(l) == "ham":
                hKey = hKey + 1
            elif str(l) == "spam":
                sKey = sKey + 1
        totalK = len(kData)
        totalR = len(rData)
        #sResult = 0
        #hResult = 0
        k = kData
        r = rData
        hKeyCount = 0
        sKeyCount = 0
        sPred = 0
        hPred = 0
        dResult = 0
        if verbose:
            print "Key | Prediction"
        for i in range(0,totalK):
            if verbose:
                print kData[i], rData[i]
            if kData[i] == rData[i] and kData[i] == 'ham':
                hPred = hPred + 1
                dResult = dResult + 1
            elif kData[i] == rData[i] and kData[i] == 'spam':
                sPred = sPred +1
                dResult = dResult + 1
            else:
                if kData[i] == 'ham':
                    hKeyCount = hKeyCount + 1
                elif kData[i] == 'spam':
                    sKeyCount = sKeyCount + 1
        print 'dResult: ',dResult
        print 'Key: ',totalK
        print 'Probability: ', np.divide(dResult,np.float(totalK))
        hprob = np.divide(hPred,np.float(hKey))
        sprob = np.divide(sPred,np.float(sKey))
        s_prob = np.divide(sKey-sPred,np.float(sKey))
        h_prob = np.divide(hKey-hPred,np.float(hKey))
        print "-------------|-------------------------------------------------------|"
        print "|   Actual   |                    Predicted                          |"
        print "-------------|-------------------------------------------------------|"
        print "|            |           Ham          |             Spam             |"
        print "|    Ham     |      %d (%.2f%%)      |          %d (%.2f%%)          |"%(hPred,hprob,hKey-hPred,h_prob)
        print "|    Spam    |      %d (%.2f%%)        |          %d (%.2f%%)        |"%(sKey-sPred,s_prob,sPred,sprob)
        print "-------------|-------------------------------------------------------|"


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Spam Filter Training")
    parser.add_argument("-k","--key", dest="key", help="The file to read data from", metavar="FILE",required=True)
    parser.add_argument("-t","--training", dest="trainingResults", help="The file to read data from", metavar="FILE",required=True)
    parser.add_argument("-v","--verbose",dest="verbose",help="Verbose Mode For Evaluation.",action="store_true")
    parser.set_defaults(verbose=False)
    args = parser.parse_args()
    cp = ComputerPerformance(args.key,args.trainingResults,args.verbose)
