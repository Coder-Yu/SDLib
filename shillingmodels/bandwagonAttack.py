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


    def insertSpam(self):
        print 'Modeling bandwagon attack...'
        itemList = self.itemProfile.keys()
        startUserID = len(self.userProfile)+1

        for i in range(int(len(self.userProfile)*self.attackSize)):
            #fill 装填项目
            fillerItems = self.getFillerItems()
            for item in fillerItems:
                self.spamProfile[str(startUserID)][str(itemList[item])] = random.randint(1,6)
            #selected 选择项目
            selectedItems = self.getSelectedItems()
            for item in selectedItems:
                self.spamProfile[str(startUserID)][item] = self.targetScore
            #target 目标项目
            for j in range(self.targetCount):
                target = np.random.randint(len(self.targetItems))
                self.spamProfile[str(startUserID)][self.targetItems[target]] = self.targetScore
                self.spamItem[str(startUserID)].append(self.targetItems[target])
            startUserID += 1

    def getFillerItems(self):
        mu = int(self.fillerSize*len(self.itemProfile))
        sigma = int(0.1*mu)
        markedItemsCount = int(round(random.gauss(mu, sigma)))
        if markedItemsCount < 0:
            markedItemsCount = 0
        markedItems = np.random.randint(len(self.itemProfile), size=markedItemsCount)
        return markedItems

    def getSelectedItems(self):

        mu = int(self.selectedSize * len(self.itemProfile))
        sigma = int(0.1 * mu)
        markedItemsCount = abs(int(round(random.gauss(mu, sigma))))
        markedIndexes =  np.random.randint(len(self.hotItems), size=markedItemsCount)
        markedItems = [self.hotItems[index][0] for index in markedIndexes]
        return markedItems