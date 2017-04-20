from collections import defaultdict
import numpy as np
from tool.config import Config
from tool.file import FileIO
import random
import os
from os.path import abspath
class Attack(object):
    def __init__(self,conf):
        self.config = Config(conf)
        self.userProfile = FileIO.loadDataSet(self.config,self.config['ratings'])
        self.itemProfile = defaultdict(dict)
        self.attackSize = float(self.config['attackSize'])
        self.fillerSize = float(self.config['fillerSize'])
        self.selectedSize = float(self.config['selectedSize'])
        self.targetCount = int(self.config['targetCount'])
        self.targetScore = float(self.config['targetScore'])
        self.threshold = float(self.config['threshold'])
        self.minCount = int(self.config['minCount'])
        self.maxCount = int(self.config['maxCount'])
        self.outputDir = self.config['outputDir']
        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)
        for user in self.userProfile:
            for item in self.userProfile[user]:
                self.itemProfile[item][user] = self.userProfile[user][item]
        self.spamProfile = defaultdict(dict)
        self.spamItem = defaultdict(list) #items rated by spammers
        self.targetItems = []
        self.itemAverage = {}
        self.getAverageRating()
        self.selectTarget()

    # def selectTarget(count = 20):
    #     pass
    # def reload(self):
    #     self.userProfile, self.itemProfile = loadRatings(self.config['ratings'])
    #     self.spamProfile = defaultdict(dict)
    #     self.spamItem = defaultdict(list)

    def getAverageRating(self):
        for itemID in self.itemProfile:
            li = self.itemProfile[itemID].values()
            self.itemAverage[itemID] = float(sum(li)) / len(li)


    def selectTarget(self,):
        print 'Selecting target items...'
        print '-'*80
        print 'Target item       Average rating of the item'
        itemList = self.itemProfile.keys()
        itemList.sort()
        while len(self.targetItems) < self.targetCount:
            target = np.random.randint(len(itemList)) #generate a target order at random

            if len(self.itemProfile[str(itemList[target])]) < self.maxCount and len(self.itemProfile[str(itemList[target])]) > self.minCount \
                    and str(itemList[target]) not in self.targetItems \
                    and self.itemAverage[str(itemList[target])] <= self.threshold:
                self.targetItems.append(str(itemList[target]))
                print str(itemList[target]),'                  ',self.itemAverage[str(itemList[target])]

    def getFillerItems(self):
        mu = int(self.fillerSize*len(self.itemProfile))
        sigma = int(0.1*mu)
        markedItemsCount = abs(int(round(random.gauss(mu, sigma))))
        markedItems = np.random.randint(len(self.itemProfile), size=markedItemsCount)
        return markedItems.tolist()

    def insertSpam(self):
        pass

    def loadTarget(self,filename):
        with open(filename) as f:
            for line in f:
                self.targetItems.append(line.strip())

    def generateLabels(self,filename):
        labels = []
        path = self.outputDir + filename
        with open(path,'w') as f:
            for user in self.spamProfile:
                labels.append(user+' 1\n')
            for user in self.userProfile:
                labels.append(user+' 0\n')
            f.writelines(labels)
        print 'User profiles have been output to '+abspath(self.config['outputDir'])+'.'

    def generateProfiles(self,filename):
        ratings = []
        path = self.outputDir+filename
        with open(path, 'w') as f:
            for user in self.userProfile:
                for item in self.userProfile[user]:
                    ratings.append(user+' '+item+' '+str(self.userProfile[user][item])+'\n')

            for user in self.spamProfile:
                for item in self.spamProfile[user]:
                    ratings.append(user + ' ' + item + ' ' + str(self.spamProfile[user][item])+'\n')
            f.writelines(ratings)
        print 'User labels have been output to '+abspath(self.config['outputDir'])+'.'

