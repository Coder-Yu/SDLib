#coding:utf-8
#author:Yu Junliang
import random

import numpy as np
from ratingAttack import RatingAttack

from variables import *


class RandomAttack(RatingAttack):
    def __init__(self):
        super(RandomAttack, self).__init__()

    def insertSpam(self,attackRatio,fillerSize,selectedSize,targetCount):
        itemList = self.itemProfile.keys()
        userList = self.userProfile.keys()
        startUserID = len(self.userProfile)+1

        for i in range(int(len(self.userProfile)*attackRatio)):
            #fill 装填项目
            fillerItems = self.getFillerItems(fillerSize)
            for item in fillerItems:
                self.spamProfile[str(startUserID)][str(itemList[item])] = random.randint(1,6)

            #target 目标项目
            for j in range(targetCount):
                target = np.random.randint(len(self.targetItems))
                self.spamProfile[str(startUserID)][self.targetItems[target]] = maximumScore
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