#coding:utf-8
#author:Yu Junliang

import random

import numpy as np
from ratingAttack import RatingAttack

from variables import *
class BandWagonAttack(RatingAttack):
    def __init__(self,selectedSize):
        super(BandWagonAttack, self).__init__()
        self.hotItems = sorted(self.itemProfile.iteritems(), key=lambda d: len(d[1]), reverse=True)[
                   :int(selectedSize * len(self.itemProfile))]

    def insertSpam(self,attackRatio,fillerSize,selectedSize,targetCount,targetScore):
        itemList = self.itemProfile.keys()
        userList = self.userProfile.keys()
        startUserID = len(self.userProfile)+1

        for i in range(int(len(self.userProfile)*attackRatio)):
            #fill 装填项目
            fillerItems = self.getFillerItems(fillerSize)
            for item in fillerItems:
                self.spamProfile[str(startUserID)][str(itemList[item])] = random.randint(1,6)
            #selected 选择项目
            selectedItems = self.getSelectedItems(selectedSize)
            for item in selectedItems:
                self.spamProfile[str(startUserID)][item] = targetScore
            #target 目标项目
            for j in range(targetCount):
                target = np.random.randint(len(self.targetItems))
                self.spamProfile[str(startUserID)][self.targetItems[target]] = targetScore
                self.spamItem[str(startUserID)].append(self.targetItems[target])
            startUserID += 1

    def getFillerItems(self,fillerSize):
        mu = int(fillerSize*len(self.itemProfile))
        sigma = int(0.1*mu)
        markedItemsCount = int(round(random.gauss(mu, sigma)))
        if markedItemsCount < 0:
            markedItemsCount = 0
        markedItems = np.random.randint(len(self.itemProfile), size=markedItemsCount)
        return markedItems

    def getSelectedItems(self,selectedSize):

        mu = int(selectedSize * len(self.itemProfile))
        sigma = int(0.1 * mu)
        markedItemsCount = abs(int(round(random.gauss(mu, sigma))))
        markedIndexes =  np.random.randint(len(self.hotItems), size=markedItemsCount)
        markedItems = [self.hotItems[index][0] for index in markedIndexes]
        return markedItems