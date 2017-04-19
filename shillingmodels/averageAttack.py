#coding:utf-8
#author:Yu Junliang
#Date: 2016-03-15
import random

import numpy as np
from ratingAttack import RatingAttack


class AverageAttack(RatingAttack):
    def __init__(self):
        super(AverageAttack, self).__init__()



    def insertSpam(self,attackRatio,fillerSize,selectedSize,targetCount,targetScore):
        itemList = self.itemProfile.keys()
        userList = self.userProfile.keys()
        startUserID = len(self.userProfile)+1

        for i in range(int(len(self.userProfile)*attackRatio)):
            #fill 装填项目
            fillerItems = self.getFillerItems(fillerSize)
            for item in fillerItems:
                self.spamProfile[str(startUserID)][str(itemList[item])] = round(self.itemAverage[str(itemList[item])])
            #target 目标项目
            for j in range(targetCount):
                target = np.random.randint(len(self.targetItems))
                self.spamProfile[str(startUserID)][self.targetItems[target]] = targetScore
                self.spamItem[str(startUserID)].append(self.targetItems[target])
            startUserID += 1

    def getFillerItems(self,fillerSize):
        mu = int(fillerSize*len(self.itemProfile))
        sigma = int(0.1*mu)
        markedItemsCount = abs(int(round(random.gauss(mu, sigma))))
        markedItems = np.random.randint(len(self.itemProfile), size=markedItemsCount)
        return markedItems.tolist()





