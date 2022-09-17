#coding:utf-8
#author:Yu Junliang

import random

import numpy as np
from attack import Attack


class BandWagonAttack(Attack):
    def __init__(self,conf):
        super(BandWagonAttack, self).__init__(conf)
        self.hotItems = sorted(self.itemProfile.iteritems(), key=lambda d: len(d[1]), reverse=True)[
                   :int(self.selectedSize * len(self.itemProfile))]


    def insertSpam(self,startID=0):
        print 'Modeling bandwagon attack...'
        itemList = self.itemProfile.keys()
        if startID == 0:
            self.startUserID = len(self.userProfile)
        else:
            self.startUserID = startID

        for i in range(int(len(self.userProfile)*self.attackSize)):
            #fill 装填项目
            fillerItems = self.getFillerItems()
            for item in fillerItems:
                self.spamProfile[str(self.startUserID)][str(itemList[item])] = random.randint(self.minScore,self.maxScore)
            #selected 选择项目
            selectedItems = self.getSelectedItems()
            for item in selectedItems:
                self.spamProfile[str(self.startUserID)][item] = self.targetScore
            #target 目标项目
            for j in range(self.targetCount):
                target = np.random.randint(len(self.targetItems))
                self.spamProfile[str(self.startUserID)][self.targetItems[target]] = self.targetScore
                self.spamItem[str(self.startUserID)].append(self.targetItems[target])
            self.startUserID += 1

    def getFillerItems(self):
        mu = int(self.fillerSize*len(self.itemProfile))
        sigma = int(0.1*mu)
        markedItemsCount = int(round(random.gauss(mu, sigma)))
        if markedItemsCount < 0:
            markedItemsCount = 0
        markedItems = random.sample(range(len(self.itemProfile)), markedItemsCount)
        return markedItems

    def getSelectedItems(self):

        mu = int(self.selectedSize * len(self.itemProfile))
        sigma = int(0.1 * mu)
        markedItemsCount = abs(int(round(random.gauss(mu, sigma))))
        markedIndexes = random.sample(range(len(self.hotItems)), markedItemsCount)
        markedItems = [self.hotItems[index][0] for index in markedIndexes]
        return markedItems
