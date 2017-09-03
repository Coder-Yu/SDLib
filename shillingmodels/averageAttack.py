#coding:utf-8
#author:Yu Junliang
#Date: 2016-03-15
import random

import numpy as np
from attack import Attack


class AverageAttack(Attack):
    def __init__(self,conf):
        super(AverageAttack, self).__init__(conf)


    def insertSpam(self,startID=0):
        print 'Modeling average attack...'
        itemList = self.itemProfile.keys()
        if startID == 0:
            self.startUserID = len(self.userProfile)
        else:
            self.startUserID = startID

        for i in range(int(len(self.userProfile)*self.attackSize)):
            #fill 装填项目
            fillerItems = self.getFillerItems()
            for item in fillerItems:
                self.spamProfile[str(self.startUserID)][str(itemList[item])] = round(self.itemAverage[str(itemList[item])])
            #target 目标项目
            for j in range(self.targetCount):
                target = np.random.randint(len(self.targetItems))
                self.spamProfile[str(self.startUserID)][self.targetItems[target]] = self.targetScore
                self.spamItem[str(self.startUserID)].append(self.targetItems[target])
            self.startUserID += 1






